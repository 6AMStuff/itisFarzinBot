#!/bin/sh
set -e

PUID=${PUID:-1000}
PGID=${PGID:-1000}

if ! getent passwd abc > /dev/null; then
    adduser -u $PUID -g $PGID -D abc
fi

chown -R abc:abc /app

exec su-exec abc "$@"
