"""Execute the shipped examples so copied test fixtures cannot mask failures."""

import ast
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def example(name):
    result = subprocess.run(
        [sys.executable, str(ROOT / 'roadc.py'), 'run', str(ROOT / 'examples' / name)],
        cwd=ROOT, capture_output=True, text=True, timeout=5,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    return result.stdout


def test_route_action_example_emits_complete_envelopes():
    requests = [ast.literal_eval(line) for line in example('route_actions.road').splitlines()]
    assert len(requests) == 2
    for request, verb in zip(requests, ['status', 'ask']):
        assert request['version'] == 'road-action/0.1'
        assert request['action'] == verb
        assert request['requires'] == [verb]
        assert request['authority'] == {'mode': 'self', 'scope': 'road://self'}
        assert request['provenance'] == {'source': 'examples/route_actions.road'}
    assert requests[0]['target'] == 'road://self/devices/octavia'
    assert requests[1]['input'] == {'prompt': 'summarize the current state'}


def test_object_example_runs_permission_aware_dispatch():
    output = example('road_objects.road')
    assert 'fleet: 3' in output
    assert 'start lucidia: started' in output
    assert 'lucidia status: online' in output
    assert 'start alexandria: permission denied' in output
