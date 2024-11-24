import pytest
from app.services.ai import AIService
from app.utils.rag import RAGConverter

@pytest.mark.asyncio
async def test_content_generation():
    ai_service = AIService()
    prompt = "테스트 게시물입니다. #테스트 #인스타그램"
    target_platform = "Thread"
    
    # 기본 변환 테스트
    basic_result = await ai_service.generate_content(prompt, target_platform)
    assert basic_result is not None
    assert isinstance(basic_result, str)
    
    # RAG 변환 테스트
    rag_result = await ai_service.generate_enhanced_content(prompt, target_platform)
    assert rag_result is not None
    assert isinstance(rag_result, str)

@pytest.mark.asyncio
async def test_rag_converter():
    rag_converter = RAGConverter()
    query = "테스트 게시물입니다."
    target_platform = "Thread"
    
    context = await rag_converter.get_relevant_context(query, target_platform)
    assert context is not None
    assert isinstance(context, str) 