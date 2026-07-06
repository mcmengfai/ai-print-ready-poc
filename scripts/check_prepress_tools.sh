#!/usr/bin/env bash
set -euo pipefail

echo "== Required binaries =="
for c in python uv magick gs qpdf pdfinfo pdftoppm exiftool; do
  if command -v "$c" >/dev/null 2>&1; then
    printf 'OK   %-10s %s\n' "$c" "$(command -v "$c")"
  else
    printf 'MISS %-10s\n' "$c"
    exit 1
  fi
done

echo "== Versions =="
magick -version | head -n 2
gs --version
qpdf --version | head -n 1
pdfinfo -v 2>&1 | head -n 1
exiftool -ver

echo "== ICC profiles found =="
count=$(find /usr/share/color /usr/local/share/color -type f \( -iname '*.icc' -o -iname '*.icm' \) 2>/dev/null | wc -l | tr -d ' ')
echo "ICC_COUNT=$count"
if [ "$count" -eq 0 ]; then
  echo "No ICC profiles found; install/add printer ICC profiles."
  exit 1
fi
find /usr/share/color /usr/local/share/color -type f \( -iname '*.icc' -o -iname '*.icm' \) 2>/dev/null | head -n 20
