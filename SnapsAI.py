import requests
from typing import List, Dict, Any
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
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

    def __init__(self, access_token=None):
        self.access_token = access_token

    def set_access_token(self, access_token):
        """액세스 토큰을 설정하는 메서드"""
        self.access_token = access_token

    def get_user_media(self, limit: int = 10) -> List[Dict[str, Any]]:
        """사용자의 Instagram 미디어를 가져옵니다."""
        if not self.access_token:
            raise ValueError("Access token is not set")
            
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
            print(f"Error fetching user media: {str(e)}")
            return []

    def format_posts(self, media_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """API 응답을 보기 좋게 포맷팅합니다."""
        formatted_posts = []
        for item in media_items:
            formatted_post = {
                "id": item.get("id"),
                "media_url": item.get("media_url") or item.get("thumbnail_url"),
                "caption": item.get("caption", "No caption"),
                "media_type": item.get("media_type"),
                "permalink": item.get("permalink"),
                "timestamp": item.get("timestamp")
            }
            formatted_posts.append(formatted_post)
        return formatted_posts

    def authenticate(self, code: str) -> Dict[str, str]:
        """Instagram OAuth 인증 코드로 액세스 토큰을 획득합니다."""
        token_url = "https://api.instagram.com/oauth/access_token"
        data = {
            "client_id": os.getenv("INSTAGRAM_CLIENT_ID"),
            "client_secret": os.getenv("INSTAGRAM_CLIENT_SECRET"),
            "grant_type": "authorization_code",
            "redirect_uri": os.getenv("INSTAGRAM_REDIRECT_URI"),
            "code": code
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to authenticate: {str(e)}")

class ThreadAPI:
    def __init__(self):
        self.base_url = "https://graph.threads.net/v1.0"
        self.access_token = None

    def get_user_media(self, user_id):
        """사용자의 모든 Thread 게시물 조회"""
        try:
            endpoint = f"{self.base_url}/{user_id}/threads"
            params = {
                'fields': 'id,media_product_type,media_type,media_url,permalink,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post',
                'access_token': self.access_token
            }
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            # 각 게시물의 미디어 정보 처리
            posts = data.get('data', [])
            for post in posts:
                if post.get('media_type') in ['IMAGE', 'VIDEO', 'CAROUSEL_ALBUM']:
                    # 비디오인 경우 썸네일 URL 추가
                    if post.get('media_type') == 'VIDEO' and post.get('thumbnail_url'):
                        post['media_preview'] = post['thumbnail_url']
                    
                    # 캐러셀인 경우 모든 미디어 URL 수집
                    if post.get('media_type') == 'CAROUSEL_ALBUM' and post.get('children'):
                        post['carousel_media'] = [child.get('media_url') for child in post['children']['data']]

            return data
        except Exception as e:
            logger.error(f"Error fetching Thread media: {str(e)}")
            return {'data': []}

    def get_media_insights(self, media_id):
        """특정 Thread 게시물의 인사이트 조회"""
        endpoint = f"{self.base_url}/{media_id}/insights"
        params = {
            'metric': 'views,likes,replies,reposts,quotes,shares',
            'access_token': self.access_token
        }
        response = requests.get(endpoint, params=params)
        return response.json()

    def get_user_insights(self, user_id):
        """사용자의 Thread 계정 인사이트 조회"""
        try:
            endpoint = f"{self.base_url}/{user_id}/threads_insights"
            params = {
                'metric': 'views,likes,replies,reposts,quotes,followers_count',
                'period': 'day',  # 일별 데이터 요청
                'access_token': self.access_token
            }
            response = requests.get(endpoint, params=params)
            response_data = response.json()
            
            # 기본 통계 데이터 구조 초기화
            stats = {
                'total_posts': 0,
                'total_likes': 0,
                'total_replies': 0,
                'avg_likes': 0,
                'avg_replies': 0,
                'dates': [],
                'likes_data': [],
                'replies_data': []
            }

            # 게시물 수 조회
            posts_response = self.get_user_media(user_id)
            stats['total_posts'] = len(posts_response.get('data', []))

            # 최근 30일 데이터 생성
            current_date = datetime.now()
            for i in range(30):
                date = (current_date - timedelta(days=i)).strftime('%Y-%m-%d')
                stats['dates'].insert(0, date)
                stats['likes_data'].insert(0, random.randint(10, 100))  # 임시 데이터
                stats['replies_data'].insert(0, random.randint(5, 50))  # 임시 데이터

            # 총계 및 평균 계산
            stats['total_likes'] = sum(stats['likes_data'])
            stats['total_replies'] = sum(stats['replies_data'])
            stats['avg_likes'] = round(stats['total_likes'] / len(stats['likes_data']))
            stats['avg_replies'] = round(stats['total_replies'] / len(stats['replies_data']))

            return stats
        except Exception as e:
            logger.error(f"Error fetching Thread insights: {str(e)}")
            return {
                'total_posts': 0,
                'total_likes': 0,
                'total_replies': 0,
                'avg_likes': 0,
                'avg_replies': 0,
                'dates': [],
                'likes_data': [],
                'replies_data': []
            }

    def post_thread(self, user_id, content, media_type='TEXT', media_url=None):
        """Thread 게시물 작성"""
        endpoint = f"{self.base_url}/{user_id}/threads"
        data = {
            'text': content,
            'media_type': media_type,
            'access_token': self.access_token
        }
        
        if media_url:
            data['media_url'] = media_url
            
        response = requests.post(endpoint, json=data)
        return response.json()

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
            model_name="gpt-4o-mini",
            openai_api_key=openai_api_key
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

    def create_vector_store(self, text: str):
        document = Document(page_content=text)
        texts = self.text_splitter.split_documents([document])
        return Chroma.from_documents(texts, self.embeddings)

    def generate_enhanced_post(self, original_post: str, target_platform: str, has_image: bool) -> str:
        prompt = PromptTemplate(
            input_variables=["target_platform", "original_post", "has_image"],
            template="""
            당신은 소셜 미디어 마케팅 전문가입니다. 주어진 콘텐츠를 {target_platform}의 특성에 맞게 변환해주세요.
            
            각 플랫폼별 특성과 변환 규칙:
            - Instagram: 
              * 감성적이고 시각적인 표현
              * 해시태그 적극 활용 (5-10개)
              * 이모지 자연스럽게 사용
              * 짧은 단락으로 구성
            
            - Facebook: 
              * 상세하고 친근한 톤
              * 이야기하듯이 서술
              * 이모지 적절히 활용
              * 공감을 유도하는 질문 포함
            
            - Thread: 
              * 간결하면서도 대화를 유도
              * 위트있는 표현 사용
              * 해시태그 2-3개만 사용
              * 대화형 마무리
            
            - 네이버 블로그:
              * 정보성 콘텐츠 강화
              * 명확한 단락 구분
              * 키워드 강조
              * SEO를 위한 태그 활용
              * 목차형 구성 권장
            
            Original post: {original_post}
            Has image: {has_image}
            Target platform: {target_platform}
            
            변환된 콘텐츠만 출력하세요.
            """
        )

        result = self.llm.invoke(prompt.format(
            target_platform=target_platform,
            original_post=original_post,
            has_image=has_image
        ))

        return result.content.strip()

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