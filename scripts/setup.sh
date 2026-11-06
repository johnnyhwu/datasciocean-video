#!/usr/bin/env bash
# 從零建立本專案的環境。全部裝在專案資料夾內，不動系統（使用者的硬性要求）。
#   tools/micromamba   獨立執行檔（conda-forge 官方 release）
#   .mamba/            micromamba 的 root prefix（快取）
#   .sysdeps/          cairo、pango、pkg-config 等系統函式庫（pycairo 編譯與執行時用）
#   .venv/、.uv-cache/ Python 套件（uv）
# 刪掉這幾個資料夾就完全乾淨。
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
export MAMBA_ROOT_PREFIX="$ROOT/.mamba"
if [ ! -x tools/micromamba ]; then
  mkdir -p tools
  curl -sSL -o tools/micromamba https://github.com/mamba-org/micromamba-releases/releases/latest/download/micromamba-osx-arm64
  chmod +x tools/micromamba
fi
if [ ! -f .sysdeps/lib/pkgconfig/cairo.pc ]; then
  tools/micromamba create -y -q -p "$ROOT/.sysdeps" -c conda-forge --override-channels cairo pango pkg-config zlib expat
fi
# pycairo 在 macOS 沒有 wheel：對 .sysdeps 的 cairo 編譯，並寫入 rpath，執行時不需要任何環境變數
export PATH="$ROOT/.sysdeps/bin:$PATH" PKG_CONFIG_PATH="$ROOT/.sysdeps/lib/pkgconfig" LDFLAGS="-Wl,-rpath,$ROOT/.sysdeps/lib"
uv sync
uv run python -W ignore -c "import cairo, manim; print('OK  manim', manim.__version__, ' cairo', cairo.version)"
