class ContentExtractFailedException(Exception):
    """웹 페이지에서 콘텐츠를 추출하지 못했을 때 발생하는 예외"""
    def __init__(self, url=None):
        message = f"웹 페이지에서 콘텐츠를 추출할 수 없습니다" + (f": {url}" if url else "")
        super().__init__(message)


class ConversionFailedException(Exception):
    """문서 변환 실패 관련 예외"""
    def __init__(self, format_type=None, error=None):
        message = f"변환 실패" + (f" ({format_type})" if format_type else "")
        if error:
            message += f": {error}"
        super().__init__(message)
