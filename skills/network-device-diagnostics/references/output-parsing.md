# Parsing device output safely

Structured parsing makes a triage repeatable across captures. It also fails silently in ways that read as clean results, so every pattern here is paired with the failure it prevents. **Store the raw output alongside any parse.** Summary formats vary by platform, version, and address family, and a parse that silently matched nothing is indistinguishable from a device with nothing to report.

Requires only the Python standard library (`re`, `typing`). Verify a pattern by running it against a capture from the platform in front of you and checking that the row count matches what the device printed — not by checking that it returned without error.

## Slice blocks header to header

Do not use an arbitrary character window; large interface blocks can cause counters to be missed or assigned to the wrong port.

This is the rule that matters most in this file. A fixed-size window is correct on the test capture and wrong on the device with a busy uplink, and the symptom is a counter attributed to the neighbouring interface — a wrong answer, not an error.

## Session summary rows

The row shape is the discriminator, not the address format. Matching the neighbour column against a dotted quad restricts the parser to IPv4 unicast, which contradicts the first rule of the triage: do not assume the address family. Anchor on the *structure* — a non-space token followed by the fixed numeric columns — and IPv4, IPv6, VPNv4, and EVPN rows all parse.

```python
import re
from typing import Any

SUMMARY_ROW_RE = re.compile(
    r"^(?P<neighbor>\S+)\s+"
    r"(?P<version>\d+)\s+"
    r"(?P<remote_as>\d+)\s+"
    r"(?P<msg_rcvd>\d+)\s+"
    r"(?P<msg_sent>\d+)\s+"
    r"(?P<table_version>\d+)\s+"
    r"(?P<input_queue>\d+)\s+"
    r"(?P<output_queue>\d+)\s+"
    r"(?P<uptime>\S+)\s+"
    r"(?P<state_or_prefixes>\S+)\s*$",
    re.M,
)


def parse_summary(raw: str) -> list[dict[str, Any]]:
    rows = []
    for match in SUMMARY_ROW_RE.finditer(raw):
        tail = match.group("state_or_prefixes")
        # The final column is a received-prefix count when the session is
        # Established, and a state name otherwise. This is the only place the
        # state appears on the summary line.
        established = tail.isdigit()
        rows.append({
            "neighbor": match.group("neighbor"),
            "remote_as": int(match.group("remote_as")),
            "state": "Established" if established else tail,
            "prefixes_received": int(tail) if established else None,
            "uptime": match.group("uptime"),
        })
    return rows
```

A zero-row result on output that clearly contains sessions means the platform's column layout differs — read the raw capture and adjust, rather than reporting "no neighbours found".

## Interface counters

Input drops and output drops are reported in different places and mean different things, and the triage branches on exactly that split. A parser that captures one and labels it the other collapses the distinction the skill exists to preserve.

On IOS-style output, input drops appear inside the input-queue tuple (`size/max/drops/flushes`) and output drops on their own total line. Both are captured here.

```python
HEADER_RE = re.compile(
    r"^(?P<name>\S+) is (?P<status>(?:administratively )?down|up), "
    r"line protocol is (?P<protocol>up|down)",
    re.I | re.M,
)
INPUT_ERR_RE = re.compile(
    r"(?P<input_errors>\d+) input errors?, (?P<crc>\d+) CRC", re.I
)
RUNTS_RE = re.compile(r"(?P<runts>\d+) runts?, (?P<giants>\d+) giants?", re.I)
OUTPUT_ERR_RE = re.compile(
    r"(?P<output_errors>\d+) output errors?, (?P<collisions>\d+) collisions?", re.I
)
INPUT_DROP_RE = re.compile(r"Input queue: \d+/\d+/(?P<input_drops>\d+)/\d+", re.I)
OUTPUT_DROP_RE = re.compile(r"Total output drops: (?P<output_drops>\d+)", re.I)
DUPLEX_RE = re.compile(
    r"(?P<duplex>Full|Half|Auto)-duplex,\s+(?P<speed>[^,]+)", re.I
)


def parse_interfaces(raw: str) -> list[dict[str, Any]]:
    headers = list(HEADER_RE.finditer(raw))
    interfaces = []
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(raw)
        block = raw[header.start():end]
        record: dict[str, Any] = {
            "name": header.group("name"),
            "status": header.group("status"),
            "protocol": header.group("protocol"),
        }
        for pattern in (
            INPUT_ERR_RE, RUNTS_RE, OUTPUT_ERR_RE, INPUT_DROP_RE, OUTPUT_DROP_RE,
        ):
            match = pattern.search(block)
            # Absent counter stays None. Defaulting to 0 asserts the device
            # reported zero when it reported nothing, which reads as a clean
            # interface in the increment comparison.
            record.update(
                {k: (int(v) if match else None) for k, v in
                 (match.groupdict() if match else
                  dict.fromkeys(pattern.groupindex, None)).items()}
            )
        duplex = DUPLEX_RE.search(block)
        record["duplex"] = duplex.group("duplex") if duplex else None
        record["speed"] = duplex.group("speed").strip() if duplex else None
        interfaces.append(record)
    return interfaces
```

## Compare increments, never totals

Both parsers above return a snapshot. The triage compares two snapshots taken a stated interval apart:

```python
def deltas(before: dict[str, Any], after: dict[str, Any]) -> dict[str, int]:
    out = {}
    for key, new in after.items():
        old = before.get(key)
        # A None on either side means the counter was not reported in that
        # capture. Subtracting it as zero manufactures a delta.
        if isinstance(new, int) and isinstance(old, int):
            out[key] = new - old
    return out
```

A counter that went *down* between captures means it was cleared during the interval — the measurement is void, not negative.
