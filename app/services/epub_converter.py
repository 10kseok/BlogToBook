# 기존의 epub 변환 관련 코드를 여기로 이동
import trafilatura as tf
import requests
import base64
from bs4 import BeautifulSoup
import mimetypes
from urllib.parse import urljoin
import subprocess
import tempfile
import os
from pathlib import Path
from app.core.config import settings

class EPUBConverter:
    def __init__(self, output_dir: str = settings.EPUB_OUTPUT_DIR):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def _get_image_base64(self, img_url: str) -> str | None:
        try:
            response = requests.get(img_url)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if not content_type:
                    ext = mimetypes.guess_type(img_url)[0]
                    content_type = ext if ext else 'image/jpeg'
                
                b64_image = base64.b64encode(response.content).decode('utf-8')
                return f"data:{content_type};base64,{b64_image}"
        except Exception as e:
            print(f"Error downloading image {img_url}: {e}")
        return None

    def _convert_images_to_base64(self, html_content: str, base_url: str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                absolute_url = urljoin(base_url, src)
                base64_data = self._get_image_base64(absolute_url)
                if base64_data:
                    img['src'] = base64_data
        return str(soup)

    def _convert_to_epub(self, html_content: str, output_path: str, title: str) -> bool:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_html:
            temp_html.write(html_content)
            temp_html_path = temp_html.name

        try:
            cmd = [
                'ebook-convert',
                temp_html_path,
                output_path,
                '--enable-heuristics',
                '--input-encoding', 'utf-8',
                '--epub-version', '2',
                '--pretty-print',
                '--title', title,
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

    async def _extract_useful_content(self, url: str) -> str:
        downloaded = tf.fetch_url(url).replace("\\u003C", "<").replace("\\n", "<br>")
        html_content = tf.extract(
            downloaded,
            url=url,
            output_format="html",
            include_images=True,
            include_formatting=True,
            include_comments=True,
            favor_recall=True,
        ).replace("graphic", "img")
        
        # base64로 변환하면 epub으로 변환할 때 따로 이미지를 다운로드하지 않아도 됨
        html_with_base64 = self._convert_images_to_base64(html_content, url)
        
        return html_with_base64
    
    async def convert_urls_to_epub(self, urls: list[str], title: str) -> str:
        contents = "\n".join([await self._extract_useful_content(u) for u in urls])

        # Generate output path
        output_filename = f"{title}.epub"
        output_path = os.path.join(self.output_dir, output_filename)

        # Convert to EPUB
        success = self._convert_to_epub(contents, output_path, title)
        
        if success:
            return output_path
        raise Exception("EPUB conversion failed") 