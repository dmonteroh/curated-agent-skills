# Layer checks

Runnable pattern checks for layers 1–5. Standard library only (`re`, `ipaddress`, `collections`). Verify a check by running it against a candidate that is known to contain the fault and confirming the line number it returns points at the offending line — not by confirming it returned a list.

**One block-parsing convention.** Every section-scoped check below goes through `iter_blocks`. Ad-hoc "remember the last header I saw" tracking is the defect this file exists to avoid: it never learns that a block ended, so a line at global scope is attributed to the last interface seen dozens of lines earlier, and the finding points at the wrong object. If a check needs config structure, it gets a block.

```python
import ipaddress
import re
from collections import Counter


def iter_blocks(config: str, starts_with: str) -> list[list[str]]:
    """Yield each block as its lines, starting at `starts_with` and ending at
    the next non-indented line. Blocks carry (line_number, text) pairs so every
    finding can name a location."""
    blocks: list[list[str]] = []
    current: list[tuple[int, str]] = []
    for number, line in enumerate(config.splitlines(), start=1):
        if line.startswith(starts_with):
            if current:
                blocks.append(current)
            current = [(number, line)]
            continue
        if current:
            if line and not line.startswith((" ", "\t")):
                blocks.append(current)
                current = []
            else:
                current.append((number, line))
    if current:
        blocks.append(current)
    return blocks
```

## Layer 1 — destructive commands

```python
DESTRUCTIVE = [
    (re.compile(r"\breload\b", re.I), "reload causes downtime"),
    (re.compile(r"\berase\s+(startup|nvram|flash)", re.I), "erases persistent storage"),
    (re.compile(r"\bformat\b", re.I), "formats a device filesystem"),
    (re.compile(r"\bno\s+router\s+(bgp|ospf|eigrp|isis)\b", re.I), "removes a routing process"),
    (re.compile(r"\bno\s+interface\s+\S+", re.I), "removes interface configuration"),
    (re.compile(r"\baaa\s+new-model\b", re.I), "changes authentication behavior"),
    (re.compile(r"\bcrypto\s+key\s+(zeroize|generate)\b", re.I), "changes device SSH keys"),
]


def find_destructive(config: str) -> list[dict[str, object]]:
    findings = []
    for number, line in enumerate(config.splitlines(), start=1):
        stripped = line.strip()
        for pattern, reason in DESTRUCTIVE:
            if pattern.search(stripped):
                findings.append({"layer": 1, "line": number,
                                 "text": stripped, "reason": reason})
                break  # one finding per line: the first match is the reason
    return findings
```

## Layer 2 — credentials and management plane

Patterns are ordered most-specific first and **only the first match on a line is reported**. Without that rule a default community string matches both the "default community" pattern and the broader "v2c is in use" pattern, and one line produces two findings — inflating the blocker count and making the reviewer distrust the gate.

```python
CREDENTIAL = [
    (re.compile(r"\bsnmp-server community\s+(public|private)\b", re.I),
     "default SNMP community configured"),
    (re.compile(r"\bsnmp-server community\s+\S+", re.I),
     "SNMPv2c community string configured; prefer SNMPv3 authPriv"),
    (re.compile(r"\bip ssh version 1\b", re.I), "SSH version 1 enabled"),
    (re.compile(r"\benable password\b", re.I),
     "enable password present; use enable secret"),
    (re.compile(r"\busername\s+\S+\s+password\b", re.I),
     "local username uses password instead of secret"),
]


def find_credential_exposure(config: str) -> list[dict[str, object]]:
    findings = []
    for number, line in enumerate(config.splitlines(), start=1):
        for pattern, reason in CREDENTIAL:
            if pattern.search(line):
                findings.append({"layer": 2, "line": number,
                                 "text": line.strip(), "reason": reason})
                break
    return findings


def check_vty(config: str) -> list[dict[str, object]]:
    findings = []
    for block in iter_blocks(config, "line vty"):
        start, header = block[0]
        text = "\n".join(line for _, line in block)
        if re.search(r"transport\s+input\s+.*telnet", text, re.I):
            findings.append({"layer": 2, "line": start, "text": header.strip(),
                             "reason": "VTY allows Telnet; require SSH only"})
        if not re.search(r"\baccess-class\s+\S+\s+in\b", text, re.I):
            findings.append({"layer": 2, "line": start, "text": header.strip(),
                             "reason": "VTY has no inbound access-class restriction"})
        if not re.search(r"\bexec-timeout\s+\d+\s+\d+\b", text, re.I):
            findings.append({"layer": 2, "line": start, "text": header.strip(),
                             "reason": "VTY has no explicit exec-timeout"})
    return findings
```

## Layer 3 — address collisions

Built on `iter_blocks`, so an `ip address` line at global scope belongs to no interface and is not silently attributed to the previous one.

```python
IP_ADDRESS_RE = re.compile(
    r"^\s*ip address\s+(?P<ip>\d{1,3}(?:\.\d{1,3}){3})"
    r"\s+(?P<mask>\d{1,3}(?:\.\d{1,3}){3})\b", re.I)


def extract_interfaces(config: str) -> list[dict[str, object]]:
    results = []
    for block in iter_blocks(config, "interface "):
        _, header = block[0]
        name = header.split(maxsplit=1)[1].strip()
        for number, line in block[1:]:
            match = IP_ADDRESS_RE.match(line)
            if not match:
                continue
            network = ipaddress.ip_interface(
                f"{match.group('ip')}/{match.group('mask')}").network
            results.append({"interface": name, "line": number,
                            "ip": match.group("ip"), "network": network})
    return results


def find_address_collisions(config: str) -> list[dict[str, object]]:
    entries = extract_interfaces(config)
    findings = []
    counts = Counter(entry["ip"] for entry in entries)
    for entry in entries:
        if counts[entry["ip"]] > 1:
            findings.append({"layer": 3, "line": entry["line"], "text": entry["ip"],
                             "reason": f"duplicate address on {entry['interface']}"})
    for index, left in enumerate(entries):
        for right in entries[index + 1:]:
            if left["network"].overlaps(right["network"]):
                findings.append({
                    "layer": 3, "line": right["line"], "text": str(right["network"]),
                    "reason": f"overlaps {left['network']} on {left['interface']}"})
    return findings
```

## Layer 4 — stale references

A referenced-but-undefined filter is a device that permits what it was meant to deny. Definitions and references live in different syntax, so both sides are collected before comparing.

```python
DEFINITIONS = [
    (re.compile(r"^ip access-list\s+\S+\s+(?P<name>\S+)", re.I), "acl"),
    (re.compile(r"^access-list\s+(?P<name>\d+)\b", re.I), "acl"),
    (re.compile(r"^route-map\s+(?P<name>\S+)", re.I), "route-map"),
    (re.compile(r"^ip prefix-list\s+(?P<name>\S+)", re.I), "prefix-list"),
]
REFERENCES = [
    (re.compile(r"\bip access-group\s+(?P<name>\S+)\s+(in|out)\b", re.I), "acl"),
    (re.compile(r"\baccess-class\s+(?P<name>\S+)\s+(in|out)\b", re.I), "acl"),
    (re.compile(r"\broute-map\s+(?P<name>\S+)", re.I), "route-map"),
    (re.compile(r"\bprefix-list\s+(?P<name>\S+)", re.I), "prefix-list"),
]


def find_stale_references(config: str) -> list[dict[str, object]]:
    defined = set()
    for line in config.splitlines():
        for pattern, kind in DEFINITIONS:
            match = pattern.match(line.strip())
            if match:
                defined.add((kind, match.group("name")))
    findings = []
    for number, line in enumerate(config.splitlines(), start=1):
        for pattern, kind in REFERENCES:
            match = pattern.search(line)
            if match and (kind, match.group("name")) not in defined:
                findings.append({
                    "layer": 4, "line": number, "text": line.strip(),
                    "reason": f"{kind} '{match.group('name')}' referenced but not defined"})
    return findings
```

A finding here is only as good as the config it was given. If the candidate is a fragment that will merge into an existing running config, the definitions may exist on the device — pass the merged result, or record in the output contract that layer 4 ran against a fragment.

## Layer 5 — hygiene, warn only

```python
HYGIENE = [
    (re.compile(r"\bntp server\b", re.I), "NTP server"),
    (re.compile(r"\bservice timestamps\b", re.I), "log timestamps"),
    (re.compile(r"\blogging host\b|\blogging\s+\d{1,3}(\.\d{1,3}){3}", re.I),
     "remote logging destination"),
    (re.compile(r"\bsnmp-server group\s+\S+\s+v3\s+priv\b", re.I), "SNMPv3 authPriv group"),
    (re.compile(r"\bbanner\s+(login|motd)\b", re.I), "login banner"),
]


def find_hygiene_gaps(config: str) -> list[dict[str, object]]:
    return [{"layer": 5, "line": None, "text": None,
             "reason": f"missing {description}"}
            for pattern, description in HYGIENE if not pattern.search(config)]
```

These carry no line number by construction — an absence has no location. That is also why they warn rather than block: a fragment under review legitimately lacks global configuration that the device already has.

## Composing the verdict

```python
def review(config: str) -> dict[str, object]:
    blocking = (find_destructive(config) + find_credential_exposure(config)
                + check_vty(config) + find_address_collisions(config)
                + find_stale_references(config))
    warnings = find_hygiene_gaps(config)
    return {
        "verdict": "blocked" if blocking else "cleared to proceed",
        "blocking": sorted(blocking, key=lambda f: (f["layer"], f["line"] or 0)),
        "warnings": warnings,
    }
```

`cleared to proceed` from this function means the pattern layer found nothing. It does not mean the change is safe, and the output contract requires saying which constructs went unchecked.
