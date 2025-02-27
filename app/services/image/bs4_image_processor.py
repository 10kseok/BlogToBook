import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base_processor import ImageProcessorInterface
from .base_downloader import ImageDownloaderInterface


class BS4ImageProcessor(ImageProcessorInterface):
    """BeautifulSoup4를 사용한 이미지 처리기"""
    
    def __init__(self, downloader: ImageDownloaderInterface):
        """
        Args:
            downloader: 이미지 다운로드에 사용할 다운로더
        """
        self.downloader = downloader
        
    async def process_images(self, html_content: str, base_url: str, temp_dir: str) -> str:
        """
        BS4를 사용하여 HTML 내 이미지를 처리합니다.
        
        Args:
            html_content: 이미지를 처리할 HTML 컨텐츠
            base_url: 상대 URL을 절대 URL로 변환하기 위한 기본 URL
            temp_dir: 이미지를 저장할 임시 디렉토리
            
        Returns:
            이미지가 처리된 HTML 컨텐츠
        """
        soup = BeautifulSoup(html_content, "html.parser")
        img_tasks = []
        img_elements = []
        
        # 이미지 태그에서 src 추출 및 다운로드 태스크 생성
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                absolute_url = urljoin(base_url, src)
                img_tasks.append(self.downloader.download(absolute_url, temp_dir))
                img_elements.append(img)
        
        # 모든 이미지 비동기 다운로드 실행
        if img_tasks:
            results = await asyncio.gather(*img_tasks, return_exceptions=True)
            
            # 결과 처리 및 HTML 업데이트
            for img, result in zip(img_elements, results):
                if isinstance(result, Exception):
                    print(f"Error downloading image: {result}")
                    continue
                    
                if result:  # 다운로드 성공
                    img["src"] = result
        
        return str(soup)
