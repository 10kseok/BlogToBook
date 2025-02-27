import os
import uuid
import mimetypes
import aiohttp
from .base_downloader import ImageDownloaderInterface


class AioHttpDownloader(ImageDownloaderInterface):
    """aiohttp를 사용한 비동기 이미지 다운로더"""
    
    async def download(self, img_url: str, temp_dir: str) -> str | None:
        """
        aiohttp를 사용하여 이미지를 비동기적으로 다운로드합니다.
        
        Args:
            img_url: 다운로드할 이미지 URL
            temp_dir: 이미지를 저장할 임시 디렉토리
            
        Returns:
            저장된 이미지 파일명 또는 다운로드 실패 시 None
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(img_url) as response:
                    if response.status == 200:
                        content_type = response.headers.get("content-type", "")
                        ext = mimetypes.guess_extension(content_type) if content_type else ".jpg"
                        filename = f"{uuid.uuid4()}{ext}"
                        file_path = os.path.join(temp_dir, filename)
                        
                        with open(file_path, "wb") as f:
                            f.write(await response.read())
                            
                        return filename
        except Exception as e:
            print(f"Error downloading image {img_url}: {e}")
        return None
