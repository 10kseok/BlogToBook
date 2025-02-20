from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EPUB Converter"
    EPUB_OUTPUT_DIR: str = "output/epub"
    PDF_OUTPUT_DIR: str = "output/pdf"

    class Config:
        case_sensitive = True


settings = Settings()
