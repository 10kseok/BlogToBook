from pydantic_settings import BaseSettings
import tempfile
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EPUB Converter"
    # 기본값으로 시스템 임시 디렉토리 아래에 epub_outputs 폴더 사용
    EPUB_OUTPUT_DIR: str = os.path.join(tempfile.gettempdir(), "outputs")
    
    class Config:
        case_sensitive = True

settings = Settings() 