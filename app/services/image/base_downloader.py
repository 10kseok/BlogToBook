from abc import ABC, abstractmethod


class ImageDownloaderInterface(ABC):
    """이미지 다운로드를 위한 인터페이스"""
    
    @abstractmethod
    async def download(self, img_url: str, temp_dir: str) -> str | None:
        """
        이미지를 다운로드합니다.
        
        Args:
            img_url: 다운로드할 이미지 URL
            temp_dir: 이미지를 저장할 임시 디렉토리
            
        Returns:
            저장된 이미지 파일명 또는 다운로드 실패 시 None
        """
        pass
