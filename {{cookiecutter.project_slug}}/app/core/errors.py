import dataclasses
from enum import Enum
from typing import Any, Optional


class ErrorCategories(Enum):
    CONFIGURATION_EXCEPTION = 'ConfigurationException'
    SECURITY_EXCEPTION = 'SecurityException'
    VALIDATION_EXCEPTION = 'ValidationException'
    UNEXPECTED_EXCEPTION = 'UnexpectedException'
    BUSINESS_EXCEPTION = 'BusinessException'


class BaseBusinessError(Exception):
    """
    status: str: Код ошибки
    detail: str: Краткая информация об ошибке
    type: str: Ссылка на вики с описанием типа ошибки
    data: Optional[dict[str, Any]]: НЕОБЯЗАТЕЛЬНОЕ ПОЛЕ (только для dev-а)! Данные, связанные с возникшей ошибкой

    recovery_type: str: НЕОБЯЗАТЕЛЬНОЕ ПОЛЕ (только для dev-а)! Тип необходимый для восстановления исключений при
    межсервисном общении

    raw_type: str: НЕОБЯЗАТЕЛЬНОЕ ПОЛЕ (только для dev-а)! Тип исключения
    category: ErrorCategories: НЕОБЯЗАТЕЛЬНОЕ ПОЛЕ (только для dev-а)! Категория возникшего исключения.
    """
    status: str
    detail: str
    type: str
    data: dict[str, Any] = dataclasses.field(default_factory=dict)
    recovery_type: str = ""
    raw_type: str = ""
    category: Optional[ErrorCategories] = None

    def __init__(
        self, status: str, detail: str, error_type: str, data: dict = None, recovery_type: str = "", raw_type: str = "",
        category: Optional[ErrorCategories] = None
    ):
        self.status = status
        self.detail = detail
        self.type = error_type
        self.data = data or {}
        self.recovery_type = recovery_type or self.recovery_type
        self.raw_type = raw_type or self.raw_type
        self.category = category or self.category

    def as_dict(self):
        return dict(**vars(self))


class ExternalServiceBusinessError(BaseBusinessError):
    ...


class BaseInternalBusinessError(BaseBusinessError):
    def __init__(
        self, status: str, detail: str, error_type: str = "", data: dict = None, recovery_type: str = "",
        raw_type: str = "", category: Optional[ErrorCategories] = None
    ):
        super().__init__(status, detail, error_type, data, recovery_type, raw_type, category)
        self.raw_type = self.raw_type or self.__class__.__name__


class ConfigurationBusinessError(BaseInternalBusinessError):
    category = ErrorCategories.CONFIGURATION_EXCEPTION


class SecurityBusinessError(BaseInternalBusinessError):
    category = ErrorCategories.SECURITY_EXCEPTION


class ValidationBusinessError(BaseInternalBusinessError):
    category = ErrorCategories.VALIDATION_EXCEPTION


class UnexpectedBusinessError(BaseInternalBusinessError):
    category = ErrorCategories.UNEXPECTED_EXCEPTION


class BusinessError(BaseInternalBusinessError):
    category = ErrorCategories.BUSINESS_EXCEPTION
