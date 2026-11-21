#!/bin/sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
revision=$(git -C "$root" rev-parse --verify "${1:-HEAD}^{commit}")
image=${2:-"ghcr.io/fanny7d/nas-tools:sha-$revision"}
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT HUP INT TERM

python3 "$root/scripts/prepare_fork_image.py" --revision "$revision" --output "$work/context"
docker build --platform linux/amd64 --build-arg "SOURCE_REVISION=$revision" \
    -f "$work/context/source/docker/fork.Dockerfile" -t "$image" "$work/context"
