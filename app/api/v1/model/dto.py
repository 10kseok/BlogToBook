from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelAliasModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ConvertRequest(CamelAliasModel):
  book_title: str
  links: list[str]
