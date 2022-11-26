from humps import camelize
from pydantic import BaseModel


class CustomModel(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class BaseCommand(CustomModel):
    ...


class BaseCommandResult(BaseModel):
    ...


class BaseQuery(CustomModel):
    ...


class BaseResult(CustomModel):
    ...


class BaseUseCaseResult(BaseModel):
    ...
