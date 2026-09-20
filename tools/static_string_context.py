"""Print offset-aware ASCII/UTF-16LE string context around search terms."""
from __future__ import annotations

import argparse
import bisect
import re
from pathlib import Path


ASCII = re.compile(rb"[\x20-\x7e]{4,}")
UTF16 = re.compile(rb"(?:[\x20-\x7e]\x00){4,}")


def strings(data: bytes):
    for match in ASCII.finditer(data):
        yield match.start(), "ascii", match.group().decode("ascii")
    for match in UTF16.finditer(data):
        yield match.start(), "utf16le", match.group().decode("utf-16le")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("terms", nargs="+")
    parser.add_argument("--window", type=int, default=512)
    args = parser.parse_args()
    data = args.binary.read_bytes()
    entries = sorted(strings(data))
    offsets = [entry[0] for entry in entries]
    selected: set[int] = set()
    lowered = [term.casefold() for term in args.terms]
    for index, (_, _, value) in enumerate(entries):
        if any(term in value.casefold() for term in lowered):
            selected.add(index)
    for index in sorted(selected):
        target_offset = entries[index][0]
        print(f"\n--- target 0x{target_offset:08x} ({target_offset}) ---")
        start = bisect.bisect_left(offsets, target_offset - args.window)
        stop = bisect.bisect_right(offsets, target_offset + args.window)
        for offset, encoding, value in entries[start:stop]:
            print(f"0x{offset:08x} {encoding:7} {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
