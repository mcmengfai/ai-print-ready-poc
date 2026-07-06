# ICC Profile Strategy

## Product rule

Do **not** silently choose a CMYK profile and call the result print-accurate. Profile choice is part of the print condition: printer, ink, substrate, paper/board, RIP, and region all matter.

The workflow should use this priority order:

1. **Printer-supplied ICC profile** — best option.
2. **Print-shop instruction to keep RGB** — common in large-format/RIP-managed output; produce RGB print canvas and let the printer convert.
3. **Explicit user-selected generic CMYK profile** — acceptable for testing or non-critical output, but report must label it.
4. **Pillow CMYK fallback** — only a technical fallback, not color-managed print output.

## What the code supports

List available profiles:

```bash
uv run ai-print-ready profiles
uv run ai-print-ready profiles --search-dir ./profiles
```

Run with an explicit CMYK profile:

```bash
uv run ai-print-ready convert examples/demo-poster.png \
  --preset A1-poster \
  --job-name cmyk-demo \
  --overwrite \
  --upscale auto \
  --cmyk-profile ./profiles/printer-cmyk.icc
```

Optional explicit sRGB input profile:

```bash
uv run ai-print-ready convert examples/demo-poster.png \
  --preset A1-poster \
  --job-name cmyk-demo \
  --overwrite \
  --upscale auto \
  --srgb-profile ./profiles/sRGB.icc \
  --cmyk-profile ./profiles/printer-cmyk.icc
```

## Generic profile sources

### 1. Printer / output vendor profile

Preferred for real jobs. Ask the print shop:

- Do you prefer RGB or CMYK files for large-format output?
- If CMYK, which ICC profile should I use?
- Required total ink limit / TAC?
- Required PDF/X version, if any?
- Bleed and safety margins?

### 2. Debian packages inside Docker

The Dockerfile installs:

```bash
icc-profiles-free
```

Use:

```bash
scripts/check_prepress_tools.sh
uv run ai-print-ready profiles
find /usr/share/color /usr/local/share/color -type f \( -iname '*.icc' -o -iname '*.icm' \)
```

These packages are useful as baseline profile sources, but the exact installed profile list depends on the Debian release/package contents.

### 3. ICC profile registry

The International Color Consortium provides a profile library. The ICC license text on its profile library page says ICC-owned profiles may be copied, distributed, embedded, made, used, and sold without restriction, with conditions around altered versions retaining/removing original identification/copyright as appropriate.

Use these primarily for common color encoding / reference profiles unless a registered CMYK output profile matches your print condition.

Source: https://www.color.org/profiles2.xalter

### 4. ECI / FOGRA profiles

ECI publishes offset/CMYK exchange profiles such as eciCMYK v2 / FOGRA-related profiles. These are strong candidates for European-style generic CMYK workflows, but they must be downloaded and reviewed under ECI's terms before bundling in this repo.

Source: https://www.eci.org/en/downloads

Do not bundle ECI profiles into the repo until license/distribution terms are confirmed. Instead, document a download step or ask the user to mount profiles under `/profiles`.

## Recommended first real-world test profile plan

For PoC validation:

1. Ask one local Macau/HK print shop for their preferred input:
   - If they say **RGB preferred**, test RGB PDF output and report only.
   - If they provide **CMYK ICC**, mount it and test `--cmyk-profile`.
2. If no print-shop profile is available, use a clearly labeled generic profile from the Docker environment or manually downloaded ECI/ICC source.
3. Print one small A3/A2 proof before trusting A1/roll-up output.

## Report wording

When a printer ICC profile is supplied:

```text
CMYK conversion used the supplied ICC profile: <profile path/name>. Final appearance still depends on the print shop RIP, media, and calibration.
```

When a generic profile is used:

```text
CMYK conversion used a generic profile selected by the user. This is suitable for workflow testing but may not match the target printer/media.
```

When fallback is used:

```text
CMYK TIFF fallback was generated without ICC color management. Do not treat it as color-accurate production CMYK.
```
