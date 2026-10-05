"""Stop the kubectl port-forwards started by forwarding.py.

    uv run --project scripts python scripts/kubernetes/kill_forwarding.py

Only PIDs recorded by forwarding.py are stopped, and each is re-checked to
confirm it is still a kubectl port-forward before anything is signalled. It
never touches unrelated kubectl processes.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from port_utils import (  # noqa: E402
    forget_forward,
    is_port_forward_process,
    load_forwards,
    process_command_line,
    save_forwards,
    terminate_pid,
)


def stop_recorded_forwards() -> int:
    """Stop every recorded port-forward we still own."""
    forwards = load_forwards()
    if not forwards:
        print("ℹ️  No port-forwards recorded — nothing to stop.")
        print("   (Recorded PIDs live in infra/.local/port-forwards.json)")
        return 0

    stopped = 0
    for entry in forwards:
        pid = entry.get("pid")
        if not isinstance(pid, int):
            continue

        command = process_command_line(pid)
        if not command:
            print(f"ℹ️  PID {pid} is no longer running.")
            forget_forward(pid)
            continue

        if not is_port_forward_process(command):
            print(f"⚠️  PID {pid} is no longer a kubectl port-forward:")
            print(f"     {command}")
            print("     Leaving it alone.")
            forget_forward(pid)
            continue

        name = entry.get("name", "unknown")
        if terminate_pid(pid):
            print(f"✅ Stopped {name} port-forward (PID {pid})")
            stopped += 1
        else:
            print(f"❌ Could not stop PID {pid}")

        forget_forward(pid)

    remaining = load_forwards()
    save_forwards(remaining)
    return stopped


def main() -> None:
    print("🛑 Stopping SpeechToNote port-forwards")
    stop_recorded_forwards()
    time.sleep(0.5)
    print("✅ Done.")


if __name__ == "__main__":
    main()