# NATS for roadc

This repository participates as `roadc` in the shared RoadOS NATS transport.
Keep a current `RoadOS` checkout beside this repository, or explicitly set
`ROAD_BUS_ROOT` to its absolute path. The implementation is maintained in one place.

```bash
python3 nats_bus.py status
python3 nats_bus.py enqueue README.md
```

These commands work offline without the NATS client dependency. `enqueue` stores
only a SHA-256 fingerprint and size of the explicitly selected file in a durable
local outbox. Neither command contacts a broker or runs the file.

Install the optional client with `python3 -m pip install -r ../RoadOS/requirements-nats.txt`.
Configure a broker using the [shared setup guide](https://github.com/blackboxprogramming/RoadOS/blob/main/NATS.md).
Then enable the connection explicitly:

```bash
export ROAD_NATS_ENABLED=1
export NATS_URL=nats://127.0.0.1:4222
python3 nats_bus.py flush
python3 nats_bus.py publish README.md
python3 nats_bus.py receive --component roados --consumer roadc-observations --batch 1
```

For a receipt file written by your running service, start a sidecar with an
explicit path (replace the example with your actual file):

```bash
python3 nats_bus.py relay /absolute/path/to/receipt.json --kind receipt
```

The relay polls every two seconds, queues changed content, and retries delivery.
It does not start automatically with the application. A receipt kind is a label;
the notification does not verify the receipt's semantic content or hash chain.
Only selected file hashes and sizes cross the bus. File contents and local paths
are never put into these events. Source files are limited to 16 MiB.

Subject: `road.v1.roadc.<kind>`, where kind is `artifact`, `receipt`, `handoff`,
or `completion`. The matching Route is
`road://components/roadc/events/<kind>`.

A JetStream acknowledgment means the broker accepted an event. It is not proof
that a Roadie accepted work or that execution occurred. Consumers persist events
locally and never execute messages. See the shared guide for TLS/authentication,
retry semantics, state limits, and rollback.
