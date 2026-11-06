# 環境

所有東西都裝在專案內，不安裝任何東西到全域（使用者的硬性要求）。

## 基本環境（已可用）

```bash
uv sync                 # Python 3.12，套件在 .venv/，快取在 .uv-cache/
```

- ffmpeg：用 `imageio-ffmpeg` 附帶的靜態檔（`.venv` 內），程式透過 `lib/paths.py: ffmpeg()` 取得。系統沒有 ffmpeg，也不需要裝。
- 字型：`assets/fonts/` 的 Noto Sans CJK TC（OFL）。Manim 在行程內用 `manimpango.register_font` 註冊，不放到 `~/.fonts`。

## 渲染環境（已可用，2026-11-07）

ManimCE 需要 pycairo，而 pycairo 在 macOS 沒有 wheel，要對 cairo 編譯。做法是**專案內的 micromamba**（使用者 2026-11-07 同意）：

```bash
./scripts/setup.sh      # 從零建立：tools/micromamba → .sysdeps/（cairo、pango、pkg-config、zlib、expat）→ uv sync
```

- 全部在專案資料夾內：`tools/`、`.mamba/`、`.sysdeps/`、`.venv/`、`.uv-cache/`（都在 `.gitignore`）。刪掉就乾淨。
- pycairo 編譯時寫入指向 `.sysdeps/lib` 的 rpath，執行時不需要任何環境變數。
- manim 已列在預設依賴群組（`default-groups = ["render"]`），平常 `uv sync`、`uv run` 就有 manim。
  如果 uv 快取被清掉、要重新編譯 pycairo，請跑 `scripts/setup.sh`，不要直接 `uv sync`（缺少編譯環境變數會失敗）。
- 沒有 LaTeX：公式用 Text 排（PoC 也是這樣做）。需要 MathTex 時再評估（例如 Typst，manim 0.21 起內建）。
