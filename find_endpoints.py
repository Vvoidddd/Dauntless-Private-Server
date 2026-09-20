"""Find stricter URL, host, IP, and known-service candidates in a binary."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from extract_endpoints import classify
from extract_strings import printable_strings

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path, help="binary file to inspect")
    parser.add_argument("--max-results", type=int, default=500, help="maximum total unique results")
    parser.add_argument("--max-length", type=int, default=300)
    parser.add_argument("--chunk-size", type=int, default=1024 * 1024)
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    if not args.binary.is_file():
        print(f"error: file not found: {args.binary}", file=sys.stderr)
        return 2
    if min(args.max_results, args.max_length, args.chunk_size) < 1:
        print("error: limits must be positive", file=sys.stderr)
        return 2
    results: set[tuple[str, str]] = set()
    try:
        for value in printable_strings(args.binary, 4, args.chunk_size):
            if len(value) > args.max_length:
                continue
            category = classify(value)
            if category in {"URLs", "IP addresses", "Host names"} or (category == "Service keywords" and any(k in value.lower() for k in ("playfab", "graphql", "dauntless", "archon"))):
                results.add((category or "Other", value))
                if len(results) >= args.max_results:
                    break
    except OSError as exc:
        print(f"error: could not read {args.binary}: {exc}", file=sys.stderr)
        return 1
    for category, value in sorted(results):
        print(f"[{category}] {value}")
    print(f"Found {len(results)} unique endpoint candidates.", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
