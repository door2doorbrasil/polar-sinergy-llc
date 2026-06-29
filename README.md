# Polar Sinergy LLC

Static site for Polar Sinergy LLC, packaged for Docker so it can run cleanly on a VPS.

## Local run

```bash
docker compose up -d --build
```

The site will answer on `http://127.0.0.1:18080/` by default.

## VPS flow

1. Create a fresh target directory on the server:

```bash
PROJECT_DIR=/opt/polar-sinergy sh deploy/vps/bootstrap-zero.sh
```

2. Sync the repository to that directory.
3. Run:

```bash
PROJECT_DIR=/opt/polar-sinergy HOST_PORT=80 sh deploy/vps/deploy.sh
```

## GitHub deploy

The workflow at `.github/workflows/deploy-vps.yml` expects these secrets:

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_PRIVATE_KEY`
- `VPS_PATH`
- `VPS_SSH_PORT` if the server does not use port `22`

On every push to `main`, GitHub syncs the repository to the VPS and runs the deploy script, which recreates the container and performs a smoke test against `http://127.0.0.1/`.
