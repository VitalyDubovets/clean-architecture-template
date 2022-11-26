import logging
import os
import shutil

logger = logging.getLogger(__name__)

current_path = os.getcwd()
logger.info(f"Current path: {current_path}")

is_used_postgres = "{{cookiecutter.use_postgres}}" == "yes"
is_used_https_backoff_client = "{{cookiecutter.use_http_backoff_client}}" == "yes"
is_used_kafka = "{{cookiecutter.use_kafka}}" == "yes"


def _remove(filepath: str) -> None:
    if os.path.isdir(filepath):
        shutil.rmtree(filepath)
    else:
        os.remove(filepath)


if not is_used_postgres:
    path = os.path.join(current_path, "app", "infrastructure", "db")
    _remove(path)
    logger.info(f"directory '{path}' was deleted")

    path = os.path.join(current_path, "alembic.ini")
    _remove(path)
    logger.info(f"directory '{path}' was deleted")

if not is_used_postgres:
    path = os.path.join(current_path, "app", "infrastructure", "http")
    _remove(path)
    logger.info(f"directory '{path}' was deleted")

    path = os.path.join(current_path, "app", "core", "interfaces", "service.py")
    _remove(path)
    logger.info(f"directory '{path}' was deleted")


if not is_used_kafka:
    path = os.path.join(current_path, "app", "infrastructure", "ioc", "kafka_container.py")
    _remove(path)
    logger.info(f"directory '{path}' was deleted")

    path = os.path.join(current_path, "app", "infrastructure", "kafka")
    _remove(path)
    logger.info(f"directory '{path}' was deleted")

    path = os.path.join(current_path, "app", "consumer")
    _remove(path)
    logger.info(f"directory '{path}' was deleted")
