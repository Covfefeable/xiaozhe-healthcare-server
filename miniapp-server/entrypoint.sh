#!/bin/sh

set -e

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    uv run flask db upgrade
fi

exec "$@"
