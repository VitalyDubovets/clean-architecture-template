from enum import Enum


class Status(str, Enum):
    HEALTHY = "Healthy"
    UNHEALTHY = "Unhealthy"
