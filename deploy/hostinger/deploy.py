#!/usr/bin/env python3
"""Deploy the site to a Hostinger VPS using the official API."""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


API_BASE = os.getenv("HOSTINGER_API_BASE_URL", "https://developers.hostinger.com").rstrip("/")
VPS_ID = os.getenv("HOSTINGER_VPS_ID")
TOKEN = os.getenv("HOSTINGER_API_TOKEN")
PROJECT_NAME = os.getenv("HOSTINGER_PROJECT_NAME", "polar-sinergy")
REPO_URL = os.getenv("HOSTINGER_REPO_URL", "https://github.com/door2doorbrasil/polar-sinergy-llc")
PURGE_ALL = os.getenv("HOSTINGER_PURGE_ALL", "1").lower() in {"1", "true", "yes", "on"}
SMOKE_URL = os.getenv("HOSTINGER_SMOKE_URL")
SMOKE_TIMEOUT = int(os.getenv("HOSTINGER_SMOKE_TIMEOUT", "15"))
POLL_SECONDS = int(os.getenv("HOSTINGER_POLL_SECONDS", "10"))
POLL_ATTEMPTS = int(os.getenv("HOSTINGER_POLL_ATTEMPTS", "36"))


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def request(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    url = f"{API_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=60) as response:
            body = response.read().decode("utf-8").strip()
            return json.loads(body) if body else None
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        fail(f"{method} {path} failed: HTTP {exc.code} {exc.reason}\n{body}")
    except URLError as exc:
        fail(f"{method} {path} failed: {exc.reason}")


def get_projects() -> list[dict[str, Any]]:
    data = request("GET", f"/api/vps/v1/virtual-machines/{VPS_ID}/docker")
    if not isinstance(data, list):
        fail(f"Unexpected project list response: {data!r}")
    return data


def delete_project(name: str) -> None:
    request("DELETE", f"/api/vps/v1/virtual-machines/{VPS_ID}/docker/{quote(name)}/down")


def deploy_project() -> None:
    request(
        "POST",
        f"/api/vps/v1/virtual-machines/{VPS_ID}/docker",
        {
            "project_name": PROJECT_NAME,
            "content": REPO_URL,
        },
    )


def project_details() -> dict[str, Any]:
    for project in get_projects():
        if project.get("name") == PROJECT_NAME:
            return project
    fail(f"Project {PROJECT_NAME!r} not found after deployment")


def project_containers() -> list[dict[str, Any]]:
    data = request(
        "GET",
        f"/api/vps/v1/virtual-machines/{VPS_ID}/docker/{quote(PROJECT_NAME)}/containers",
    )
    if not isinstance(data, list):
        fail(f"Unexpected container response: {data!r}")
    return data


def smoke_test() -> None:
    if not SMOKE_URL:
        return
    import urllib.request

    deadline = time.time() + SMOKE_TIMEOUT
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(SMOKE_URL, timeout=10) as response:
                body = response.read().decode("utf-8", errors="replace")
                if "Polar Sinergy" in body:
                    print(f"Smoke test passed: {SMOKE_URL}")
                    return
                raise RuntimeError("Smoke test response did not contain the expected site marker")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(2)
    fail(f"Smoke test failed for {SMOKE_URL}: {last_error}")


def main() -> None:
    if not VPS_ID:
        fail("HOSTINGER_VPS_ID is required")
    if not TOKEN:
        fail("HOSTINGER_API_TOKEN is required")

    print(f"Using Hostinger API at {API_BASE}")
    print(f"Target VPS: {VPS_ID}")
    print(f"Project: {PROJECT_NAME}")

    projects = get_projects()
    if PURGE_ALL:
        for project in projects:
            name = project.get("name")
            if name and name != PROJECT_NAME:
                print(f"Removing existing project: {name}")
                delete_project(name)

    print(f"Deploying {PROJECT_NAME} from {REPO_URL}")
    deploy_project()

    for attempt in range(1, POLL_ATTEMPTS + 1):
        details = project_details()
        containers = project_containers()
        state = details.get("state")
        status = details.get("status")
        print(f"Poll {attempt}/{POLL_ATTEMPTS}: state={state} status={status}")
        if state == "running" and containers:
            healthy = all(c.get("state") == "running" for c in containers)
            if healthy:
                break
        time.sleep(POLL_SECONDS)
    else:
        fail("Project did not reach a running state in time")

    print(json.dumps(project_details(), indent=2, ensure_ascii=False))
    print(json.dumps(project_containers(), indent=2, ensure_ascii=False))
    smoke_test()


if __name__ == "__main__":
    main()
