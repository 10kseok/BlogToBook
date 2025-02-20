from abc import ABC, abstractmethod
from pathlib import Path


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
