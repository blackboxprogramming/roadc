#!/usr/bin/env python3
"""Run this component's shared RoadOS NATS adapter."""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
BUS_ROOT = Path(os.environ.get("ROAD_BUS_ROOT", str(ROOT.parent / "RoadOS"))).resolve()
if not (BUS_ROOT / "road_bus" / "cli.py").is_file():
    print("NATS adapter needs the sibling RoadOS checkout or ROAD_BUS_ROOT", file=sys.stderr)
    raise SystemExit(2)
sys.path.insert(0, str(BUS_ROOT))
from road_bus.cli import main

if __name__ == "__main__":
    raise SystemExit(main(ROOT / "nats-component.json"))
