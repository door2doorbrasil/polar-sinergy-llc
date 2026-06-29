#!/bin/sh
set -eu

PROJECT_DIR="${PROJECT_DIR:-/opt/polar-sinergy}"

if [ "${PROJECT_DIR}" = "/" ] || [ -z "${PROJECT_DIR}" ]; then
  echo "PROJECT_DIR is not safe" >&2
  exit 1
fi

if [ -d "${PROJECT_DIR}" ]; then
  docker compose -p polar-sinergy -f "${PROJECT_DIR}/docker-compose.yml" down -v --remove-orphans || true
  rm -rf "${PROJECT_DIR}"
fi

mkdir -p "${PROJECT_DIR}"
echo "Bootstrap complete. Sync the repository into ${PROJECT_DIR} and run deploy/vps/deploy.sh."
