from bs4 import BeautifulSoup
from .base_processor import HtmlProcessorInterface


class BS4HtmlProcessor(HtmlProcessorInterface):
    """BeautifulSoup4를 사용한 HTML 처리기"""
    
    def process(self, html_content: str) -> str:
        """
        HTML 컨텐츠 전처리:
        1. 'graphic' 태그를 'img' 태그로 변환 (trafilatura에서 추출된 이미지 처리)
        2. 중첩된 pre 태그 구조 정리
        3. 단일 라인 짧은 텍스트 pre 태그를 code 태그로 변환
        4. 여러 줄 pre 태그에 코드 블록 클래스 추가
        
        Args:
            html_content: 처리할 HTML 컨텐츠
            
        Returns:
            처리된 HTML 컨텐츠
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
