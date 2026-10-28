#!/usr/bin/env python3
"""Copy the canonical browser reveal CSS into the Python and Ruby packages."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "js" / "textprov.css"
TARGETS = (
    ROOT / "python" / "textprov" / "textprov.css",
    ROOT / "ruby" / "lib" / "textprov" / "textprov.css",
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="fail if packaged copies differ"
    )
    args = parser.parse_args(argv)
    canonical = SOURCE.read_bytes()
    different = [
        target for target in TARGETS
        if not target.exists() or target.read_bytes() != canonical
    ]
    if args.check:
        for target in different:
            print(f"out of sync: {target.relative_to(ROOT)}", file=sys.stderr)
        if different:
            print("run python3 tools/sync_display_styles.py", file=sys.stderr)
        return int(bool(different))
    for target in different:
        target.write_bytes(canonical)
        print(f"wrote {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
