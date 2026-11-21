#!/usr/bin/env python3
"""Prepare a Docker build context from a committed Git revision."""

import argparse
import hashlib
import io
import json
import pathlib
import subprocess
import tarfile
import urllib.request


WHEELS = {
    ("qbittorrent-api", "2026.8.1"): "c17260e416ec5832c3ed7aff46fb0e2b47e70b90de182e89c34133b9d4ce5a6e",
    ("Flask-Cors", "4.0.0"): "bc3492bfd6368d27cfe79c7821df5a8a319e1a6d5eab277a3794be19bdc51783",
    ("bencode.py", "4.0.0"): "99c06a55764e85ffe81622fdf9ee78bd737bad3ea61d119784a54bb28860d962",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--revision", default="HEAD")
    args = parser.parse_args()
    root = pathlib.Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(["git", "rev-parse", "--verify", args.revision + "^{commit}"], cwd=root, text=True).strip()
    args.output.mkdir(parents=True, exist_ok=False)
    source = args.output / "source"
    source.mkdir()
    archive = subprocess.check_output(["git", "archive", revision], cwd=root)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar.getmembers():
            path = pathlib.PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir()):
                raise ValueError(f"Unsupported archive entry: {member.name}")
        tar.extractall(source)
    wheels = args.output / "wheels"
    wheels.mkdir()
    for (name, version), digest in WHEELS.items():
        with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/{version}/json", timeout=30) as response:
            metadata = json.load(response)
        wheel = next(item for item in metadata["urls"] if item["filename"].endswith("none-any.whl"))
        with urllib.request.urlopen(wheel["url"], timeout=60) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError(f"Wheel checksum mismatch: {wheel['filename']}")
        (wheels / wheel["filename"]).write_bytes(data)
    print(revision)


if __name__ == "__main__":
    main()
