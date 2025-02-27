from abc import ABC, abstractmethod
from pathlib import Path
import os
import uuid
from app.services.content.base_extractor import ContentExtractorInterface
from app.services.content.base_processor import HtmlProcessorInterface
from app.services.image.base_processor import ImageProcessorInterface


class Converter(ABC):
    """전자책 변환을 위한 기본 클래스"""
    
    def __init__(
        self,
        output_dir: str,
        content_extractor: ContentExtractorInterface,
        html_processor: HtmlProcessorInterface,
        image_processor: ImageProcessorInterface
    ):
        """
        Args:
            output_dir: 출력 파일 저장 디렉토리
            content_extractor: 컨텐츠 추출기
            html_processor: HTML 처리기
            image_processor: 이미지 처리기
        """
        self.output_dir = output_dir
        self.content_extractor = content_extractor
        self.html_processor = html_processor
        self.image_processor = image_processor
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def convert(self, urls: list[str], title: str) -> str:
        """
        URLs의 내용을 전자책으로 변환합니다.

        Args:
            urls: 변환할 블로그 포스트 URL 목록
            title: 전자책 제목

        Returns:
            생성된 전자책 파일의 경로
        """
        pass

    async def _extract_and_process_content(self, url: str, temp_dir: str) -> str:
        """
        URL에서 컨텐츠를 추출하고 처리합니다.
        
        Args:
            url: 컨텐츠를 추출할 URL
            temp_dir: 임시 파일 저장 디렉토리
            
        Returns:
            처리된 HTML 컨텐츠
        """
        raw_content = await self.content_extractor.extract(url)
        processed_html = self.html_processor.process(raw_content)
        return await self.image_processor.process_images(processed_html, url, temp_dir)

    async def _generate_combined_html(self, urls: list[str], temp_dir: str) -> str:
        """
        여러 URL의 컨텐츠를 추출하여 결합합니다.
        
        Args:
            urls: 컨텐츠를 추출할 URL 목록
            temp_dir: 임시 파일 저장 디렉토리
            
        Returns:
            결합된 HTML 컨텐츠
        """
        return "\n".join([await self._extract_and_process_content(url, temp_dir) for url in urls])

    def _write_html_file(self, contents: str, temp_dir: str) -> str:
        """
        HTML 컨텐츠를 파일로 저장합니다.
        
        Args:
            contents: 저장할 HTML 컨텐츠
            temp_dir: 저장할 임시 디렉토리
            
        Returns:
            저장된 HTML 파일명
        """
        html_filename = f"input_{uuid.uuid4()}.html"
        input_html = os.path.join(temp_dir, html_filename)
        with open(input_html, "w", encoding="utf-8") as f:
            f.write(contents)
        return html_filename
