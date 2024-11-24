import pytest
from app.services.ai import AIService
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_convert_content_success():
    ai_service = AIService()
    content = "테스트 콘텐츠"
    target_platform = "Instagram"
    has_image = True
    expected_response = "변환된 콘텐츠"

    with patch.object(ai_service, 'get_relevant_context', return_value="관련 컨텍스트"):
        with patch.object(ai_service.memory, 'clear') as mock_clear:
            with patch.object(ai_service.llm, 'ainvoke', return_value={'answer': expected_response}) as mock_invoke:
                response = await ai_service.convert_content(content, target_platform, has_image)
                assert response == expected_response
                mock_invoke.assert_called_once()

@pytest.mark.asyncio
async def test_convert_content_failure():
    ai_service = AIService()
    content = "테스트 콘텐츠"
    target_platform = "Instagram"
    has_image = False

    with patch.object(ai_service, 'get_relevant_context', side_effect=Exception("Context error")):
        with pytest.raises(Exception) as exc_info:
            await ai_service.convert_content(content, target_platform, has_image)
        assert str(exc_info.value) == "Context error" 