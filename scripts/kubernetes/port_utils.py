"""Cross-platform port helpers for the kind scripts.

These helpers deliberately never kill anything. A port conflict is reported to
the user with the owning PID so they can decide what to do — killing whatever
happens to hold a port is how these scripts used to terminate an unrelated
process (an IDE, a database, another project).
"""

import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_FILE = REPO_ROOT / "infra" / ".local" / "port-forwards.json"


def is_windows() -> bool:
    return sys.platform == "win32"


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """True when nothing is listening on the port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def pids_on_port(port: int) -> list[int]:
    """PIDs listening on the given port (empty when unknown).

    Uses lsof on macOS/Linux and netstat on Windows. Returns an empty list
    rather than guessing when the lookup tool is unavailable.
    """
    try:
        if is_windows():
            result = subprocess.run(
                ["netstat", "-ano", "-p", "TCP"],
                capture_output=True, text=True, check=False,
            )
            pids = set()
            for line in result.stdout.splitlines():
                if not re.search(rf":{port}\s", line) or "LISTENING" not in line:
                    continue
                parts = line.split()
                if len(parts) >= 5 and parts[-1].isdigit():
                    pids.add(int(parts[-1]))
            return sorted(pids)

        result = subprocess.run(
            ["lsof", "-ti", f":{port}", "-sTCP:LISTEN"],
            capture_output=True, text=True, check=False,
        )
        return sorted(
            int(line) for line in result.stdout.split() if line.strip().isdigit()
        )
    except (OSError, subprocess.SubprocessError):
        return []


def process_command_line(pid: int) -> str:
    """Best-effort command line for a PID (empty when unavailable)."""
    try:
        if is_windows():
            # wmic was removed in Windows 11 24H2+, so prefer PowerShell/CIM.
            result = subprocess.run(
                [
                    "powershell", "-NoProfile", "-Command",
                    "(Get-CimInstance Win32_Process -Filter "
                    f'"ProcessId={pid}").CommandLine',
                ],
                capture_output=True, text=True, check=False,
            )
            if not result.stdout.strip():
                result = subprocess.run(
                    ["wmic", "process", "where", f"ProcessId={pid}",
                     "get", "CommandLine"],
                    capture_output=True, text=True, check=False,
                )
        else:
            result = subprocess.run(
                ["ps", "-p", str(pid), "-o", "args="],
                capture_output=True, text=True, check=False,
            )
        return " ".join(result.stdout.split())
    except (OSError, subprocess.SubprocessError):
        return ""


def describe_conflict(port: int) -> str:
    """Explain who holds a port. Never terminates the owner."""
    pids = pids_on_port(port)
    lines = [f"Port {port} is already in use."]

    if not pids:
        lines.append(
            "  Could not identify the owning process (lsof/netstat unavailable)."
        )
        return "\n".join(lines)

    for pid in pids:
        command = process_command_line(pid)
        lines.append(f"  PID {pid}: {command or '<command unavailable>'}")

    lines.append("")
    lines.append("  Stop it yourself if it is not needed, or pick another port.")
    lines.append("  This script will not terminate other processes.")
    return "\n".join(lines)


def is_port_forward_process(command_line: str) -> bool:
    """True only for a kubectl port-forward command."""
    if not command_line:
        return False
    normalized = command_line.lower()
    return "kubectl" in normalized and "port-forward" in normalized


def load_forwards(state_file: Path | None = None) -> list[dict]:
    """Previously recorded port-forward processes."""
    path = state_file or STATE_FILE
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def save_forwards(forwards: list[dict], state_file: Path | None = None) -> None:
    """Record port-forward PIDs so we can stop exactly those later."""
    path = state_file or STATE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(forwards, indent=2))


def forget_forward(pid: int, state_file: Path | None = None) -> None:
    """Drop a single entry from the state file."""
    remaining = [entry for entry in load_forwards(state_file) if entry.get("pid") != pid]
    save_forwards(remaining, state_file)


def terminate_pid(pid: int) -> bool:
    """Stop one PID, politely first.

    Only ever called for PIDs recorded by this project and re-verified as
    kubectl port-forward processes. Returns whether the process is gone, not
    merely whether the signal was sent.
    """
    if is_windows():
        result = subprocess.run(
            ["taskkill", "/PID", str(pid)], capture_output=True, check=False
        )
        if result.returncode != 0:
            return False
    else:
        try:
            os.kill(pid, 15)  # SIGTERM, so the process can clean up
        except (ProcessLookupError, PermissionError):
            return False

    # Give it a moment, then confirm it actually exited.
    for _ in range(10):
        if not _pid_alive(pid):
            return True
        time.sleep(0.2)
    return not _pid_alive(pid)


def _pid_alive(pid: int) -> bool:
    if is_windows():
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, text=True, check=False,
        )
        return str(pid) in result.stdout

    # A terminated child stays a zombie until the parent reaps it, and
    # os.kill(pid, 0) still succeeds on a zombie — so read the process state.
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        stat = ""
    if stat:
        # "pid (comm) S ..." — comm may contain spaces or parentheses.
        state = stat.rpartition(")")[2].split()
        if state and state[0] == "Z":
            return False
        return True

    try:
        os.kill(pid, 0)  # signal 0 = existence check only
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True