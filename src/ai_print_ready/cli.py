from __future__ import annotations
from pathlib import Path
from dataclasses import asdict
import typer
from rich.console import Console
from . import __version__
from .presets import get_preset, apply_overrides, PRESETS
from .analyzer import read_image_info, calculate_dpi, analyze_aspect_ratio
from .tools import detect_tools
from .outputs import prepare_job, write_json, export_rgb_pdf, export_cmyk_tiff_fallback, identify_with_pillow
from .bleed import make_print_canvas
from .reports import build_report, write_printer_note
from .upscale import choose_upscale_factor, upscale_image
from .prepress import run_imagemagick_cmyk, run_ghostscript_cmyk_pdf
from .profiles import find_icc_profiles

app = typer.Typer(help="AI image print-readiness PoC CLI")
console=Console()

def resolve_preset(preset_id, width_mm, height_mm, target_dpi, bleed_mm):
    return apply_overrides(get_preset(preset_id), width_mm, height_mm, target_dpi, bleed_mm)

@app.command()
def version():
    typer.echo(f"ai-print-ready {__version__}")

@app.command()
def presets():
    for p in PRESETS.values():
        typer.echo(f"{p.id}: {p.name} — {p.width_mm:g}x{p.height_mm:g}mm, {p.target_dpi}dpi, bleed {p.bleed_mm:g}mm")

@app.command()
def profiles(search_dir: list[Path] | None = typer.Option(None, "--search-dir", help="Extra directory to scan for .icc/.icm profiles")):
    """List discovered ICC profiles and flag likely CMYK candidates."""
    found = find_icc_profiles(search_dir)
    if not found:
        typer.echo("No ICC profiles found. Mount printer profiles under /profiles or install icc-profiles packages.")
        raise typer.Exit(code=1)
    for item in found:
        mark = "CMYK?" if item['likely_cmyk'] else "RGB/other"
        typer.echo(f"{mark:9} {item['path']}")

@app.command()
def analyze(input_path: Path, preset: str="A1-poster", width_mm: float|None=None, height_mm: float|None=None, target_dpi: int|None=None, bleed_mm: float|None=None):
    p=resolve_preset(preset,width_mm,height_mm,target_dpi,bleed_mm)
    info=read_image_info(input_path)
    dpi=calculate_dpi(info.width_px, info.height_px, p)
    aspect=analyze_aspect_ratio(info.width_px, info.height_px, p)
    console.print(f"Image: {input_path}")
    console.print(f"Target: {p.name}, {p.width_mm:g} x {p.height_mm:g} mm, {p.target_dpi} dpi")
    console.print(f"Effective DPI: {dpi.effective_dpi:.1f} [{dpi.status}] — {dpi.recommendation}")
    console.print(f"Aspect ratio: {aspect.status} — {aspect.recommendation}")
    console.print(f"Color risk: {info.color_status} — {info.color_warning}")

@app.command()
def convert(input_path: Path, preset: str="A1-poster", job_name: str|None=None, output_root: Path=Path("print_jobs"), width_mm: float|None=None, height_mm: float|None=None, target_dpi: int|None=None, bleed_mm: float|None=None, fit: str="cover", overwrite: bool=False, rgb_only: bool=False, upscale: str="auto", cmyk_profile: Path|None=None, srgb_profile: Path|None=None, make_cmyk_pdf: bool=True):
    p=resolve_preset(preset,width_mm,height_mm,target_dpi,bleed_mm)
    job=job_name or f"{input_path.stem}-{p.id}"
    paths=prepare_job(input_path, job, output_root, overwrite)
    tools=detect_tools()
    info=read_image_info(paths['copied_input'])
    dpi=calculate_dpi(info.width_px, info.height_px, p)
    aspect=analyze_aspect_ratio(info.width_px, info.height_px, p)
    outputs={}
    upscale_factor=choose_upscale_factor(upscale, dpi, p.target_dpi)
    working_input=paths['copied_input']
    upscale_info={"factor": 1, "path": str(working_input), "method": "none"}
    if upscale_factor > 1:
        upscaled_path=paths['output']/f"upscaled-{upscale_factor}x.png"
        upscale_info=upscale_image(working_input, upscaled_path, upscale_factor)
        working_input=upscaled_path
        outputs[f"Upscaled source {upscale_factor}x"]=str(upscaled_path)
        upscaled_image_info=read_image_info(working_input)
        dpi=calculate_dpi(upscaled_image_info.width_px, upscaled_image_info.height_px, p)
        aspect=analyze_aspect_ratio(upscaled_image_info.width_px, upscaled_image_info.height_px, p)
    canvas_png=paths['output']/"print-canvas-rgb.png"
    canvas_info=make_print_canvas(working_input, canvas_png, p, fit=fit)
    canvas_info['upscale']=upscale_info
    outputs['RGB print canvas PNG']=str(canvas_png)
    rgb_pdf=paths['output']/"print-canvas-rgb.pdf"
    export_rgb_pdf(canvas_png, rgb_pdf)
    outputs['RGB print canvas PDF']=str(rgb_pdf)
    command_results=[]
    if not rgb_only and cmyk_profile:
        cmyk_tiff=paths['output']/"image-cmyk-icc.tif"
        result=run_imagemagick_cmyk(canvas_png, cmyk_tiff, cmyk_profile, srgb_profile)
        command_results.append({"step":"imagemagick_cmyk_tiff", **result})
        if result.get('ok'):
            outputs['CMYK TIFF ICC-managed']=str(cmyk_tiff)
        else:
            cmyk_tiff=paths['output']/"image-cmyk-pillow-fallback.tif"
            export_cmyk_tiff_fallback(canvas_png, cmyk_tiff)
            outputs['CMYK TIFF fallback (no ICC)']=str(cmyk_tiff)
    elif not rgb_only:
        cmyk_tiff=paths['output']/"image-cmyk-pillow-fallback.tif"
        export_cmyk_tiff_fallback(canvas_png, cmyk_tiff)
        outputs['CMYK TIFF fallback (no ICC)']=str(cmyk_tiff)
    if make_cmyk_pdf and cmyk_profile:
        cmyk_pdf=paths['output']/"print-ready-cmyk-candidate.pdf"
        result=run_ghostscript_cmyk_pdf(rgb_pdf, cmyk_pdf, cmyk_profile)
        command_results.append({"step":"ghostscript_cmyk_pdf", **result})
        if result.get('ok'):
            outputs['CMYK PDF candidate']=str(cmyk_pdf)
    preview=paths['previews']/"rgb-preview.jpg"
    from PIL import Image
    with Image.open(canvas_png) as im:
        prev=im.convert('RGB'); prev.thumbnail((1600,1600)); prev.save(preview, quality=90)
    outputs['RGB preview']=str(preview)
    limitations=[
        "If a CMYK ICC profile is supplied and ImageMagick is available, the workflow attempts ICC-managed CMYK TIFF output; otherwise it falls back to Pillow RGB→CMYK conversion.",
        "Auto bleed uses blurred/covered image extension; manually check important text/logo near edges.",
        "PDF output is a print-size RGB PDF; CMYK PDF candidate requires Ghostscript and should still be validated by the printer.",
    ]
    report=build_report(job, info, p, dpi, aspect, tools, outputs, canvas_info, limitations)
    md=paths['analysis']/"preflight-report.md"; md.write_text(report, encoding='utf-8')
    data={
        'job_name':job,'input':str(input_path),'preset':p.model_dump(),'image':asdict(info),'dpi':asdict(dpi),'aspect':asdict(aspect),'tools':asdict(tools),'canvas':canvas_info,'upscale':upscale_info,'outputs':outputs,'command_results':command_results,'limitations':limitations,
        'readback': {k: identify_with_pillow(v) for k,v in outputs.items() if v.lower().endswith(('.png','.jpg','.jpeg','.tif','.tiff'))}
    }
    write_json(paths['analysis']/"preflight-report.json", data)
    write_json(paths['logs']/"tool-capabilities.json", asdict(tools))
    write_json(paths['logs']/"command-results.json", command_results)
    write_printer_note(paths['output']/"printer-note.txt", p, outputs)
    console.print(f"Created print package: {paths['root']}")
    console.print(f"Report: {md}")
