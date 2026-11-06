# 環境

所有東西都裝在專案內，不安裝任何東西到全域（使用者的硬性要求）。

## 基本環境（已可用）

```bash
uv sync                 # Python 3.12，套件在 .venv/，快取在 .uv-cache/
```

- ffmpeg：用 `imageio-ffmpeg` 附帶的靜態檔（`.venv` 內），程式透過 `lib/paths.py: ffmpeg()` 取得。系統沒有 ffmpeg，也不需要裝。
- 字型：`assets/fonts/` 的 Noto Sans CJK TC（OFL）。Manim 在行程內用 `manimpango.register_font` 註冊，不放到 `~/.fonts`。

## 渲染環境（`--group render`，待定）

ManimCE 需要 pycairo，而 pycairo 在 macOS 沒有 wheel，要對系統的 cairo 編譯。本機沒有 Homebrew，也沒有 cairo。可行方案：

1. **專案內的 micromamba**：binary 放 `tools/`，環境放 `.sysdeps/`，從 conda-forge 裝 cairo、pango、pkg-config，再讓 uv 編譯 pycairo。全部在專案資料夾內。
2. **Docker**：用官方的 `manimcommunity/manim:v0.22.1` 映像，掛載專案資料夾渲染。附帶 LaTeX，公式可以用 MathTex。
3. 使用者自行安裝 Homebrew 與 cairo。這是全域安裝，違反使用者的規則，除非他明確同意。

定案後更新這份文件與 `pyproject.toml`。
