FROM python:3.13-alpine AS base

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PYTHONDONTWRITEBYTECODE=1

RUN apk add --no-cache \
    build-base python3-dev libffi-dev openssl-dev git su-exec

RUN touch /IS_CONTAINER

FROM base AS dependencies

COPY requirements.txt /tmp/

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --disable-pip-version-check --break-system-packages --root-user-action ignore -r /tmp/requirements.txt

FROM base AS runtime

ARG BUILDTIME
ARG VERSION
ARG REVISION

LABEL \
  maintainer="Farzin Kazemzadeh <itisFarzin@gmail.com>" \
  org.opencontainers.image.authors="Farzin Kazemzadeh <itisFarzin@gmail.com>" \
  org.opencontainers.image.source="https://github.com/6AMStuff/itisFarzinBot" \
  org.opencontainers.image.title="itisFarzinBot" \
  org.opencontainers.image.description="My personal Telegram bot with Kurigram" \
  org.opencontainers.image.created=$BUILDTIME \
  org.opencontainers.image.version=$VERSION \
  org.opencontainers.image.revision=$REVISION

COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY . .

RUN chmod +x docker-entrypoint.sh

RUN mkdir data plugins \
    && ln -s /app/data /data \
    && ln -s /app/plugins /plugins

VOLUME ["/data", "/plugins"]

ENTRYPOINT ["/app/docker-entrypoint.sh"]

CMD ["python3", "main.py"]
