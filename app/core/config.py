from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 프로젝트 기본 경로 설정
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    
    @property
    def STATIC_DIR(self) -> Path:
        return self.BASE_DIR.joinpath('app', 'static')
    
    @property
    def PDF_OUTPUT_DIR(self) -> Path:
        return self.BASE_DIR.joinpath('output', 'pdf')
    
    @property
    def EPUB_OUTPUT_DIR(self) -> Path:
        return self.BASE_DIR.joinpath('output', 'epub')

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EPUB Converter"

    class Config:
        case_sensitive = True


settings = Settings()
