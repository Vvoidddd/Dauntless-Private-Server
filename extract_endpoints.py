"""Classify likely network endpoints found in printable binary strings."""
from __future__ import annotations
import argparse
import ipaddress
import re
import sys
from pathlib import Path
from extract_strings import printable_strings

URL = re.compile(r"^https?://\S+$", re.I)
HOST = re.compile(r"^(?:[a-z0-9-]+\.)+[a-z]{2,63}(?::\d{1,5})?$", re.I)
IP_PORT = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){3})(?::(\d{1,5}))?$")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path, help="binary file to inspect")
    parser.add_argument("--max-results", type=int, default=200, help="maximum unique results per category")
    parser.add_argument("--max-length", type=int, default=300)
    parser.add_argument("--chunk-size", type=int, default=1024 * 1024)
    return parser.parse_args()

def classify(value: str) -> str | None:
    if URL.fullmatch(value):
        return "URLs"
    match = IP_PORT.fullmatch(value)
    if match:
        try:
            ipaddress.ip_address(match.group(1))
            if match.group(2) is None or int(match.group(2)) <= 65535:
                return "IP addresses"
        except ValueError:
            pass
    if HOST.fullmatch(value):
        port = value.rpartition(":")[2] if ":" in value else None
        if port is None or int(port) <= 65535:
            return "Host names"
    if any(word in value.lower() for word in ("epic", "eos", "eac", "playfab", "sandbox", "prod-")):
        return "Service keywords"
    return None

def main() -> int:
    args = parse_args()
    if not args.binary.is_file():
        print(f"error: file not found: {args.binary}", file=sys.stderr)
        return 2
    if min(args.max_results, args.max_length, args.chunk_size) < 1:
        print("error: limits must be positive", file=sys.stderr)
        return 2
    found: dict[str, set[str]] = {}
    try:
        for value in printable_strings(args.binary, 4, args.chunk_size):
            if len(value) <= args.max_length and (category := classify(value)):
                bucket = found.setdefault(category, set())
                if len(bucket) < args.max_results:
                    bucket.add(value)
    except OSError as exc:
        print(f"error: could not read {args.binary}: {exc}", file=sys.stderr)
        return 1
    for category, values in found.items():
        print(f"\n=== {category.upper()} ({len(values)}) ===")
        print(*sorted(values), sep="\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
