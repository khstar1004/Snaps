import requests
from typing import List, Dict, Any
import random
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.schema import Document
from typing import List, Dict, Any, Optional
import os
import time
from datetime import datetime, timedelta
from requests.exceptions import RequestException
import logging
from bson.objectid import ObjectId


load_dotenv()
logger = logging.getLogger(__name__)

class InstagramAPI:
    BASE_URL = "https://graph.instagram.com/v12.0"

    def __init__(self, user_id: Optional[str] = None, mongo_client: Optional[Any] = None):
        self.user_id = user_id
        self.mongo_client = mongo_client
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self.last_request_time = 0
        self.min_request_interval = 1

        if user_id and mongo_client:
            self.db = self.mongo_client.get_database('snaps_db')
            self.users_collection = self.db.users
            user = self.users_collection.find_one({"_id": ObjectId(self.user_id)})
            if user:
                self._access_token = user.get('access_token')
                self._token_expiry = user.get('token_expiry')
        else:
            self._access_token = self.get_valid_instagram_token()

    @property
    def access_token(self):
        if not self._access_token:
            user = self.users_collection.find_one({"_id": ObjectId(self.user_id)})
            self._access_token = user.get('access_token')
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value

    @staticmethod
    def get_valid_instagram_token():
        token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        if not token:
            raise ValueError("INSTAGRAM_ACCESS_TOKEN not found in .env file")
        return token

    def get_user_media(self, limit: int = 10) -> List[Dict[str, Any]]:
        endpoint = f"{self.BASE_URL}/me/media"
        params = {
            "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp",
            "access_token": self.access_token,
            "limit": limit
        }
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.RequestException as e:
            logging.error(f"Error fetching user media: {str(e)}")
            return []

    def format_posts(self, media_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        formatted_posts = []
        for item in media_items:
            media_urls = []
            if item.get("media_type") == "CAROUSEL_ALBUM" and "children" in item:
                for child in item["children"]["data"]:
                    media_url = child.get("media_url") or child.get("thumbnail_url")
                    if media_url:
                        media_urls.append(self.ensure_https(media_url))
            else:
                media_url = item.get("media_url") or item.get("thumbnail_url")
                if media_url:
                    media_urls.append(self.ensure_https(media_url))

            formatted_post = {
                "id": item.get("id"),
                "media_urls": media_urls,
                "caption": item.get("caption", "No caption"),
                "media_type": item.get("media_type"),
                "permalink": item.get("permalink"),
                "timestamp": item.get("timestamp")
            }
            formatted_posts.append(formatted_post)
        return formatted_posts

    @staticmethod
    def ensure_https(url: str) -> str:
        if url and not url.startswith(('http://', 'https://')):
            return f"https://{url}"
        return url
    
    def get_user_statistics(self, limit: int = 30) -> Dict[str, Any]:
        media_items = self.get_user_media(limit)
        
        post_types = {'IMAGE': 0, 'VIDEO': 0, 'CAROUSEL_ALBUM': 0}
        hashtags = {}
        posting_hours = {i: 0 for i in range(24)}

        for item in media_items:
            post_types[item.get('media_type', 'IMAGE')] += 1
            
            caption = item.get('caption', '')
            if caption:
                for tag in caption.split('#')[1:]:
                    tag = tag.strip().lower()
                    hashtags[tag] = hashtags.get(tag, 0) + 1
            
            timestamp = item.get('timestamp')
            if timestamp:
                hour = int(timestamp.split('T')[1].split(':')[0])
                posting_hours[hour] += 1

        popular_hashtags = sorted(hashtags.items(), key=lambda x: x[1], reverse=True)[:5]
        peak_posting_hours = sorted(posting_hours.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'total_posts': len(media_items),
            'post_types': post_types,
            'popular_hashtags': popular_hashtags,
            'peak_posting_hours': peak_posting_hours
        }

class ThreadAPI:
    BASE_URL = "https://graph.threads.net/v1.0"

    def __init__(self):
        self.access_token = os.getenv('THREAD_ACCESS_TOKEN')
        if not self.access_token:
            raise ValueError("THREAD_ACCESS_TOKEN not found in .env file")

    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}
        params['access_token'] = self.access_token

        print(f"Making request to: {url}")
        print(f"With params: {params}")
        print(f"With data: {data}")

        try:
            response = requests.request(method, url, params=params, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            if response.text:
                print(f"Response content: {response.text}")
            raise


    def post_thread(self, user_id: str, content: str, media_type: str = "TEXT", image_url: str = None, video_url: str = None) -> Dict[str, Any]:
        creation_params = {
            "media_type": media_type,
            "text": content
        }

        if media_type == "IMAGE" and image_url:
            creation_params["image_url"] = image_url
        elif media_type == "VIDEO" and video_url:
            creation_params["video_url"] = video_url

        creation_data = self._make_request("POST", f"{user_id}/threads", data=creation_params)
        
        if "id" not in creation_data:
            raise Exception(f"Failed to create media container: {creation_data}")

        creation_id = creation_data["id"]

        publish_data = self._make_request("POST", f"{user_id}/threads_publish", data={"creation_id": creation_id})

        if "id" not in publish_data:
            raise Exception(f"Failed to publish thread: {publish_data}")

        return publish_data

    def get_user_threads(self, user_id: str = None, since: str = None, until: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        user_id = user_id or self.default_user_id
        if not user_id:
            raise ValueError("User ID is required")

        params = {
            "fields": "id,media_product_type,media_type,media_url,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post",
            "limit": limit
        }
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        response = self._make_request("GET", f"{user_id}/threads", params=params)
        return response.get("data", [])

    def get_thread(self, thread_id: str) -> Dict[str, Any]:
        params = {
            "fields": "id,media_product_type,media_type,media_url,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post"
        }
        return self._make_request("GET", thread_id, params=params)

    def get_thread_insights(self, thread_id: str) -> Dict[str, Any]:
        params = {
            "metric": "views,likes,replies,reposts,quotes"
        }
        return self._make_request("GET", f"{thread_id}/insights", params=params)

    def get_user_insights(self, user_id: str = None, since: int = None, until: int = None) -> Dict[str, Any]:
        user_id = user_id or self.default_user_id
        if not user_id:
            raise ValueError("User ID is required")

        params = {
            "metric": "views,likes,replies,reposts,quotes,followers_count"
        }
        if since and until:
            params["since"] = since
            params["until"] = until
        return self._make_request("GET", f"{user_id}/threads_insights", params=params)
    

def convert_post(caption: str, target_platform: str, has_image: bool) -> str:
    converted_post = caption

    if target_platform == "Twitter":
        converted_post = f"Check out my latest Instagram post! 📸\n\n{caption[:200]}..." if len(caption) > 200 else caption
        converted_post += "\n\n#Instagram #Social"
    elif target_platform == "LinkedIn":
        converted_post = f"I just shared a new post on Instagram! Here's a sneak peek:\n\n{caption}\n\nFollow me on Instagram for more updates!"
        converted_post += "\n\n#SocialMedia #Professional #Instagram"
    elif target_platform == "Facebook":
        converted_post = f"New Instagram Post Alert! 🚨\n\n{caption}\n\nHead over to my Instagram profile to see the full post and more content!"
    elif target_platform == "Thread":
        converted_post = f"Continuing from my recent Instagram post...\n\n{caption[:100]}...\n\nThoughts?"
    elif target_platform == "YouTube Community":
        converted_post = f"📸 Instagram Update 📸\n\n{caption[:150]}...\n\nCheck out my Instagram for the full post and more behind-the-scenes content!"

    if has_image:
        converted_post += "\n\n[Image from Instagram]"

    return converted_post

class RAGConverter:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="chatgpt-4o-latest",
            openai_api_key=openai_api_key
        )
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

    def create_vector_store(self, text: str):
        document = Document(page_content=text)
        texts = self.text_splitter.split_documents([document])
        return Chroma.from_documents(texts, self.embeddings)

    def generate_enhanced_post(self, original_post: str, target_platform: str, has_image: bool) -> str:
        vector_store = self.create_vector_store(original_post)
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever()
        )

        prompt_template = """
        You are a social media expert. Your task is to convert an Instagram post to a {target_platform} post.
        Use the following rules:
        1. Maintain the core message and tone of the original post.
        2. Adapt the content to fit the style and conventions of {target_platform}.
        3. Include relevant hashtags for {target_platform}.
        4. Keep the post within the character limit of {target_platform} if applicable.
        5. If the original post has an image, mention it in the converted post.
        
        answer in korean

        Original Instagram post: {original_post}
        Has image: {has_image}

        Convert this post for {target_platform}:
        """

        prompt = PromptTemplate(
            input_variables=["target_platform", "original_post", "has_image"],
            template=prompt_template
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)

        enhanced_post = chain.run(
            target_platform=target_platform,
            original_post=original_post,
            has_image=has_image
        )

        return enhanced_post

def main():
    try:
        # Initialize Instagram API
        instagram_api = InstagramAPI()

        # Fetch recent Instagram posts
        media_items = instagram_api.get_user_media(limit=5)
        formatted_posts = instagram_api.format_posts(media_items)

        print(f"Total posts fetched: {len(formatted_posts)}")
        for i, post in enumerate(formatted_posts, 1):
            print(f"\nPost {i}:")
            print(f"ID: {post['id']}")
            print(f"Type: {post['media_type']}")
            print(f"Caption: {post['caption'][:50]}..." if len(post['caption']) > 50 else f"Caption: {post['caption']}")
            print(f"Media URLs: {', '.join(post['media_urls'])}")
            print(f"Permalink: {post['permalink']}")
            print(f"Timestamp: {post['timestamp']}")

        # Instagram 통계 가져오기
        instagram_stats = instagram_api.get_user_statistics()
        print("\nInstagram Statistics:")
        print(f"Total Posts: {instagram_stats['total_posts']}")
        print(f"Post Types: {instagram_stats['post_types']}")
        print("Popular Hashtags:")
        for tag, count in instagram_stats['popular_hashtags']:
            print(f"  #{tag}: {count}")
        print("Peak Posting Hours:")
        for hour, count in instagram_stats['peak_posting_hours']:
            print(f"  {hour}:00 - {count} posts")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()