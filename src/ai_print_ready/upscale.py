from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageFilter
from .models import DpiResult


def choose_upscale_factor(mode: str, dpi: DpiResult, target_dpi: int) -> int:
    """Return 1, 2, or 4 based on mode and DPI gap."""
    normalized = mode.lower().strip()
    if normalized in {"none", "off", "1", "1x"}:
        return 1
    if normalized in {"2", "2x"}:
        return 2
    if normalized in {"4", "4x"}:
        return 4
    if normalized != "auto":
        raise ValueError("upscale must be one of: none, auto, 2x, 4x")
    if dpi.effective_dpi >= target_dpi:
        return 1
    if dpi.effective_dpi * 2 >= target_dpi:
        return 2
    if dpi.effective_dpi * 4 >= target_dpi:
        return 4
    return 4


def upscale_image(input_path: str | Path, output_path: str | Path, factor: int) -> dict:
    """Upscale with Pillow LANCZOS + light sharpening.

    This is a practical built-in fallback, not a neural upscaler. It produces
    larger print-prep pixels so the rest of the pipeline can work without
    external Real-ESRGAN/Upscayl dependencies.
    """
    src = Path(input_path)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if factor <= 1:
        return {"factor": 1, "path": str(src), "method": "none"}
    with Image.open(src) as im:
        rgb = im.convert("RGB")
        new_size = (rgb.width * factor, rgb.height * factor)
        up = rgb.resize(new_size, Image.Resampling.LANCZOS)
        up = up.filter(ImageFilter.UnsharpMask(radius=1.2, percent=80, threshold=3))
        up.save(out, dpi=im.info.get("dpi", (72, 72)))
    return {"factor": factor, "path": str(out), "method": "pillow-lanczos-unsharp", "size_px": list(new_size)}
