from .converter import Converter
import trafilatura as tf
import requests
from bs4 import BeautifulSoup
import mimetypes
from urllib.parse import urljoin
import subprocess
import tempfile
import os
import uuid
from app.core.config import settings


class PDFConverter(Converter):
    def __init__(self):
        super().__init__(settings.PDF_OUTPUT_DIR)

    async def convert(self, urls: list[str], title: str) -> str:
        with tempfile.TemporaryDirectory() as temp_dir:
            contents = await self._generate_combined_html(urls, temp_dir)
            output_path = os.path.join(self.output_dir, f"{title}.pdf")
            html_filename = self._write_html_file(contents, temp_dir)
            if self._convert_to_pdf(html_filename, output_path, title, temp_dir):
                return output_path
        raise Exception("PDF conversion failed")

    async def _generate_combined_html(self, urls: list[str], temp_dir: str) -> str:
        return "\n".join([await self._extract_useful_content(u, temp_dir) for u in urls])

    def _write_html_file(self, contents: str, temp_dir: str) -> str:
        html_filename = f"input_{uuid.uuid4()}.html"
        input_html = os.path.join(temp_dir, html_filename)
        with open(input_html, "w", encoding="utf-8") as f:
            f.write(contents)
        return html_filename

    async def _extract_useful_content(self, url: str, temp_dir: str) -> str:
        downloaded = tf.fetch_url(url)
        html_content = tf.extract(
            downloaded,
            url=url,
            output_format="html",
            include_images=True,
            include_formatting=True,
            favor_recall=True,
            include_comments=False,
        ).replace("graphic", "img") # trafilatura는 img 태그를 graphic으로 변환하기 때문에 다시 img로 변환
        return self._replace_images_with_temp_files(html_content, url, temp_dir)

    def _replace_images_with_temp_files(self, html_content: str, base_url: str, temp_dir: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                absolute_url = urljoin(base_url, src)
                filename = self._download_image(absolute_url, temp_dir)
                if filename:
                    img["src"] = filename
        return str(soup)

    def _download_image(self, img_url: str, temp_dir: str) -> str | None:
        try:
            response = requests.get(img_url)
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                ext = mimetypes.guess_extension(content_type) if content_type else ".jpg"
                filename = f"{uuid.uuid4()}{ext}"
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return filename
        except Exception as e:
            print(f"Error downloading image {img_url}: {e}")
        return None

    def _convert_to_pdf(self, html_filename: str, output_path: str, title: str, work_dir: str) -> bool:
        try:
            css_path = str(settings.STATIC_DIR.joinpath('styles', 'ebook.css'))
            if not os.path.exists(css_path):
                raise FileNotFoundError(f"CSS file not found at {css_path}")
            cmd = [
                "ebook-convert",
                html_filename,  # HTML 파일명만 전달
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
