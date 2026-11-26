# Port Scanner

A small Python TCP connect scanner for **loopback and private lab IP addresses**. It reports ports that accepted a connection and maps common port numbers to the local service-name database.

**Author:** Jason Santos Ritchie

**Stage:** Prototype with human-readable and JSON output.

## Scope and safety

The tool accepts IP addresses only, rejects public addresses, and limits each run to 4,096 ports. Use it only on systems you own or have explicit permission to assess.

## Requirements

- Python 3.10 or newer
- No third-party packages

## Usage

    python3 port_scanner.py 127.0.0.1 --ports 1-1024

For a private lab host:

    python3 port_scanner.py 192.168.1.20 --ports 1-256 --timeout 0.4 --delay 0.02

Add `--json` to print a structured report that can be saved or piped into another local tool:

    python3 port_scanner.py 127.0.0.1 --ports 1-1024 --json

The JSON report includes the target, number of ports scanned, and open ports with their protocol and service label.

## Smoke checks

- Scanned 127.0.0.1 ports 1-32.
- Confirmed a public address is rejected before a connection is attempted.

## Current limits

This is a basic TCP connect scan. It does not identify software versions, perform UDP scanning, or guarantee that a closed or filtered port can be distinguished. The service label comes from the machine’s local service-name database.

## Lessons and next steps

The scanner keeps its scope explicit and port ranges bounded. Structured output makes local result handling easier; next steps include clearer timeout reporting and documenting results from an authorised local lab.

## Demo screenshot

![Loopback port scanner demo](screenshots/port-scanner-demo.png)

This run scanned five ports on 127.0.0.1 while a temporary local HTTP service listened on port 8765.
