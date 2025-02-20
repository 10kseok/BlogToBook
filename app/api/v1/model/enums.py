from enum import Enum


class EBookFormat(str, Enum):  # str 상속 추가
    """전자책 포맷 열거형"""

    EPUB = "epub"
    PDF = "pdf"

    @property
    def mime_type(self) -> str:
        return {
            EBookFormat.EPUB: "application/epub+zip",
            EBookFormat.PDF: "application/pdf",
        }[self]
