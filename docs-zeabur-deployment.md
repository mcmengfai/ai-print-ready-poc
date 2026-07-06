# Zeabur / Docker Deployment Notes for ai-print-ready

This project now includes a Dockerfile that installs the mature open-source prepress toolchain:

- ImageMagick + LittleCMS path for ICC-based CMYK TIFF conversion
- Ghostscript for CMYK PDF candidate generation
- qpdf / poppler-utils for future PDF checks
- exiftool for metadata inspection
- Debian ICC profile packages as a baseline

## Build locally

```bash
docker build -t ai-print-ready:prepress .
```

## Run CLI in Docker

```bash
docker run --rm \
  -v "$PWD/examples:/input:ro" \
  -v "$PWD/print_jobs:/app/print_jobs" \
  ai-print-ready:prepress \
  convert /input/demo-poster.png --preset A1-poster --job-name docker-demo --overwrite --upscale auto
```

## With printer ICC profile

Put the printer profile on the host, then mount it:

```bash
docker run --rm \
  -v "$PWD/examples:/input:ro" \
  -v "$PWD/print_jobs:/app/print_jobs" \
  -v "$PWD/profiles:/profiles:ro" \
  ai-print-ready:prepress \
  convert /input/demo-poster.png \
  --preset A1-poster \
  --job-name cmyk-demo \
  --overwrite \
  --upscale auto \
  --cmyk-profile /profiles/printer-cmyk.icc
```

When `--cmyk-profile` is supplied and ImageMagick/Ghostscript are available, the workflow attempts:

- `output/image-cmyk-icc.tif`
- `output/print-ready-cmyk-candidate.pdf`

The report still labels the PDF as a candidate, because final PDF/X/preflight validation should be done by the printer or a dedicated validator.

## Zeabur deployment

Use Dockerfile deployment. The service does not need to run a web server for CLI usage; for a Hermes-integrated workflow, call this CLI from Hermes inside a container image that includes the same apt packages.

If integrating into the existing Hermes Zeabur image, add the apt packages from this Dockerfile to the image build layer, not by running `apt-get` inside the live container. The current live Hermes tool shell does not have root permissions, and Docker daemon access is not available from the session.

## Verification after deploy

Run inside the built container:

```bash
scripts/check_prepress_tools.sh
uv run pytest -q
uv run python examples/create_demo_image.py
uv run ai-print-ready convert examples/demo-poster.png --preset A1-poster --job-name verify --overwrite --upscale auto
```

Then confirm:

- the script exits successfully even if no system ICC profile is installed; missing profiles are a runtime warning, not a build blocker
- `analysis/preflight-report.md` exists
- `output/print-canvas-rgb.pdf` exists
- `output/image-cmyk-pillow-fallback.tif` exists, or `output/image-cmyk-icc.tif` if an ICC profile was supplied
- `logs/command-results.json` records ImageMagick/Ghostscript command results
