FROM python:3.13-alpine3.21 AS base

ENV \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  UV_INSTALL_DIR=/opt/uv

RUN apk add --no-cache \
  build-base python3-dev libffi-dev openssl-dev git su-exec

RUN wget -qO- https://astral.sh/uv/install.sh | sh
ENV PATH="$UV_INSTALL_DIR:$PATH"

RUN rm -f /usr/local/bin/pip /usr/local/bin/pip3 && \
  printf '#!/bin/sh\nexec uv pip "$@"\n' > /usr/local/bin/pip && \
  chmod +x /usr/local/bin/pip

FROM base AS dependencies

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --extra full

FROM base AS runtime

ARG BUILDTIME
ARG VERSION
ARG REVISION

LABEL \
  org.opencontainers.image.authors="Farzin Kazemzadeh <itisFarzin@proton.me>" \
  org.opencontainers.image.source="https://github.com/6AMStuff/itisFarzinBot" \
  org.opencontainers.image.title="itisFarzinBot" \
  org.opencontainers.image.description="A base for Telegram (user)bots" \
  org.opencontainers.image.created=$BUILDTIME \
  org.opencontainers.image.version=$VERSION \
  org.opencontainers.image.revision=$REVISION

WORKDIR /app

COPY --from=dependencies --chown=1000:1000 /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:/opt/uv/bin:$PATH"
ENV VERSION=$VERSION
ENV PLUGINS_REPO=""

COPY --chown=1000:1000 . .

RUN chmod +x docker-entrypoint.sh
RUN mkdir -p config plugins

VOLUME ["/app/config", "/app/plugins"]

ENTRYPOINT ["/app/docker-entrypoint.sh"]

CMD ["python3", "main.py"]
