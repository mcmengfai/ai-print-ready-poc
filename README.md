# ai-print-ready PoC

Hermes-assisted PoC for turning AI/Canva/Figma-style RGB images into a print handoff package.

## What it does now

- Reads PNG/JPG/WebP image metadata.
- Calculates effective DPI for poster / roll-up / board presets.
- Warns about aspect-ratio mismatch.
- Estimates high-saturation RGB color risk for CMYK printing.
- Generates a target-size RGB print canvas with bleed.
- Supports built-in 2x/4x/auto upscale using Pillow LANCZOS + light sharpening.
- Exports RGB PNG and PDF.
- Exports a basic CMYK TIFF fallback via Pillow when `--rgb-only` is not used.
- Generates Markdown/JSON preflight reports and a printer note.

## Important limitation

The CMYK fallback is **not ICC-managed** unless ImageMagick + printer ICC profiles are added later. It is useful as a technical output artifact, not a guarantee of commercial color accuracy.

## Quick start

```bash
uv sync --extra dev
uv run ai-print-ready presets
uv run python examples/create_demo_image.py
uv run ai-print-ready convert examples/demo-poster.png --preset A1-poster --job-name demo-a1 --overwrite --upscale auto
```

## Optional stronger prepress tools

On a system where you have root access:

```bash
sudo apt-get update
sudo apt-get install -y imagemagick ghostscript qpdf poppler-utils exiftool icc-profiles icc-profiles-free
```

This current Hermes container did not allow apt installation, so the first runnable version uses Python/Pillow fallbacks. For a full prepress toolchain, use the included `Dockerfile` and see `docs-zeabur-deployment.md`. For profile selection, see `docs-icc-profile-strategy.md`.

List available ICC profiles in a deployed/prepress environment:

```bash
uv run ai-print-ready profiles
uv run ai-print-ready profiles --search-dir ./profiles
```

## ICC-managed CMYK / CMYK PDF candidate

When running in the Docker image or another environment with ImageMagick and Ghostscript installed, provide a printer CMYK ICC profile:

```bash
uv run ai-print-ready convert examples/demo-poster.png \
  --preset A1-poster \
  --job-name cmyk-demo \
  --overwrite \
  --upscale auto \
  --cmyk-profile /path/to/printer-cmyk.icc
```

If successful, outputs include:

- `output/image-cmyk-icc.tif`
- `output/print-ready-cmyk-candidate.pdf`
- `logs/command-results.json`
