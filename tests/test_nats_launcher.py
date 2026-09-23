"""Check the real shared adapter only when a trusted checkout is selected."""

import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]


def invoke(bus_root, state, *args):
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("NATS_", "ROAD_NATS_"))}
    env.update(ROAD_BUS_ROOT=str(bus_root), ROAD_NATS_ENABLED="0")
    return subprocess.run(
        [sys.executable, str(ROOT / "nats_bus.py"), "--state", str(state), *map(str, args)],
        env=env, capture_output=True, text=True, timeout=5,
    )


def test_missing_shared_adapter_has_actionable_error(tmp_path):
    state = tmp_path / "state"
    result = invoke(tmp_path / "missing", state, "status")
    assert result.returncode == 2
    assert "ROAD_BUS_ROOT" in result.stderr
    assert "Traceback" not in result.stderr
    assert not state.exists()


@pytest.fixture
def bus_root():
    selected = os.environ.get("ROAD_TEST_BUS_ROOT")
    if not selected:
        pytest.skip("Set ROAD_TEST_BUS_ROOT to a trusted RoadOS checkout")
    root = Path(selected).resolve()
    assert (root / "road_bus" / "cli.py").is_file()
    return root


def test_status_stays_offline_and_creates_no_state(bus_root, tmp_path):
    state = tmp_path / "state"
    result = invoke(bus_root, state, "status")
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["component"] == "roadc"
    assert report["enabled"] is False
    assert report["connection"] == "not-tested"
    assert report["execution"] == "not-requested"
    assert not state.exists()


def test_queue_fingerprints_deduplicate_without_source_content(bus_root, tmp_path):
    state = tmp_path / "state"
    source = tmp_path / "private-receipt.json"
    content = b'{"private_marker":"not-for-transport"}'
    source.write_bytes(content)
    first = invoke(bus_root, state, "enqueue", source, "--kind", "receipt")
    second = invoke(bus_root, state, "enqueue", source, "--kind", "receipt")
    assert first.returncode == second.returncode == 0
    assert json.loads(first.stdout)["inserted"] is True
    assert json.loads(second.stdout)["inserted"] is False
    with sqlite3.connect(state / "roadc.sqlite3") as db:
        rows = db.execute("SELECT event, delivered_at FROM outbox").fetchall()
    assert len(rows) == 1
    raw, delivered = rows[0]
    event = json.loads(raw)
    assert event["sha256"] == hashlib.sha256(content).hexdigest()
    assert event["size"] == len(content)
    assert event["route"] == "road://components/roadc/events/receipt"
    assert event["execution"] == "not-requested"
    assert delivered is None
    assert content not in raw
    assert b"private_marker" not in raw
    assert str(source).encode() not in raw


@pytest.mark.parametrize("command", ["publish", "flush"])
def test_network_commands_require_opt_in_before_state_creation(bus_root, tmp_path, command):
    state = tmp_path / "state"
    args = [command, tmp_path / "missing"] if command == "publish" else [command]
    result = invoke(bus_root, state, *args)
    assert result.returncode == 1
    assert "NATS is disabled" in json.loads(result.stdout)["error"]
    assert not state.exists()
