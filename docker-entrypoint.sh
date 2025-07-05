#!/bin/sh
set -e

PUID=${PUID:-1000}
PGID=${PGID:-1000}

if ! getent passwd abc > /dev/null; then
    adduser -u $PUID -g $PGID -D abc
fi

chown -R abc:abc /app

find -L /plugins -name requirements.txt -print0 | while IFS= read -r -d $'\0' req_file; do
    pip install --upgrade --disable-pip-version-check -r $req_file
done

exec su-exec abc "$@"
