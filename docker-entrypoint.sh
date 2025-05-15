#!/bin/sh
set -e

rm -rf data plugins
ln -s /data /app/
ln -s /plugins /app/

exec "$@"
