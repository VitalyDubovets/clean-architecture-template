from humps import camelize
from pydantic import BaseModel


class BaseCamelCaseModel(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True
