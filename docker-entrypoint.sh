#!/bin/sh
set -e

PUID=${PUID:-1000}
PGID=${PGID:-1000}

export IN_MEMORY=true

echo "Setting up user"
if ! getent passwd abc > /dev/null; then
    adduser -u "$PUID" -g "$PGID" -D abc
    echo "Created user 'abc'"
else
    echo "User 'abc' already exists"
fi

echo "Setting up ownership"
dirs="/app /opt/venv"

for dir in $dirs; do
    echo "- $dir"

    current_ids=$(stat -c '%u:%g' "$dir")
    if [ "$current_ids" != "$PUID:$PGID" ]; then
        chown -R "$PUID:$PGID" "$dir"
        echo "Done"
    else
        echo "Skipped"
    fi
done

exec su-exec abc "$@"
