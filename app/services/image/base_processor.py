from abc import ABC, abstractmethod


class ImageProcessorInterface(ABC):
    """HTML 내 이미지 처리를 위한 인터페이스"""
    
    @abstractmethod
    async def process_images(self, html_content: str, base_url: str, temp_dir: str) -> str:
        """
        HTML 내 이미지를 처리합니다.
        
        Args:
            html_content: 처리할 HTML 컨텐츠
            base_url: 상대 URL을 절대 URL로 변환하기 위한 기본 URL
            temp_dir: 이미지를 저장할 임시 디렉토리
            
        Returns:
            이미지가 처리된 HTML 컨텐츠
        """
        pass
