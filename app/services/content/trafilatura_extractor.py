import trafilatura as tf
from app.core.exceptions import ContentExtractFailedException
from .base_extractor import ContentExtractorInterface


class TrafilaturaExtractor(ContentExtractorInterface):
    """Trafilatura 라이브러리를 사용한 컨텐츠 추출기"""
    
    async def extract(self, url: str) -> str:
        """
        Trafilatura를 사용하여 URL에서 컨텐츠를 추출합니다.
        
        Args:
            url: 컨텐츠를 추출할 URL
            
        Returns:
            HTML 형식의 컨텐츠
            
        Raises:
            ContentExtractFailedException: 컨텐츠 추출 실패 시
        """
        downloaded = tf.fetch_url(url)
        html_content = tf.extract(
            downloaded,
            url=url,
            output_format="html",
            include_images=True,
            include_formatting=True,
            favor_recall=True,
            include_comments=False,
        )
        
        if not html_content:
            raise ContentExtractFailedException(url)
        
        return html_content
