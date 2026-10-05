"""Tests for the local Docker Compose stack.

These guard the things that silently break a clone: host-specific paths in the
service registry, and drift between the compose file and the app config.
"""

import os
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "docker"))

from docker_image_commands.core.service_model import services_registry  # noqa: E402

COMPOSE_FILE = REPO_ROOT / "infra" / "docker-compose.yml"


@pytest.mark.parametrize("service", ["backend", "frontend"])
def test_service_paths_resolve_on_this_platform(service):
    """Registry paths must resolve to real directories from the repo root.

    Windows-style backslash paths made every build fail on Linux/macOS.
    DockerManager resolves them against the project root, so do the same here.
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "docker"))
    from docker_image_commands.core.docker_image_manager_core import DockerManager

    paths = DockerManager().get_project_paths(service)
    assert os.path.isdir(paths["context_path"]), (
        f"{service}: build context not found: {paths['context_path']}"
    )
    assert os.path.isfile(paths["dockerfile_path"]), (
        f"{service}: Dockerfile not found: {paths['dockerfile_path']}"
    )


def test_service_paths_use_no_hardcoded_separators():
    """A backslash in a registry path is always wrong on POSIX."""
    for name, config in services_registry.items():
        for value in (config.context_path, config.dockerfile_path):
            assert "\\" not in value, f"{name}: hardcoded Windows separator in {value!r}"


def test_compose_file_exists():
    assert COMPOSE_FILE.is_file(), "infra/docker-compose.yml is missing"


@pytest.mark.parametrize(
    "service", ["mongo", "backend", "frontend"]
)
def test_compose_defines_service(service):
    content = COMPOSE_FILE.read_text()
    assert re.search(rf"^  {service}:", content, re.MULTILINE), (
        f"compose file does not define the '{service}' service"
    )


def test_mongo_publishes_no_host_port():
    """Another local app may already own 27017; mongo must stay internal."""
    content = COMPOSE_FILE.read_text()
    mongo_block = content.split("  mongo:", 1)[1].split("\n  backend:", 1)[0]
    assert "ports:" not in mongo_block, (
        "mongo must not publish a host port — nothing outside the compose "
        "network needs it, and 27017 is often already taken"
    )


def test_compose_backend_waits_for_mongo():
    content = COMPOSE_FILE.read_text()
    backend_block = content.split("  backend:", 1)[1].split("\n  frontend:", 1)[0]
    assert "depends_on:" in backend_block
    assert "mongo" in backend_block
    assert "condition:" in backend_block, "backend must wait for mongo to be healthy"


def test_compose_backend_uri_uses_service_name():
    """Inside compose the host is the service name, not host.docker.internal."""
    content = COMPOSE_FILE.read_text()
    assert "mongodb://mongo:27017" in content
    assert "host.docker.internal" not in content


def test_frontend_port_matches_cors_and_readme():
    """The published frontend port must be allowed by CORS and used in docs."""
    content = COMPOSE_FILE.read_text()
    frontend_block = content.split("  frontend:", 1)[1]
    match = re.search(r'\$\{FRONTEND_PORT:-(\d+)\}:80', frontend_block)
    assert match, "frontend must publish a host port to container port 80"
    host_port = match.group(1)

    cors = (REPO_ROOT / "backend/speech-to-note-backend/app/config_cors.py").read_text()
    assert f"http://localhost:{host_port}" in cors, (
        f"frontend published on {host_port} but CORS does not allow it"
    )
    assert f"http://localhost:{host_port}" in (REPO_ROOT / "README.md").read_text()


def test_docker_config_uses_compose_service_name():
    """DockerConfig should not need --add-host to reach mongo in compose."""
    config = (REPO_ROOT / "backend/speech-to-note-backend/app/configs/docker.py").read_text()
    assert "mongodb://mongo:27017" in config
    assert "host.docker.internal" not in config


def test_gcp_key_is_injected_at_runtime_not_build_time():
    """The key must never be baked into an image layer."""
    content = COMPOSE_FILE.read_text()
    assert "GCP_API_KEY" in content
    dockerfile = (REPO_ROOT / "frontend/Dockerfile").read_text()
    assert "GCP_API_KEY" not in dockerfile, (
        "the key must be injected at container start, not at build time"
    )


@pytest.mark.parametrize(
    "service, dockerfile_rel",
    [
        ("backend", "backend/speech-to-note-backend/Dockerfile"),
        ("frontend", "frontend/Dockerfile"),
    ],
)
def test_compose_context_contains_everything_its_dockerfile_copies(
    service, dockerfile_rel
):
    """A COPY source must exist inside the declared build context.

    Copying a file outside the context fails at build time with a checksum
    error, which is slow and confusing to diagnose.
    """
    content = COMPOSE_FILE.read_text()
    block = content.split(f"  {service}:", 1)[1]
    context_match = re.search(r"context:\s*(\S+)", block)
    assert context_match, f"{service}: no build context declared"

    context_dir = (COMPOSE_FILE.parent / context_match.group(1)).resolve()
    assert context_dir.is_dir(), f"{service}: context dir not found: {context_dir}"

    dockerfile = (REPO_ROOT / dockerfile_rel).read_text()
    for line in re.findall(r"^COPY\s+(.+)$", dockerfile, re.MULTILINE):
        parts = line.split()
        # Copies from another build stage are not bound by the context.
        if any(part.startswith("--from=") for part in parts):
            continue
        sources = [part for part in parts if not part.startswith("--")]
        for source in sources[:-1]:  # the last item is the destination
            if source.startswith("/"):
                continue  # absolute path inside the image, not the context
            candidate = (context_dir / source).resolve()
            assert candidate.exists(), (
                f"{service}: Dockerfile copies {source!r}, which is not inside "
                f"the build context {context_dir}"
            )


def test_frontend_dockerignore_excludes_node_modules():
    """The frontend context contains node_modules locally; keep it out."""
    ignore = (REPO_ROOT / "frontend/.dockerignore").read_text()
    assert "node_modules" in ignore


def test_entrypoint_escapes_quotes_in_key():
    """A quote in the key must not break out of the generated JS string."""
    entrypoint = (REPO_ROOT / "frontend/docker-entrypoint.sh").read_text()
    assert "escape()" in entrypoint
    assert 's/"/' in entrypoint, "the entrypoint must escape double quotes"


def test_index_html_loads_env_js_before_app():
    """The runtime config must be read before the app boots."""
    index = (REPO_ROOT / "frontend/speech-to-note-frontend/index.html").read_text()
    assert index.index("/env.js") < index.index("/src/main.ts")
    assert (REPO_ROOT / "frontend/speech-to-note-frontend/public/env.js").is_file()