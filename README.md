# Polar Sinergy LLC

Static site for Polar Sinergy LLC, packaged for Docker and deployed directly to a Hostinger VPS through the official API.

## Local run

```bash
docker compose up -d --build
```

The site will answer on `http://127.0.0.1:18080/` by default.

## Hostinger API deploy

The workflow at `.github/workflows/deploy-vps.yml` uses the official Hostinger API.

Required GitHub secrets:

- `HOSTINGER_API_TOKEN`
- `HOSTINGER_VPS_ID`
- `HOSTINGER_PROJECT_NAME`
- `HOSTINGER_SMOKE_URL`

The API token is created from the Hostinger Panel account page. Hostinger documents that API tokens use Bearer authentication, and the Docker Manager can create a project from a GitHub repository URL or raw compose content.

Because the Hostinger Docker Manager pulls the repository by URL, the GitHub repo needs to be publicly reachable.

On every push to `main` or `master`, GitHub:

1. Deletes existing Docker projects on the VPS when `HOSTINGER_PURGE_ALL=1`
2. Recreates the `HOSTINGER_PROJECT_NAME` project from the GitHub repository URL
3. Waits for the containers to come up
4. Runs the smoke test against `HOSTINGER_SMOKE_URL`

## Local run

```bash
docker compose up -d --build
```

The site will answer on `http://127.0.0.1:18080/` by default.
