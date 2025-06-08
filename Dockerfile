FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN touch /IS_CONTAINER

RUN mkdir -p data plugins

RUN ln -s /app/data /data && ln -s /app/plugins /plugins

VOLUME ["/data", "/plugins"]

COPY . .

RUN python setup.py

CMD ["python3", "main.py"]
