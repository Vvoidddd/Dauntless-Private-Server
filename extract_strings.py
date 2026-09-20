"""Extract bounded, network-related printable strings from a binary."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

DEFAULT_KEYWORDS = ("http", ".com", ".net", ".io", ".dev", ".org", "epicgames", "epiconline", "accounts", "api", "eac", "unrealengine", "localhost", ":7777", ":443", ":80", "prod-", "sandbox")

def printable_strings(path: Path, minimum: int, chunk_size: int):
    pending = bytearray()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            for value in chunk:
                if 0x20 <= value <= 0x7E:
                    pending.append(value)
                else:
                    if len(pending) >= minimum:
                        yield pending.decode("ascii")
                    pending.clear()
        if len(pending) >= minimum:
            yield pending.decode("ascii")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path, help="binary file to inspect")
    parser.add_argument("--min-length", type=int, default=4)
    parser.add_argument("--max-length", type=int, default=300)
    parser.add_argument("--max-results", type=int, default=1000)
    parser.add_argument("--chunk-size", type=int, default=1024 * 1024)
    parser.add_argument("--keyword", action="append", dest="keywords", help="case-insensitive keyword; repeatable")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    if args.min_length < 1 or args.max_length < args.min_length or min(args.max_results, args.chunk_size) < 1:
        print("error: invalid limits", file=sys.stderr)
        return 2
    if not args.binary.is_file():
        print(f"error: file not found: {args.binary}", file=sys.stderr)
        return 2
    keywords = tuple(k.lower() for k in (args.keywords or DEFAULT_KEYWORDS))
    results: set[str] = set()
    try:
        for value in printable_strings(args.binary, args.min_length, args.chunk_size):
            if len(value) <= args.max_length and any(k in value.lower() for k in keywords):
                results.add(value)
                if len(results) >= args.max_results:
                    break
    except OSError as exc:
        print(f"error: could not read {args.binary}: {exc}", file=sys.stderr)
        return 1
    print(*sorted(results), sep="\n")
    print(f"Found {len(results)} unique matching strings.", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
