from __future__ import annotations
from pathlib import Path
import shutil
import subprocess


def imagemagick_binary() -> str | None:
    return shutil.which("magick") or shutil.which("convert")


def build_imagemagick_cmyk_command(input_path: str | Path, output_tiff: str | Path, cmyk_profile: str | Path, srgb_profile: str | Path | None = None) -> list[str]:
    """Build an ImageMagick ICC conversion command.

    Best case uses an explicit input sRGB profile and explicit printer/output
    CMYK profile. If srgb_profile is omitted, ImageMagick will use the image's
    embedded profile or its own assumptions; the report must disclose this.
    """
    magick = imagemagick_binary() or "magick"
    cmd = [magick, str(input_path)]
    if srgb_profile:
        cmd += ["-profile", str(srgb_profile)]
    cmd += ["-profile", str(cmyk_profile), str(output_tiff)]
    return cmd


def run_imagemagick_cmyk(input_path: str | Path, output_tiff: str | Path, cmyk_profile: str | Path, srgb_profile: str | Path | None = None) -> dict:
    magick = imagemagick_binary()
    if not magick:
        return {"ok": False, "skipped": True, "reason": "ImageMagick not available", "command": []}
    if not Path(cmyk_profile).exists():
        return {"ok": False, "skipped": True, "reason": f"CMYK profile not found: {cmyk_profile}", "command": []}
    if srgb_profile and not Path(srgb_profile).exists():
        return {"ok": False, "skipped": True, "reason": f"sRGB profile not found: {srgb_profile}", "command": []}
    cmd = build_imagemagick_cmyk_command(input_path, output_tiff, cmyk_profile, srgb_profile)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return {"ok": result.returncode == 0 and Path(output_tiff).exists(), "skipped": False, "returncode": result.returncode, "stdout": result.stdout[-2000:], "stderr": result.stderr[-2000:], "command": cmd}


def build_ghostscript_cmyk_pdf_command(input_pdf: str | Path, output_pdf: str | Path, output_icc: str | Path | None = None) -> list[str]:
    cmd = [
        "gs", "-dSAFER", "-dBATCH", "-dNOPAUSE",
        "-sDEVICE=pdfwrite",
        "-sColorConversionStrategy=CMYK",
        "-dProcessColorModel=/DeviceCMYK",
    ]
    if output_icc:
        cmd += [f"-sOutputICCProfile={output_icc}"]
    cmd += [f"-sOutputFile={output_pdf}", str(input_pdf)]
    return cmd


def run_ghostscript_cmyk_pdf(input_pdf: str | Path, output_pdf: str | Path, output_icc: str | Path | None = None) -> dict:
    if not shutil.which("gs"):
        return {"ok": False, "skipped": True, "reason": "Ghostscript not available", "command": []}
    if output_icc and not Path(output_icc).exists():
        return {"ok": False, "skipped": True, "reason": f"Output ICC not found: {output_icc}", "command": []}
    cmd = build_ghostscript_cmyk_pdf_command(input_pdf, output_pdf, output_icc)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return {"ok": result.returncode == 0 and Path(output_pdf).exists(), "skipped": False, "returncode": result.returncode, "stdout": result.stdout[-2000:], "stderr": result.stderr[-2000:], "command": cmd}
