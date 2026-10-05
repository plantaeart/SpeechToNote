"""Tests for the cross-platform helpers in scripts/kubernetes/start.py."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kubernetes"))

from start import get_host_data_dir  # noqa: E402


def test_env_override_wins(monkeypatch):
    monkeypatch.setenv("SPEECHTONOTE_DATA_DIR", "/somewhere/else")
    assert get_host_data_dir() == "/somewhere/else"


def test_linux_and_macos_use_tmp(monkeypatch):
    monkeypatch.delenv("SPEECHTONOTE_DATA_DIR", raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    assert get_host_data_dir() == "/tmp/speechtonote-mongo-data"


def test_windows_path_has_no_windows_default_on_posix(monkeypatch):
    """On POSIX the result must never be a Windows path like C:\\temp\\..."""
    monkeypatch.delenv("SPEECHTONOTE_DATA_DIR", raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    result = get_host_data_dir()
    assert "C:" not in result
    assert "\\" not in result


def test_windows_uses_temp_env(monkeypatch):
    monkeypatch.delenv("SPEECHTONOTE_DATA_DIR", raising=False)
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("TEMP", r"C:\Users\dev\AppData\Local\Temp")
    result = get_host_data_dir()
    assert result.startswith(r"C:\Users\dev\AppData\Local\Temp")
    assert result.endswith("speechtonote-mongo-data")


def test_kind_config_hostpath_matches_helper(monkeypatch):
    """The bind mount in kind-config.yaml must match what start.py creates."""
    monkeypatch.delenv("SPEECHTONOTE_DATA_DIR", raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    config = (
        Path(__file__).resolve().parents[2] / "manifests" / "kind-config.yaml"
    ).read_text()
    assert get_host_data_dir() in config, (
        "kind-config.yaml hostPath must match get_host_data_dir(); "
        "otherwise the MongoDB volume silently stays empty."
    )