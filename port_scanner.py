#!/usr/bin/env python3
"""Small TCP connect scanner for loopback and private lab addresses."""

import argparse
import ipaddress
import socket
import time


def parse_ports(value: str) -> range:
    try:
        start_text, end_text = value.split("-", 1)
        start, end = int(start_text), int(end_text)
    except (ValueError, TypeError):
        raise argparse.ArgumentTypeError("ports must use START-END format, e.g. 1-1024")
    if not (1 <= start <= end <= 65535):
        raise argparse.ArgumentTypeError("ports must be between 1 and 65535")
    if end - start > 4095:
        raise argparse.ArgumentTypeError("select at most 4096 ports per run")
    return range(start, end + 1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="IPv4 or IPv6 address in your own lab")
    parser.add_argument("--ports", type=parse_ports, default=parse_ports("1-1024"))
    parser.add_argument("--timeout", type=float, default=0.35)
    parser.add_argument("--delay", type=float, default=0.01)
    args = parser.parse_args()

    try:
        address = ipaddress.ip_address(args.target)
    except ValueError:
        parser.error("provide an IP address; hostnames are not resolved")
    if not (address.is_private or address.is_loopback):
        parser.error("scope is limited to loopback and private lab addresses")
    if args.timeout <= 0 or args.delay < 0:
        parser.error("timeout must be positive and delay cannot be negative")

    print(f"Scanning {address} across {len(args.ports)} TCP ports")
    for port in args.ports:
        try:
            with socket.create_connection((str(address), port), timeout=args.timeout):
                try:
                    service = socket.getservbyport(port, "tcp")
                except OSError:
                    service = "unknown"
                print(f"{port}/tcp open ({service})")
        except (TimeoutError, ConnectionRefusedError, OSError):
            pass
        if args.delay:
            time.sleep(args.delay)


if __name__ == "__main__":
    main()
