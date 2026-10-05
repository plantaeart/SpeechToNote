"""Tests that keep CORS in sync with the ports the app is actually served on.

A port that is missing from CORS makes the browser block API calls, which looks
like a backend failure but is not one.
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CORS_FILE = REPO_ROOT / "backend/speech-to-note-backend/app/config_cors.py"


def _cors_origins() -> list[str]:
    source = CORS_FILE.read_text()
    block = source.split('"allow_origins":', 1)[1].split("]", 1)[0]
    return re.findall(r'"(http://[^"]+)"', block)


def _compose_port(name: str) -> str:
    compose = (REPO_ROOT / "infra/docker-compose.yml").read_text()
    match = re.search(rf"{name}:-\d+", compose)
    return match.group(0).split(":-")[1]


def _forwarding_port(name: str) -> str:
    source = (REPO_ROOT / "scripts/kubernetes/forwarding.py").read_text()
    match = re.search(rf'DEFAULT_PORTS\s*=\s*\{{[^}}]*"{name}":\s*(\d+)', source)
    return match.group(1)


@pytest.mark.parametrize(
    "origin",
    [
        "http://localhost:5173",  # vite dev server
        "http://localhost:4173",  # vite preview (npm run preview / cypress)
    ],
)
def test_cors_allows_standard_dev_ports(origin):
    assert origin in _cors_origins(), f"CORS must allow {origin}"


def test_cors_allows_compose_frontend_port():
    """docker-compose publishes the frontend on FRONTEND_PORT."""
    port = _compose_port("FRONTEND_PORT")
    assert f"http://localhost:{port}" in _cors_origins(), (
        f"compose serves the frontend on {port} but CORS does not allow it"
    )


def test_cors_allows_kind_frontend_port():
    """forwarding.py publishes the frontend on 8080 for the kind cluster."""
    port = _forwarding_port("frontend")
    assert f"http://localhost:{port}" in _cors_origins(), (
        f"the kind frontend runs on {port} (see README) but CORS does not allow it"
    )


def test_cors_origins_are_loopback_only():
    """Local-only app: a wildcard origin would expose the API to any site."""
    for origin in _cors_origins():
        assert "localhost" in origin or "127.0.0.1" in origin, (
            f"non-loopback origin in CORS: {origin}"
        )
    assert not any(o == "*" for o in _cors_origins()), (
        "a wildcard origin would let any website call this local API"
    )

def test_kub_env_api_url_matches_the_port_forwarding_serves():
    """The kind build must call the API on the port forwarding.py exposes.

    NodePorts are bound inside the kind node, not on the host, so pointing the
    frontend at one makes every request fail.
    """
    env_file = (
        REPO_ROOT
        / "frontend/speech-to-note-frontend/src/config/env.local.kub.ts"
    )
    source = env_file.read_text()
    match = re.search(r"API_BASE_URL:\s*'([^']+)'", source)
    assert match, "env.local.kub.ts must define API_BASE_URL"

    url = match.group(1)
    port = url.rsplit(":", 1)[1]
    expected = _forwarding_port("backend")

    assert port == expected, (
        f"env.local.kub.ts calls {url}, but forwarding.py exposes the API on "
        f"{expected}. NodePorts are not reachable from the host — use "
        "scripts/kubernetes/forwarding.py."
    )


def test_readme_tells_users_to_set_the_key_before_starting():
    """The quick start must tell users to add the key before running `up`.

    Otherwise users start the stack, find recording does nothing, and have to
    restart it with a key.
    """
    readme = (REPO_ROOT / "README.md").read_text()

    # Anchor links must point at the real heading (GitHub slug form).
    assert "## Generate a Google Cloud API key" in readme
    assert "(#generate-a-google-cloud-api-key)" in readme

    quickstart = readme.split("## Quick start", 1)[1].split("\n## ", 1)[0]
    up_position = quickstart.find("infra_local/up.py")
    key_position = quickstart.find("GCP_API_KEY")

    assert key_position != -1, "quick start must mention GCP_API_KEY"
    assert up_position != -1, "quick start must show the up.py command"
    assert key_position < up_position, (
        "the key instructions must come before the `up.py` command so users "
        "do not have to restart the stack"
    )


def test_infra_env_example_documents_the_key():
    example = (REPO_ROOT / "infra/.env.example").read_text()
    assert "GCP_API_KEY=" in example
