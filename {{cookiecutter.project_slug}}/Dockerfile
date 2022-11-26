FROM python:3.10-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PROJECT_DIR /service
ENV PYTHONPATH $PROJECT_DIR/app
ENV PORT 8000

WORKDIR $PROJECT_DIR
ARG POETRY_EXPORT_OPTIONS

COPY poetry.lock pyproject.toml ./

RUN apt-get update && \
    apt-get install -y build-essential gcc g++ libstdc++6 linux-headers-generic && \
    pip install --upgrade pip && \
    pip install -U poetry && \
    poetry export ${POETRY_EXPORT_OPTIONS} --without-hashes -o requirements.txt && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.10-slim

ENV PROJECT_DIR /service
ENV PYTHONPATH $PROJECT_DIR/app
ENV PORT 8000

WORKDIR $PROJECT_DIR

COPY --from=builder /app/wheels /wheels

RUN apt-get update && \
    pip install --upgrade pip && \
    pip install --no-cache /wheels/*

COPY ./ $PROJECT_DIR

EXPOSE $PORT
