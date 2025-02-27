from abc import ABC, abstractmethod
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString


class Converter(ABC):
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
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

    @abstractmethod
    async def _extract_useful_content(self, url: str) -> str:
        """
        URL에서 유용한 컨텐츠를 추출합니다.

        Args:
            url: 컨텐츠를 추출할 URL

        Returns:
            추출된 HTML 컨텐츠
        """
        pass

    def _preprocess_html_content(self, html_content: str) -> str:
        """
        HTML 컨텐츠를 전처리하는 메서드
        이 메서드는 원본 HTML 컨텐츠를 가져와 다음과 같은 전처리 작업을 수행합니다:
        1. 'graphic' 태그를 'img' 태그로 변환 (trafilatura에서 추출된 이미지 처리)
        2. 중첩된 pre 태그 구조 정리 (중첩된 내부 pre 태그의 내용은 유지하되 태그 자체는 제거)
        3. 단일 라인이고 짧은 텍스트가 포함된 pre 태그를 code 태그로 변환 (인라인 코드 강조용)
        4. 여러 줄이나 긴 텍스트가 있는 pre 태그에는 'code-block' 클래스 추가 (코드 블록 스타일링용)
        Args:
            html_content (str): 전처리할 원본 HTML 문자열
        Returns:
            str: 전처리가 완료된 HTML 문자열
        """
        
        # 1. trafilatura에서 추출된 이미지 태그를 img 태그로 변환
        html_content = html_content.replace("graphic", "img")
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 2. 중첩된 pre 태그 처리 (바깥쪽 pre 태그만 유지)
        for outer_pre in soup.find_all("pre"):
            # 내부에 또 다른 pre 태그가 있는지 확인
            inner_pres = outer_pre.find_all("pre")
            for inner_pre in inner_pres:
                # 내부 pre 태그의 내용을 추출
                content = inner_pre.decode_contents()
                # 내부 pre 태그를 그 내용으로 대체
                inner_pre.replace_with(BeautifulSoup(content, "html.parser"))
        
        # 3. 단일 라인 pre 태그를 code 태그로 변환 (강조용)
        for pre in soup.find_all("pre"):
            # pre 태그 내에 여러 줄이 있는지 확인 (코드 블록)
            content = pre.get_text()
            if "\n" not in content.strip() and len(content) < 100:  # 짧은 텍스트만 강조로 처리
                # 강조용 pre를 code로 변환
                code = soup.new_tag("code")
                code.string = content
                pre.replace_with(code)
            else:
                # 코드 블록은 클래스 추가
                pre['class'] = pre.get('class', []) + ['code-block']
        
        return str(soup)
