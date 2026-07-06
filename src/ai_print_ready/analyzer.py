from __future__ import annotations
import colorsys
from pathlib import Path
from PIL import Image
from .models import ImageInfo, DpiResult, AspectRatioResult, PrintPreset

MM_PER_INCH = 25.4

def read_image_info(path: str | Path) -> ImageInfo:
    p=Path(path)
    with Image.open(p) as img:
        width,height=img.size
        mode=img.mode
        fmt=img.format
        has_alpha = mode in ("RGBA","LA") or (mode == "P" and "transparency" in img.info)
        embedded_icc = "icc_profile" in img.info
        dpi = img.info.get("dpi")
        dpi_metadata = None
        if isinstance(dpi, tuple) and len(dpi)>=2:
            dpi_metadata=(float(dpi[0]), float(dpi[1]))
        risk = high_saturation_percent(img)
    status="pass"
    warnings=[]
    if has_alpha:
        status="warn"; warnings.append("Image has transparency; print output was flattened onto white/background canvas.")
    if not embedded_icc:
        status="warn"; warnings.append("No embedded ICC profile; assuming sRGB for analysis.")
    if risk > 25:
        status="warn"; warnings.append(f"{risk:.1f}% sampled pixels are highly saturated/bright; CMYK print may look duller.")
    return ImageInfo(str(p), width, height, mode, fmt, has_alpha, embedded_icc, dpi_metadata, risk, status, " ".join(warnings) if warnings else "No obvious RGB color risk detected.")

def high_saturation_percent(img: Image.Image) -> float:
    sample=img.convert("RGB")
    sample.thumbnail((300,300))
    pixels=list(sample.getdata())
    if not pixels: return 0.0
    high=0
    for r,g,b in pixels:
        _,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
        if s > 0.85 and v > 0.65:
            high += 1
    return high/len(pixels)*100

def calculate_dpi(width_px: int, height_px: int, preset: PrintPreset) -> DpiResult:
    width_inches = preset.width_mm / MM_PER_INCH
    height_inches = preset.height_mm / MM_PER_INCH
    dpi_w = width_px / width_inches
    dpi_h = height_px / height_inches
    effective = min(dpi_w, dpi_h)
    if effective >= preset.target_dpi:
        return DpiResult(dpi_w, dpi_h, effective, "pass", "No upscale needed.")
    if effective >= preset.target_dpi * 0.7:
        return DpiResult(dpi_w, dpi_h, effective, "warn", "Printable, but close viewing may look soft. Consider 2x upscale.")
    if effective * 2 >= preset.target_dpi:
        rec="Suggest 2x upscale."
    elif effective * 4 >= preset.target_dpi:
        rec="Suggest 4x upscale."
    else:
        rec="Image is too small. Regenerate at higher resolution."
    return DpiResult(dpi_w, dpi_h, effective, "fail", rec)

def analyze_aspect_ratio(width_px: int, height_px: int, preset: PrintPreset) -> AspectRatioResult:
    image_ratio=width_px/height_px
    target_ratio=preset.width_mm/preset.height_mm
    diff=abs(image_ratio-target_ratio)/target_ratio*100
    if diff <= 2:
        return AspectRatioResult(image_ratio,target_ratio,diff,"pass","Aspect ratio matches target size.")
    if diff <= 8:
        return AspectRatioResult(image_ratio,target_ratio,diff,"warn","Aspect ratio is close but may need minor crop or padding.")
    return AspectRatioResult(image_ratio,target_ratio,diff,"fail","Aspect ratio differs significantly. Use crop, fit-with-background, or regenerate artwork.")
