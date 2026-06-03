#!/usr/bin/env sh
set -eu

UV_BIN="${UV:-uv}"

if ! command -v "$UV_BIN" >/dev/null 2>&1; then
  if [ -x "$HOME/.local/bin/uv" ]; then
    UV_BIN="$HOME/.local/bin/uv"
  else
  echo "uv is not installed. Install it first:"
  echo "  macOS/Homebrew: brew install uv"
  echo "  official installer: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 127
  fi
fi

: "${UV_CACHE_DIR:=.uv-cache}"
: "${MPLCONFIGDIR:=.mplconfig}"
export UV_CACHE_DIR MPLCONFIGDIR

"$UV_BIN" sync
"$UV_BIN" run python -m unittest discover -s tests
