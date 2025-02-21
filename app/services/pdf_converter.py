from .converter import Converter
import trafilatura as tf
import requests
import base64
from bs4 import BeautifulSoup
import mimetypes
from urllib.parse import urljoin
import subprocess
import tempfile
import os
from app.core.config import settings


class PDFConverter(Converter):
    def __init__(self):
        super().__init__(settings.PDF_OUTPUT_DIR)

    async def convert(self, urls: list[str], title: str) -> str:
        contents = "\n".join([await self._extract_useful_content(u) for u in urls])
        output_filename = f"{title}.pdf"
        output_path = os.path.join(self.output_dir, output_filename)

        success = self._convert_to_pdf(contents, output_path, title)
        if success:
            return output_path
        raise Exception("PDF conversion failed")

    async def _extract_useful_content(self, url: str) -> str:
        downloaded = tf.fetch_url(url)
        html_content = tf.extract(
            downloaded,
            url=url,
            output_format="html",
            include_images=True,
            include_formatting=True,
            favor_recall=True,
            include_comments=False,
        ).replace("graphic", "img")

        return self._convert_images_to_base64(html_content, url)

    def _convert_images_to_base64(self, html_content: str, base_url: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                absolute_url = urljoin(base_url, src)
                base64_data = self._get_image_base64(absolute_url)
                if base64_data:
                    img["src"] = base64_data
        return str(soup)

    def _get_image_base64(self, img_url: str) -> str | None:
        try:
            response = requests.get(img_url)
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if not content_type:
                    ext = mimetypes.guess_type(img_url)[0]
                    content_type = ext if ext else "image/jpeg"

                b64_image = base64.b64encode(response.content).decode("utf-8")
                return f"data:{content_type};base64,{b64_image}"
        except Exception as e:
            print(f"Error downloading image {img_url}: {e}")
        return None

    def _convert_to_pdf(self, html_content: str, output_path: str, title: str) -> bool:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        ) as temp_html:
            temp_html.write(html_content)
            temp_html_path = temp_html.name

        try:
            css_path = str(settings.STATIC_DIR.joinpath('styles', 'ebook.css'))
            if not os.path.exists(css_path):
                raise FileNotFoundError(f"CSS file not found at {css_path}")
                
            cmd = [
                "ebook-convert",
                temp_html_path,
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
                "--pdf-header-template",
                f'<div style="text-align: center; font-size: 10pt">{title}</div>',
                "--pdf-footer-template",
                '<div style="text-align: center; font-size: 10pt">_PAGENUM_</div>',
                "--level1-toc", "//h:h2",
                "--level2-toc", "//h:h3",
                "--extra-css", css_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            success = result.returncode == 0

            if success:
                print(f"Successfully converted to {output_path}")
            else:
                print(f"Conversion failed: {result.stderr}")

            return success

        finally:
            os.unlink(temp_html_path)
