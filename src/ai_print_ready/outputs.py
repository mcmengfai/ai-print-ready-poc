from __future__ import annotations
from pathlib import Path
import json, shutil
from PIL import Image

def prepare_job(input_path: str | Path, job_name: str, output_root: str | Path="print_jobs", overwrite: bool=False) -> dict[str, Path]:
    root=Path(output_root)/job_name
    if root.exists() and not overwrite:
        raise FileExistsError(f"Job folder exists: {root}. Use --overwrite.")
    if root.exists() and overwrite:
        shutil.rmtree(root)
    paths={k: root/k for k in ["original","analysis","previews","output","logs"]}
    for p in paths.values(): p.mkdir(parents=True, exist_ok=True)
    src=Path(input_path)
    copied=paths["original"]/src.name
    shutil.copy2(src,copied)
    paths["root"]=root; paths["copied_input"]=copied
    return paths

def write_json(path: str | Path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

def export_rgb_pdf(canvas_png: Path, pdf_path: Path):
    with Image.open(canvas_png) as im:
        rgb=im.convert("RGB")
        dpi=im.info.get("dpi", (150,150))[0] if im.info.get("dpi") else 150
        rgb.save(pdf_path, "PDF", resolution=dpi)

def export_cmyk_tiff_fallback(canvas_png: Path, tiff_path: Path):
    with Image.open(canvas_png) as im:
        cmyk=im.convert("CMYK")
        cmyk.save(tiff_path, compression="tiff_lzw", dpi=im.info.get("dpi", (150,150)))

def identify_with_pillow(path: str | Path) -> dict:
    with Image.open(path) as im:
        return {"path":str(path),"format":im.format,"mode":im.mode,"size_px":list(im.size),"dpi":im.info.get("dpi")}
