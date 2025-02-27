from abc import ABC, abstractmethod


class HtmlProcessorInterface(ABC):
    """HTML 컨텐츠 처리를 위한 인터페이스"""

    @abstractmethod
    def process(self, html_content: str) -> str:
        """
        HTML 컨텐츠를 처리합니다.
        
        Args:
            html_content: 처리할 HTML 컨텐츠
            
        Returns:
            처리된 HTML 컨텐츠
        """
        pass
