from abc import ABC, abstractmethod


class ContentExtractorInterface(ABC):
    """웹 컨텐츠 추출을 위한 인터페이스"""

    @abstractmethod
    async def extract(self, url: str) -> str:
        """
        URL에서 유용한 컨텐츠를 추출합니다.

        Args:
            url: 컨텐츠를 추출할 URL

        Returns:
            추출된 HTML 컨텐츠

        Raises:
            UsefulExtractFailedException: 유용한 컨텐츠를 추출하지 못한 경우
        """
        pass
