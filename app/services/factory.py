from app.services.content import ContentExtractorInterface, HtmlProcessorInterface
from app.services.content import TrafilaturaExtractor, BS4HtmlProcessor
from app.services.image import ImageProcessorInterface, ImageDownloaderInterface
from app.services.image import BS4ImageProcessor, AioHttpDownloader
from app.services.converter import Converter, EPUBConverter, PDFConverter
from app.api.v1.model.enums import EBookFormat
from typing import Optional


class ComponentFactory:
    """컴포넌트 생성 팩토리"""
    
    @staticmethod
    def create_content_extractor(type="trafilatura") -> ContentExtractorInterface:
        """
        컨텐츠 추출기를 생성합니다.
        
        Args:
            type: 추출기 유형 ('trafilatura')
            
        Returns:
            생성된 컨텐츠 추출기
            
        Raises:
            ValueError: 지원하지 않는 추출기 유형인 경우
        """
        if type == "trafilatura":
            return TrafilaturaExtractor()
        else:
            raise ValueError(f"Unsupported content extractor type: {type}")
    
    @staticmethod
    def create_html_processor(type="bs4") -> HtmlProcessorInterface:
        """
        HTML 처리기를 생성합니다.
        
        Args:
            type: HTML 처리기 유형 ('bs4')
            
        Returns:
            생성된 HTML 처리기
            
        Raises:
            ValueError: 지원하지 않는 처리기 유형인 경우
        """
        if type == "bs4":
            return BS4HtmlProcessor()
        else:
            raise ValueError(f"Unsupported HTML processor type: {type}")
    
    @staticmethod
    def create_image_downloader(type="aiohttp") -> ImageDownloaderInterface:
        """
        이미지 다운로더를 생성합니다.
        
        Args:
            type: 다운로더 유형 ('aiohttp')
            
        Returns:
            생성된 이미지 다운로더
            
        Raises:
            ValueError: 지원하지 않는 다운로더 유형인 경우
        """
        if type == "aiohttp":
            return AioHttpDownloader()
        else:
            raise ValueError(f"Unsupported image downloader type: {type}")
    
    @staticmethod
    def create_image_processor(downloader: ImageDownloaderInterface = None, type="bs4") -> ImageProcessorInterface:
        """
        이미지 처리기를 생성합니다.
        
        Args:
            downloader: 사용할 이미지 다운로더 (None이면 기본 다운로더 생성)
            type: 처리기 유형 ('bs4')
            
        Returns:
            생성된 이미지 처리기
            
        Raises:
            ValueError: 지원하지 않는 처리기 유형인 경우
        """
        if downloader is None:
            downloader = ComponentFactory.create_image_downloader()
            
        if type == "bs4":
            return BS4ImageProcessor(downloader)
        else:
            raise ValueError(f"Unsupported image processor type: {type}")


class ConverterFactory:
    """변환기 생성 팩토리"""
    
    @staticmethod
    def create_converter(
        format: EBookFormat,
        content_extractor: Optional[ContentExtractorInterface] = None,
        html_processor: Optional[HtmlProcessorInterface] = None,
        image_processor: Optional[ImageProcessorInterface] = None,
        output_dir: Optional[str] = None
    ) -> Converter:
        """
        변환기를 생성합니다. 컴포넌트가 명시되지 않은 경우 기본 구현을 사용합니다.
        
        Args:
            format: 변환 형식 (EBookFormat enum)
            content_extractor: 컨텐츠 추출기 (None이면 기본값 사용)
            html_processor: HTML 처리기 (None이면 기본값 사용)
            image_processor: 이미지 처리기 (None이면 기본값 사용)
            output_dir: 출력 파일 저장 디렉토리 (None이면 기본값 사용)
            
        Returns:
            생성된 변환기
            
        Raises:
            ValueError: 지원하지 않는 형식인 경우
        """
        # None인 컴포넌트는 기본 구현으로 생성
        if content_extractor is None:
            content_extractor = ComponentFactory.create_content_extractor()
            
        if html_processor is None:
            html_processor = ComponentFactory.create_html_processor()
            
        if image_processor is None:
            image_processor = ComponentFactory.create_image_processor()
        
        # 변환기 인스턴스 생성
        if format == EBookFormat.PDF:
            return PDFConverter(content_extractor, html_processor, image_processor, output_dir)
        elif format == EBookFormat.EPUB:
            return EPUBConverter(content_extractor, html_processor, image_processor, output_dir)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @staticmethod
    def create_custom_converter(
        format: EBookFormat,
        extractor_type="trafilatura",
        processor_type="bs4",
        downloader_type="aiohttp",
        output_dir=None
    ) -> Converter:
        """
        사용자 정의 구성으로 변환기를 생성합니다.
        
        Args:
            format: 변환 형식 (EBookFormat enum)
            extractor_type: 컨텐츠 추출기 유형
            processor_type: HTML 처리기 유형
            downloader_type: 이미지 다운로더 유형
            output_dir: 출력 파일 저장 디렉토리
            
        Returns:
            생성된 변환기
            
        Raises:
            ValueError: 지원하지 않는 형식 또는 구성요소 유형인 경우
        """
        content_extractor = ComponentFactory.create_content_extractor(extractor_type)
        html_processor = ComponentFactory.create_html_processor(processor_type)
        downloader = ComponentFactory.create_image_downloader(downloader_type)
        image_processor = ComponentFactory.create_image_processor(downloader, processor_type)
        
        return ConverterFactory.create_converter(format, content_extractor, html_processor, image_processor, output_dir)
