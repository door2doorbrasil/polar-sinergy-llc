#!/bin/sh
set -eu

PROJECT_DIR="${PROJECT_DIR:-/opt/polar-sinergy}"
HOST_PORT="${HOST_PORT:-80}"

if [ ! -f "${PROJECT_DIR}/docker-compose.yml" ]; then
  echo "docker-compose.yml not found in ${PROJECT_DIR}" >&2
  exit 1
fi

cd "${PROJECT_DIR}"

export HOST_PORT

docker compose -p polar-sinergy down -v --remove-orphans || true
docker compose -p polar-sinergy up -d --build --remove-orphans
docker compose -p polar-sinergy ps

curl -fsS "http://127.0.0.1:${HOST_PORT}/healthz" >/dev/null
curl -fsS "http://127.0.0.1:${HOST_PORT}/" >/dev/null
echo "Deploy and smoke test completed."
