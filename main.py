#!/usr/bin/env python3
"""Entry for make.fun's "The One-Line Cat Joke That Lands" bounty.

Takes the single joke line stored in joke.txt (in the same folder as
this script) and delivers it to the judge as a file: exactly the joke,
with no trailing newline. Nothing else is produced, nothing is
downloaded, and running it twice gives the same bytes twice.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "joke.txt")


def read_joke():
    """Load the joke and check it is one clean line of 1-200 chars."""
    try:
        with open(SOURCE, encoding="utf-8", newline="") as handle:
            raw = handle.read()
    except FileNotFoundError:
        raise ValueError("cannot find joke file: " + SOURCE)
    except UnicodeDecodeError as exc:
        raise ValueError("joke.txt is not valid UTF-8: " + str(exc))

    if not raw.endswith("\n") or raw.count("\n") != 1:
        raise ValueError("joke.txt must contain one line plus one newline")
    line = raw[:-1]
    if len(line) < 1:
        raise ValueError("joke is empty")
    if len(line) > 200:
        raise ValueError("joke is %d chars, over the 200 limit" % len(line))
    if line != line.strip():
        raise ValueError("joke must not start or end with whitespace")
    if "\r" in line:
        raise ValueError("joke must not contain a carriage return")
    return line


def check_written(path, line):
    """Confirm the file on disk is byte-for-byte the joke line."""
    with open(path, "rb") as handle:
        data = handle.read()
    if data != line.encode("utf-8"):
        raise ValueError(
            "output %s is %d bytes, expected %d for the joke"
            % (path, len(data), len(line.encode("utf-8")))
        )


def run():
    line = read_joke()
    folder = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(folder, exist_ok=True)
    dest = os.path.join(folder, "entry.txt")

    # Write to a scratch file first and rename it into place, so a
    # failure partway through never leaves a half-written entry.txt.
    scratch = dest + ".tmp"
    with open(scratch, "w", encoding="utf-8", newline="") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(scratch, dest)

    check_written(dest, line)
    print(line)


if __name__ == "__main__":
    try:
        run()
    except (OSError, ValueError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        sys.exit(1)
