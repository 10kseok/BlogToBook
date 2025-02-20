from .converter import Converter
from .epub_converter import EPUBConverter
from .pdf_converter import PDFConverter
from app.api.v1.model.enums import EBookFormat


class ConverterFactory:
    @staticmethod
    def create_converter(format: EBookFormat) -> Converter:
        match format:
            case EBookFormat.EPUB:
                return EPUBConverter()
            case EBookFormat.PDF:
                return PDFConverter()
            case _:
                raise ValueError(f"Unsupported format: {format}")
