#!/bin/sh
set -e

PUID=${PUID:-1000}
PGID=${PGID:-1000}

export IN_MEMORY=true

if ! getent passwd abc > /dev/null; then
    adduser -u $PUID -g $PGID -D abc
fi

chown -R abc:abc /app /opt/venv

exec su-exec abc "$@"
