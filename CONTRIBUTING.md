# Contributing

This is an early PoC for an AI image print-readiness workflow.

## Development setup

```bash
uv sync --extra dev
uv run pytest -q
uv run python examples/create_demo_image.py
uv run ai-print-ready convert examples/demo-poster.png --preset A1-poster --job-name demo --overwrite --upscale auto
```

## Prepress toolchain

For ICC-managed CMYK and CMYK PDF candidate output, use the Dockerfile or install:

```bash
imagemagick ghostscript qpdf poppler-utils exiftool icc-profiles icc-profiles-free
```

Run:

```bash
scripts/check_prepress_tools.sh
```

## Output honesty rule

Do not claim a file is production-grade PDF/X or color-accurate unless it was validated with the printer profile and a preflight tool. Reports must distinguish:

- RGB print canvas
- Pillow CMYK fallback
- ICC-managed CMYK TIFF
- CMYK PDF candidate
- validated print-ready PDF
