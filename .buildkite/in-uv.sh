#!/usr/bin/env bash
# Run a command (usually `make <targets>`) inside the image from .buildkite/Dockerfile, with the
# checkout mounted at /work and owned by the calling user. Used by .buildkite/pipeline.yml; works
# the same locally: `.buildkite/in-uv.sh make check`.
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "usage: $0 <command> [args...]" >&2
  exit 2
fi

root="$(cd "$(dirname "$0")/.." && pwd)"
image="$(docker build --quiet --file "$root/.buildkite/Dockerfile" "$root/.buildkite")"

exec docker run --rm \
  --volume "$root:/work" \
  --workdir /work \
  --user "$(id -u):$(id -g)" \
  --env HOME=/tmp/home \
  --env UV_LOCKED=1 \
  --env UV_PROJECT_ENVIRONMENT=/tmp/venv \
  --env CI=true \
  "$image" "$@"
