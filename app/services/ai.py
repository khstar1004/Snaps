from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from typing import Dict, Any, Optional
import json
import os
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7
        )
        self.embeddings = OpenAIEmbeddings()
        self.knowledge_base = self._create_knowledge_base()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=2000
        )

    def _create_knowledge_base(self) -> FAISS:
        """플랫폼별 지식 베이스 생성"""
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            kb_path = os.path.join(base_path, 'utils', 'data', 'rag_data', 'social_media_guidelines.json')
            
            with open(kb_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            texts = []
            for platform in data['platforms']:
                platform_name = platform['platform']
                for guideline in platform['guidelines']:
                    text = f"Platform: {platform_name}\n"
                    text += f"Category: {guideline['category']}\n"
                    text += f"Description: {guideline['description']}\n"
                    text += "Best Practices:\n"
                    for practice in guideline['best_practices']:
                        text += f"- {practice}\n"
                    texts.append(text)
            
            return FAISS.from_texts(
                texts,
                self.embeddings
            )
        except Exception as e:
            logger.error(f"Error creating knowledge base: {str(e)}")
            raise

    async def get_relevant_context(self, content: str, target_platform: str) -> str:
        """컨텐츠와 관련된 플랫폼별 가이드라인 검색"""
        try:
            retriever = self.knowledge_base.as_retriever(
                search_kwargs={"k": 3}  # 상위 3개 관련 문서 검색
            )
            docs = retriever.get_relevant_documents(
                f"Platform: {target_platform}\n{content}"
            )
            return "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            return ""

    async def convert_content(self, content: str, target_platform: str, has_image: bool = False) -> str:
        """컨텐츠 변환 통합 메서드"""
        try:
            # 관련 컨텍스트 검색
            context = await self.get_relevant_context(content, target_platform)
            
            # 이미지 여부에 따른 추가 지시사항
            image_guide = "이미지가 포함된 게시물입니다." if has_image else "텍스트만 있는 게시물입니다."
            
            # QA 체인 생성 및 실행
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.knowledge_base.as_retriever(),
                memory=self.memory
            )

            prompt = f"""
            다음 컨텐츠를 {target_platform}에 맞게 변환해주세요:
            {content}

            {image_guide}
            
            참고할 플랫폼 가이드라인:
            {context}
            
            변환 시 다음 사항을 고려해주세요:
            1. 각 플랫폼의 특성과 모범 사례
            2. 이미지 포함 여부에 따른 최적화
            3. 해시태그 사용 방식
            4. 글자 수 제한
            """

            response = await qa_chain.ainvoke({"question": prompt})
            return response["answer"]

        except Exception as e:
            logger.error(f"Error converting content: {str(e)}")
            raise

    async def clear_memory(self):
        """대화 기록 초기화"""
        self.memory.clear()