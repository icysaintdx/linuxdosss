#!/bin/zsh
set -e

cd "$(dirname "$0")"

export UV_CACHE_DIR="$PWD/.uv-cache"
export VIRTUAL_ENV="$PWD/.venv"

exec uv run python linux_do_gui.py
