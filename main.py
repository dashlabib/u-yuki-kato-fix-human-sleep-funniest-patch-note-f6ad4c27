#!/usr/bin/env python3
"""Fix Human Sleep: Funniest Patch Note.

Writes exactly one line of patch notes announcing that human sleep is
fixed, to /output/entry.txt (or --output <path>).

The line must satisfy the sealed scorer's gate:
  * UTF-8 text, 1-160 characters
  * a single line, not only whitespace
"""

import argparse
import sys
import tempfile
from pathlib import Path

ENTRY = (
    "Fixed a bug where 8 hours in bed counted as 3 hours of sleep "
    "and 5 hours of reliving that embarrassing thing from 2014."
)

DEFAULT_OUTPUT = Path("/output/entry.txt")


def validate(text: str) -> None:
    """Enforce the scorer's gate on the entry line. Raises ValueError."""
    if not isinstance(text, str):
        raise ValueError("entry must be a string")
    if not text:
        raise ValueError("entry must not be empty")
    if text.strip() != text:
        raise ValueError("entry must not have leading or trailing whitespace")
    if not text.strip():
        raise ValueError("entry must not be only whitespace")
    if len(text) > 160:
        raise ValueError(f"entry is {len(text)} chars, over the 160 cap")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if "\u00a0" in text:
        raise ValueError("entry must not contain a non-breaking space (U+00A0)")
    if "  " in text:
        raise ValueError("entry must not contain double spaces")
    for ch in text:
        code = ord(ch)
        if code < 0x20 or code == 0x7F:
            raise ValueError(f"entry contains a control char U+{code:04X}")
        if 0x202A <= code <= 0x202E or 0x2066 <= code <= 0x2069 or code == 0xFEFF:
            raise ValueError(f"entry contains a format char U+{code:04X}")
    raw = text.encode("utf-8")
    if raw.decode("utf-8") != text:
        raise ValueError("entry does not survive a UTF-8 round-trip")


def write_entry(path: Path) -> None:
    validate(ENTRY)
    data = ENTRY.encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    # No trailing newline: the scorer wants exactly one line of text.
    path.write_bytes(data)


def self_test() -> bool:
    validate(ENTRY)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "entry.txt"
        write_entry(out)
        raw = out.read_bytes()
        if raw != ENTRY.encode("utf-8"):
            print("FAIL: written bytes differ from ENTRY", file=sys.stderr)
            return False
    n_chars = len(ENTRY)
    n_bytes = len(ENTRY.encode("utf-8"))
    print(f"PASS: entry is {n_chars} chars, {n_bytes} bytes, single line")
    return True


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help="where to write the entry line (default: /output/entry.txt)",
    )
    parser.add_argument(
        "--self-test", action="store_true",
        help="validate, write to a temp file, re-read and verify byte-identical",
    )
    parser.add_argument(
        "--verify-only", action="store_true",
        help="validate and print char/byte counts without writing",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return 0 if self_test() else 1
    if args.verify_only:
        validate(ENTRY)
        print(f"chars={len(ENTRY)} bytes={len(ENTRY.encode('utf-8'))}")
        return 0

    write_entry(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
