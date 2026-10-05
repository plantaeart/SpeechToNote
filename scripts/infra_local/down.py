"""Stop the SpeechToNote stack.

    uv run --project scripts python scripts/infra_local/down.py

The MongoDB data volume is kept unless --volumes is passed.
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO_ROOT / "infra" / "docker-compose.yml"
ENV_FILE = REPO_ROOT / "infra" / ".env"


def compose_env() -> list[str]:
    return ["--env-file", str(ENV_FILE)] if ENV_FILE.is_file() else []


def run_compose(args: list[str]) -> int:
    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE), *compose_env(), *args]
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Stop the SpeechToNote stack")
    parser.add_argument(
        "--volumes", "-v", action="store_true",
        help="also delete the MongoDB volume (all notes are lost)",
    )
    parser.add_argument(
        "--images", action="store_true", help="also remove the built images"
    )
    args = parser.parse_args()

    if not COMPOSE_FILE.is_file():
        print(f"❌ {COMPOSE_FILE} not found")
        return 1

    compose_args = ["down"]
    if args.volumes:
        compose_args.append("--volumes")

    code = run_compose(compose_args)

    if args.images and code == 0:
        code = run_compose(["rm", "-f", "--stop"])

    print("✅ Stack stopped")
    return code


if __name__ == "__main__":
    sys.exit(main())