import os
import subprocess
import tempfile
from app.core.config import settings
from app.core.exceptions import ConversionFailedException
from app.services.content import ContentExtractorInterface, HtmlProcessorInterface
from app.services.image import ImageProcessorInterface
from .base import Converter


class PDFConverter(Converter):
    """PDF 형식으로 변환하는 변환기"""
    
    def __init__(
        self,
        content_extractor: ContentExtractorInterface,
        html_processor: HtmlProcessorInterface,
        image_processor: ImageProcessorInterface,
        output_dir: str = None
    ):
        """
        Args:
            content_extractor: 컨텐츠 추출기
            html_processor: HTML 처리기
            image_processor: 이미지 처리기
            output_dir: 출력 파일 저장 디렉토리 (기본값: settings.PDF_OUTPUT_DIR)
        """
        super().__init__(
            output_dir or settings.PDF_OUTPUT_DIR,
            content_extractor,
            html_processor,
            image_processor
        )

    async def convert(self, urls: list[str], title: str) -> str:
        """
        URL 목록의 컨텐츠를 PDF로 변환합니다.
        
        Args:
            urls: 변환할 URL 목록
            title: PDF 파일 제목
            
        Returns:
            생성된 PDF 파일 경로
            
        Raises:
            ConversionFailedException: 변환 실패 시
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            contents = await self._generate_combined_html(urls, temp_dir)
            output_path = os.path.join(self.output_dir, f"{title}.pdf")
            html_filename = self._write_html_file(contents, temp_dir)
            if self._convert_to_pdf(html_filename, output_path, title, temp_dir):
                return output_path
        raise ConversionFailedException("PDF conversion failed")

    def _convert_to_pdf(self, html_filename: str, output_path: str, title: str, work_dir: str) -> bool:
        """
        HTML 파일을 PDF로 변환합니다.
        
        Args:
            html_filename: 변환할 HTML 파일명
            output_path: 출력 PDF 파일 경로
            title: PDF 제목
            work_dir: 작업 디렉토리
            
        Returns:
            변환 성공 여부
        """
        try:
            css_path = str(settings.STATIC_DIR.joinpath('styles', 'ebook.css'))
            if not os.path.exists(css_path):
                raise FileNotFoundError(f"CSS file not found at {css_path}")
            
            cmd = [
                "ebook-convert",
                html_filename,
                output_path,
                "--paper-size", "a4",
                "--pdf-default-font-size", "14",
                "--pdf-mono-font-size", "13",
                "--margin-left", "48",
                "--margin-right", "48",
                "--margin-top", "72",
                "--margin-bottom", "72",
                "--pdf-page-numbers",
                "--enable-heuristics",
                "--title", title,
                "--pdf-header-template", f'<div style="text-align: center; font-size: 10pt">{title}</div>',
                "--pdf-footer-template", '<div style="text-align: center; font-size: 10pt">_PAGENUM_</div>',
                "--level1-toc", "//h:h2",
                "--level2-toc", "//h:h3",
                "--extra-css", css_path,
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)
            if result.returncode == 0:
                print(f"Successfully converted to {output_path}")
                return True
            else:
                print(f"Conversion failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"Exception during PDF conversion: {e}")
            return False
