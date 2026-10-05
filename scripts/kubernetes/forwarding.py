"""Port-forward the SpeechToNote services from the local kind cluster.

    uv run --project scripts python scripts/kubernetes/forwarding.py

Port conflicts are reported, never resolved by killing a process: whatever
holds the port may be an editor, a database or another project.
"""

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from port_utils import (  # noqa: E402
    describe_conflict,
    is_port_available,
    load_forwards,
    save_forwards,
)

# The API is already reachable on NodePort 30002 and the frontend on 30080,
# so port-forwarding is optional. These defaults avoid colliding with them.
DEFAULT_PORTS = {"frontend": 8080, "backend": 8081}

SERVICES = {
    "frontend": {"service": "vue-service", "target": "80"},
    "backend": {"service": "fastapi-service", "target": "8000"},
}


def check_services_exist() -> dict:
    """Return which of our services the cluster exposes."""
    try:
        result = subprocess.run(
            ["kubectl", "get", "services", "-o", "name"],
            capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {}

    services = result.stdout.split()
    return {
        name: True
        for name, config in SERVICES.items()
        if any(config["service"] in entry for entry in services)
    }


def require_free_port(port: int) -> bool:
    """Report a busy port and return False so the caller can stop."""
    if is_port_available(port):
        return True
    print(f"\n❌ {describe_conflict(port)}\n")
    return False


def start_forward(name: str, local_port: int) -> int | None:
    """Start kubectl port-forward and record its PID."""
    config = SERVICES[name]
    command = [
        "kubectl", "port-forward",
        f"service/{config['service']}",
        f"{local_port}:{config['target']}",
    ]
    print(f"▶ {name}: kubectl port-forward {local_port} -> {config['target']}")

    try:
        process = subprocess.Popen(command)
    except FileNotFoundError:
        print("❌ kubectl was not found on your PATH.")
        return None

    time.sleep(1)
    if process.poll() is not None:
        print(f"❌ {name}: port-forward exited immediately (port {local_port} busy?)")
        return None

    forwards = load_forwards()
    forwards.append({"pid": process.pid, "port": local_port, "name": name})
    save_forwards(forwards)
    return process.pid


def print_summary(ports: dict) -> None:
    print("\n✅ Port-forwarding running. Press Ctrl+C to stop.")
    if "frontend" in ports:
        print(f"   Frontend  http://localhost:{ports['frontend']}")
    if "backend" in ports:
        print(f"   API docs  http://localhost:{ports['backend']}/docs")
    print("\n   The kind cluster also exposes the API directly on http://localhost:30002")


def main() -> None:
    print("🔗 Port-forwarding for SpeechToNote")
    print("=" * 50)

    available = check_services_exist()
    if not available:
        print("❌ No SpeechToNote services found in the current cluster.")
        print("   Run start.py first, and check that kubectl points at the kind cluster:")
        print("   kubectl config current-context")
        return

    print("Services detected: " + ", ".join(sorted(available)))

    ports: dict = {}
    for name in available:
        port = DEFAULT_PORTS[name]
        if not require_free_port(port):
            continue
        if start_forward(name, port) is not None:
            ports[name] = port

    if not ports:
        print("\nNothing was started.")
        return

    print_summary(ports)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping. Run kill_forwarding.py to end the forwards.")


if __name__ == "__main__":
    main()