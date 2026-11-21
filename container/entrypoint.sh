#!/bin/sh
set -eu

jarvis-v2 init --state "${ARCHON_STATE:-/var/lib/archon}"
exec "$@"
