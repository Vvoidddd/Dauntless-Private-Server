"""Find likely configuration strings in a binary and preview named config files."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from extract_strings import printable_strings

KEYWORDS = ("playfab", "graphql", "gateway", "service", "epic", "dauntless", "ws://", "wss://", "sandbox", "prod-", "production")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path, help="binary file to inspect")
    parser.add_argument("--config", type=Path, action="append", default=[], help="text config to preview; repeatable")
    parser.add_argument("--max-results", type=int, default=500)
    parser.add_argument("--max-length", type=int, default=300)
    parser.add_argument("--preview-chars", type=int, default=1500)
    parser.add_argument("--chunk-size", type=int, default=1024 * 1024)
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    if not args.binary.is_file():
        print(f"error: file not found: {args.binary}", file=sys.stderr)
        return 2
    if min(args.max_results, args.max_length, args.preview_chars, args.chunk_size) < 1:
        print("error: limits must be positive", file=sys.stderr)
        return 2
    matches: set[str] = set()
    try:
        for value in printable_strings(args.binary, 4, args.chunk_size):
            if len(value) <= args.max_length and any(k in value.lower() for k in KEYWORDS):
                matches.add(value)
                if len(matches) >= args.max_results:
                    break
    except OSError as exc:
        print(f"error: could not read {args.binary}: {exc}", file=sys.stderr)
        return 1
    print("=== BINARY CONFIGURATION CANDIDATES ===")
    print(*sorted(matches), sep="\n")
    for config in args.config:
        print(f"\n=== CONFIG PREVIEW: {config} ===")
        try:
            with config.open("r", encoding="utf-8", errors="replace") as stream:
                print(stream.read(args.preview_chars))
        except OSError as exc:
            print(f"warning: could not read {config}: {exc}", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
