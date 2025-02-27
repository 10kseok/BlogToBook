"""이미지 처리 모듈: 이미지 다운로드 및 처리 관련 클래스 제공"""

from .base_processor import ImageProcessorInterface
from .base_downloader import ImageDownloaderInterface
from .bs4_image_processor import BS4ImageProcessor
from .aiohttp_downloader import AioHttpDownloader

__all__ = ['ImageProcessorInterface', 'ImageDownloaderInterface', 'BS4ImageProcessor', 'AioHttpDownloader']
