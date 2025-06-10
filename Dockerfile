FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PYTHONDONTWRITEBYTECODE=1

RUN apk add --no-cache \
    build-base \
    python3-dev \
    libffi-dev \
    openssl-dev

WORKDIR /app

RUN touch /IS_CONTAINER

RUN mkdir -p data plugins

RUN ln -s /app/data /data && ln -s /app/plugins /plugins

VOLUME ["/data", "/plugins"]

COPY . .

RUN python setup.py

CMD ["python3", "main.py"]
