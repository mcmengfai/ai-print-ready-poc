from __future__ import annotations
import shutil
from .models import ToolCapabilities

def detect_tools() -> ToolCapabilities:
    imagemagick = bool(shutil.which("magick") or shutil.which("convert"))
    notes=[]
    if not imagemagick:
        notes.append("ImageMagick not available: ICC-based CMYK conversion is unavailable; Pillow fallback may create a basic CMYK TIFF only.")
    if not shutil.which("gs"):
        notes.append("Ghostscript not available: PDF/X candidate generation is unavailable.")
    return ToolCapabilities(
        imagemagick=imagemagick,
        ghostscript=bool(shutil.which("gs")),
        exiftool=bool(shutil.which("exiftool")),
        qpdf=bool(shutil.which("qpdf")),
        pdfinfo=bool(shutil.which("pdfinfo")),
        pdftoppm=bool(shutil.which("pdftoppm")),
        notes=notes,
    )
