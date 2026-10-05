"""Bring the whole SpeechToNote stack up with Docker Compose.

    uv run --project scripts python scripts/infra_local/up.py
"""

import argparse
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO_ROOT / "infra" / "docker-compose.yml"
ENV_FILE = REPO_ROOT / "infra" / ".env"

TIMEOUT_SECONDS = 180


def env_port(name: str, default: int) -> int:
    """Read a port from infra/.env, falling back to the default."""
    if ENV_FILE.is_file():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line.startswith(f"{name}="):
                value = line.split("=", 1)[1].strip()
                if value.isdigit():
                    return int(value)
    return default


def compose_env() -> list[str]:
    """Build the --env-file argument when the user has created one."""
    return ["--env-file", str(ENV_FILE)] if ENV_FILE.is_file() else []


def has_api_key() -> bool:
    """True when infra/.env defines a non-empty GCP_API_KEY."""
    if not ENV_FILE.is_file():
        return False
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("GCP_API_KEY="):
            return bool(line.split("=", 1)[1].strip().strip("\"'"))
    return False


def run_compose(args: list[str]) -> int:
    cmd = [
        "docker", "compose",
        "-f", str(COMPOSE_FILE),
        *compose_env(),
        *args,
    ]
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def wait_for_backend(port: int, timeout: int) -> bool:
    """Poll the API until it answers, so we do not report success too early."""
    url = f"http://127.0.0.1:{port}/speaker_notes/"
    deadline = time.time() + timeout
    print(f"⏳ Waiting for the backend on {url} ...")

    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if response.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(2)

    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Start the SpeechToNote stack")
    parser.add_argument(
        "--no-build", action="store_true", help="reuse existing images"
    )
    parser.add_argument(
        "--timeout", type=int, default=TIMEOUT_SECONDS,
        help=f"seconds to wait for the backend (default: {TIMEOUT_SECONDS})",
    )
    args = parser.parse_args()

    if not COMPOSE_FILE.is_file():
        print(f"❌ {COMPOSE_FILE} not found")
        return 1

    if not ENV_FILE.is_file():
        print("ℹ️  No infra/.env found — starting without a Google API key.")
        print("   Copy infra/.env.example to infra/.env to enable speech recognition.")
    elif not has_api_key():
        print("⚠️  GCP_API_KEY is empty in infra/.env — speech recognition will not work.")
        print("   Get a key: see 'Generate a Google Cloud API key' in the README,")
        print("   then set GCP_API_KEY=... in infra/.env and run this script again.")

    compose_args = ["up", "-d"]
    if not args.no_build:
        compose_args.append("--build")

    code = run_compose(compose_args)
    if code != 0:
        print("❌ docker compose up failed")
        return code

    backend_port = env_port("BACKEND_PORT", 8000)
    frontend_port = env_port("FRONTEND_PORT", 5173)

    if not wait_for_backend(backend_port, args.timeout):
        print("❌ The backend did not become ready in time.")
        print("   Check the logs with: docker compose -f infra/docker-compose.yml logs")
        return 1

    print("\n✅ SpeechToNote is up")
    print(f"   Frontend  http://localhost:{frontend_port}")
    print(f"   API docs  http://localhost:{backend_port}/docs")
    return 0


if __name__ == "__main__":
    sys.exit(main())