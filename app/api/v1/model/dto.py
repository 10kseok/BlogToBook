from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing import List
from .enums import EBookFormat


class CamelAliasModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class ConvertRequest(CamelAliasModel):
    book_title: str = Field(..., description="전자책 제목")
    format: EBookFormat = Field(..., description="전자책 포맷 (epub 또는 pdf)")
    links: List[str] = Field(..., description="변환할 블로그 포스트 URL 목록")
