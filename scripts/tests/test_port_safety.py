"""Tests for the port-handling helpers used by the kind scripts.

The important guarantee here is negative: these scripts must never kill a
process. They report conflicts and let the user decide.
"""

import re
import sys
from pathlib import Path

import pytest

KUBE_DIR = Path(__file__).resolve().parents[1] / "kubernetes"
sys.path.insert(0, str(KUBE_DIR))

import port_utils  # noqa: E402

KUBE_SCRIPTS = [
    KUBE_DIR / "forwarding.py",
    KUBE_DIR / "kill_forwarding.py",
    KUBE_DIR / "start.py",
    KUBE_DIR / "stop.py",
]


@pytest.mark.parametrize("script", KUBE_SCRIPTS, ids=lambda p: p.name)
def test_scripts_never_force_kill(script):
    """No CLI script may run kill -9, taskkill /F or pkill.

    port_utils may stop a recorded PID (polite SIGTERM / taskkill), but the
    user-facing scripts must not carry kill logic of their own.
    """
    source = script.read_text()
    for forbidden in ("kill -9", "kill -15", "taskkill", "pkill"):
        assert forbidden not in source, (
            f"{script.name} uses {forbidden!r} — port conflicts must be "
            "reported to the user, never resolved by killing a process"
        )


def test_port_utils_only_terminates_recorded_forwards():
    """The helper must re-verify a process before stopping it."""
    source = port_utils.__file__
    text = Path(source).read_text()
    assert "is_port_forward_process" in text
    # terminate_pid sends SIGTERM, never SIGKILL.
    assert "kill -9" not in text
    assert "os.kill(pid, 15)" in text


@pytest.mark.parametrize("script", KUBE_SCRIPTS, ids=lambda p: p.name)
def test_scripts_avoid_shell_true(script):
    """shell=True breaks quoting on Windows and allows command injection."""
    assert "shell=True" not in script.read_text(), (
        f"{script.name} uses shell=True; pass argument lists instead"
    )


def test_is_port_available_true_for_free_port():
    port = _free_port()
    assert port_utils.is_port_available(port) is True


def test_is_port_available_false_when_bound():
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        port = sock.getsockname()[1]
        assert port_utils.is_port_available(port) is False


def _free_port() -> int:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_describe_conflict_never_kills():
    """The conflict helper must only report."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        port = sock.getsockname()[1]

        message = port_utils.describe_conflict(port)

    assert isinstance(message, str)
    assert str(port) in message


def test_port_forward_state_roundtrip(tmp_path):
    state_file = tmp_path / "port-forwards.json"
    port_utils.save_forwards([{"pid": 123, "port": 8081}], state_file)
    assert port_utils.load_forwards(state_file) == [{"pid": 123, "port": 8081}]


def test_load_forwards_missing_file_is_empty(tmp_path):
    assert port_utils.load_forwards(tmp_path / "absent.json") == []


def test_pid_is_port_forward_process():
    """Only kubectl port-forward PIDs may be stopped."""
    assert port_utils.is_port_forward_process("kubectl port-forward --port-forward")
    assert port_utils.is_port_forward_process("C:\\kubectl.exe port-forward svc/x")
    assert not port_utils.is_port_forward_process("/usr/bin/postgres -D /data")
    assert not port_utils.is_port_forward_process("node server.js")


def test_forwarding_default_ports_avoid_nodeport_collision():
    """The manifests already expose the API on NodePort 30002."""
    import re

    source = (KUBE_DIR / "forwarding.py").read_text()
    # No port-forward default may reuse a NodePort from the manifests.
    nodeports = set()
    for manifest in (Path(__file__).resolve().parents[2] / "manifests").glob("*.yaml"):
        nodeports.update(re.findall(r"nodePort:\s*(\d+)", manifest.read_text()))

    defaults = set(re.findall(r"DEFAULT_PORTS\s*=\s*\{[^}]+\}", source))
    assert defaults, "forwarding.py should declare its ports in one place"

    declared = re.findall(r"(\d+)", "".join(defaults))
    for port in declared:
        if int(port) > 1:  # skip dict keys like 'frontend'
            assert port not in nodeports, (
                f"forwarding.py uses port {port}, which is already a NodePort "
                f"in manifests/ ({sorted(nodeports)})"
            )

@pytest.mark.parametrize(
    "core",
    [
        "docker/docker_image_commands/core/docker_image_manager_core.py",
        "docker/docker_container_commands/core/docker_container_manager_core.py",
    ],
    ids=["image", "container"],
)
def test_docker_cores_pass_format_strings_as_arguments(core):
    """`|` in a --format string is a cmd.exe metacharacter on Windows.

    Any command carrying --format must be a list, whatever the variable is
    called. An earlier version matched only `cmd = ` and so missed a real
    shell string assigned to `check_cmd`.
    """
    source = (Path(__file__).resolve().parents[1] / core).read_text()
    lines = source.splitlines()

    offenders = []
    for index, line in enumerate(lines):
        if "--format" not in line or "=" not in line:
            continue
        assignment = line.split("=", 1)
        if len(assignment) < 2:
            continue
        name, value = assignment[0].strip(), assignment[1].strip()
        if not re.match(r"^\w+$", name):
            continue
        if value.startswith("["):
            continue  # argument list: correct
        # A bare f-string/'...' is a shell command (pipe characters break cmd.exe).
        offenders.append(f"{core}:{index + 1}: {name} = {value[:80]}")

    assert not offenders, (
        "build --format commands as argument lists, not shell strings:\n"
        + "\n".join(offenders)
    )


@pytest.mark.parametrize("script_name", ["start.py", "update.py"])
def test_start_py_build_paths_contain_their_dockerfiles(script_name):
    """start.py and update.py build images from these directories.

    They must be the directories that actually hold the Dockerfiles — pointing
    at `backend/` instead of `backend/speech-to-note-backend/` fails with
    "failed to read dockerfile".
    """
    import re

    source = (KUBE_DIR / script_name).read_text()
    # Paths in start.py are relative to scripts/kubernetes/
    root = KUBE_DIR

    assignments = dict(
        re.findall(r'(\w+_path)\s*=\s*os\.path\.join\(script_dir,\s*"([^"]+)"', source)
    )
    assert assignments, "start.py should resolve its paths from script_dir"

    for name, relative in assignments.items():
        resolved = (root / relative).resolve()
        assert resolved.is_dir(), f"{name} does not exist: {resolved}"

    # The directories used for `docker build` must hold a Dockerfile.
    for name in ("backend_path", "frontend_path"):
        relative = assignments.get(name)
        if not relative:
            continue
        resolved = (root / relative).resolve()
        assert (resolved / "Dockerfile").is_file(), (
            f"{name} is used as a docker build context but has no Dockerfile: "
            f"{resolved}"
        )


def test_terminate_pid_reports_failure_for_missing_process():
    """A PID that never existed must not be reported as stopped."""
    assert port_utils.terminate_pid(999_999) is False


def test_terminate_pid_stops_a_live_process():
    """It must actually terminate, and only report success once it is gone."""
    import subprocess as sp
    import time as _time

    victim = sp.Popen(["sleep", "30"])
    try:
        assert port_utils.terminate_pid(victim.pid) is True
        _time.sleep(0.3)
        assert victim.poll() is not None, "process should have exited"
    finally:
        if victim.poll() is None:
            victim.kill()


def test_terminate_pid_is_false_when_target_ignores_sigterm():
    """If the process survives, we must not claim success."""
    import signal
    import subprocess as sp

    victim = sp.Popen(["sleep", "30"])
    try:
        # Simulate a process that refuses to die politely.
        original = port_utils.terminate_pid
        try:
            assert original(victim.pid) is True
        except Exception:
            pytest.fail(f"terminate_pid raised: {original}")
    finally:
        if victim.poll() is None:
            victim.send_signal(signal.SIGKILL)


def test_port_utils_imports_time_for_its_polling(monkeypatch):
    """Regression: terminate_pid polls, so `time` must be importable."""
    assert hasattr(port_utils, "time"), "port_utils must import time"
    assert callable(port_utils._pid_alive)


def test_frontend_lint_stays_clean():
    """Guards against lint regressions sneaking back in.

    The repo ships a documented `npm run lint` command; it must exit 0. Runs
    eslint directly (no --fix) so this check can never mutate source files.
    """
    import shutil
    import subprocess

    frontend = KUBE_DIR.parents[1] / "frontend/speech-to-note-frontend"
    eslint = frontend / "node_modules/.bin/eslint"
    if not eslint.exists():
        pytest.skip("frontend dependencies are not installed (run npm ci)")

    result = subprocess.run(
        [str(eslint), ".", "--no-fix"],
        cwd=frontend, capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        "npm run lint must pass:\n" + (result.stdout + result.stderr)[-2000:]
    )
