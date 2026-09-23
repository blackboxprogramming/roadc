"""Opt-in runtime receipt integration with an explicitly trusted RoadOS checkout."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


pytestmark = pytest.mark.skipif(
    not os.environ.get("ROAD_TEST_ROADOS"),
    reason="set ROAD_TEST_ROADOS to a trusted RoadOS checkout",
)
RUNTIME = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("source,status,output,error", [
    ('let transform = map\nprint(transform(int, ["2", "3"]))\n'
     'print(filter(bool, [0, 4]))\n', "completed", "[2, 3]\n[4]\n", ""),
    ('let transform = map\nfun values():\n    print("MUST NOT RUN")\n'
     '    return [1]\ntransform(len, values(), values())\n',
     "failed", "", "len: expected"),
    ('type Device:\n    permissions: set[string]\n'
     'let device = Device{permissions: {"read",},}\n'
     'print("read" in device.permissions,)\n'
     'print(3 < 2 < missing())\nprint(6 & 3)\nprint(-2 ** 2)\n',
     "completed", "True\nFalse\n2\n-4\n", ""),
    ('let = 1\n', "failed", "", "Expected IDENTIFIER"),
    ('async fun task():\n    print("MUST NOT RUN")\ntask()\n',
     "failed", "", "Unsupported async function"),
    ('print("before")\nlet result = 1 / 0\nprint("after")\n',
     "failed", "before\n", "division by zero"),
])
def test_runtime_produces_verified_workspace_receipts(tmp_path, source, status, output, error):
    workspace = Path(os.environ["ROAD_TEST_ROADOS"]).resolve() / "workspace.py"
    (tmp_path / "main.road").write_text(source, encoding="utf-8")
    project = tmp_path / "road.json"
    project.write_text(json.dumps({
        "schema": "road-project/v1", "name": "builtin-callback-integration",
        "route": "/road/projects/builtin-callback-integration",
        "runtime": "roadc-python", "entrypoint": "main.road",
    }))
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"schema": "roadies-catalog/v1", "roadies": [{
        "agent_id": "cordelia", "name": "Cordelia", "route": "/roadies/cordelia",
        "brain_id": None, "allowed_tools": [], "preferred_ramp": "local",
    }]}))
    result = subprocess.run([
        sys.executable, str(workspace), "run", "--project", str(project),
        "--catalog", str(catalog), "--roadc", str(RUNTIME), "--roadie", "cordelia",
        "--allow-code", "--receipts", str(tmp_path / "receipts"), "--timeout", "5",
    ], capture_output=True, text=True, timeout=15)
    assert result.returncode == (0 if status == "completed" else 1), result.stderr
    summary = json.loads(result.stdout)
    receipt_path = Path(summary["receipt"])
    receipt = json.loads(receipt_path.read_text())
    assert receipt["status"] == status
    assert receipt["stdout"]["text"] == output
    if error:
        assert error in receipt["stderr"]["text"]
    else:
        assert receipt["stderr"]["text"] == ""
    assert receipt["context"]["provider_connection"] == "not-requested"
    verified = subprocess.run([
        sys.executable, str(workspace), "verify", str(receipt_path),
    ], capture_output=True, text=True, timeout=10)
    assert verified.returncode == 0, verified.stderr
    assert json.loads(verified.stdout)["ok"] is True
