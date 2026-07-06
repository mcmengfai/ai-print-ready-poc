from __future__ import annotations
from pathlib import Path
from dataclasses import asdict, is_dataclass

def overall_status(dpi_status: str, aspect_status: str, color_status: str) -> str:
    statuses=[dpi_status, aspect_status, color_status]
    if "fail" in statuses: return "fail"
    if "warn" in statuses: return "warn"
    return "pass"

def status_icon(status: str) -> str:
    return {"pass":"✅","warn":"⚠️","fail":"❌"}.get(status,"ℹ️")

def build_report(job_name, image, preset, dpi, aspect, tools, outputs, canvas_info, limitations):
    status=overall_status(dpi.status, aspect.status, image.color_status)
    lines=[
        "# Print Readiness Report", "",
        "## Summary", "",
        f"Status: {status_icon(status)} **{status.upper()}**", "",
        f"Job: `{job_name}`", "",
        "## Target", "",
        f"- Preset: {preset.name}",
        f"- Trim size: {preset.width_mm:g} × {preset.height_mm:g} mm",
        f"- Bleed: {preset.bleed_mm:g} mm",
        f"- Target DPI: {preset.target_dpi}", "",
        "## Input image", "",
        f"- Format/mode: {image.format} / {image.mode}",
        f"- Pixels: {image.width_px} × {image.height_px}",
        f"- Embedded ICC: {'yes' if image.embedded_icc else 'no'}",
        f"- Alpha/transparency: {'yes' if image.has_alpha else 'no'}", "",
        "## Checks", "",
        f"- {status_icon(dpi.status)} Effective DPI: {dpi.effective_dpi:.1f} dpi — {dpi.recommendation}",
        f"- {status_icon(aspect.status)} Aspect ratio difference: {aspect.difference_percent:.1f}% — {aspect.recommendation}",
        f"- {status_icon(image.color_status)} Color risk: {image.high_saturation_percent:.1f}% high-saturation bright pixels. {image.color_warning}", "",
        "## Generated outputs", "",
    ]
    for k,v in outputs.items(): lines.append(f"- {k}: `{v}`")
    lines += ["", "## Tool capabilities", ""]
    lines += [f"- ImageMagick: {'available' if tools.imagemagick else 'not available'}", f"- Ghostscript: {'available' if tools.ghostscript else 'not available'}", f"- qpdf: {'available' if tools.qpdf else 'not available'}", f"- poppler pdfinfo: {'available' if tools.pdfinfo else 'not available'}", f"- exiftool: {'available' if tools.exiftool else 'not available'}"]
    if canvas_info:
        lines += ["", "## Canvas", "", f"- Canvas pixels: {canvas_info['canvas_px']}", f"- Trim pixels: {canvas_info['trim_px']}", f"- Bleed pixels: {canvas_info['bleed_px']}"]
        if 'upscale' in canvas_info:
            up = canvas_info['upscale']
            lines += [f"- Upscale: {up.get('factor', 1)}x via {up.get('method', 'unknown')}"]
    lines += ["", "## Limitations", ""]
    for item in limitations + tools.notes:
        lines.append(f"- {item}")
    lines += ["", "## Printer note", "", "This file was prepared using an automated open-source print workflow. It checks size, bleed, DPI, and color-conversion risk, but final print accuracy depends on the printer, paper, RIP settings, and ICC profile. Please ask the print shop to run final preflight before production."]
    return "\n".join(lines)+"\n"

def write_printer_note(path, preset, outputs):
    Path(path).write_text(f"""This package was prepared for {preset.name} ({preset.width_mm:g} × {preset.height_mm:g} mm) with {preset.bleed_mm:g} mm bleed.\n\nGenerated files:\n""" + "\n".join(f"- {k}: {v}" for k,v in outputs.items()) + "\n\nPlease run final preflight with your printer/RIP. If your print shop prefers RGB for large-format output, use the RGB PDF/PNG and let the RIP handle color conversion. If they require CMYK, ask for their ICC profile.\n", encoding="utf-8")
