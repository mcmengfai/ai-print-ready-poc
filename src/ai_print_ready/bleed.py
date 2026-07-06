from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageFilter
from .models import PrintPreset

MM_PER_INCH=25.4

def mm_to_px(mm: float, dpi: int) -> int:
    return max(1, round(mm / MM_PER_INCH * dpi))

def make_print_canvas(input_path: str | Path, output_png: str | Path, preset: PrintPreset, fit: str="cover") -> dict:
    out=Path(output_png); out.parent.mkdir(parents=True, exist_ok=True)
    dpi=preset.target_dpi
    bleed_px=mm_to_px(preset.bleed_mm, dpi)
    trim_w=mm_to_px(preset.width_mm, dpi)
    trim_h=mm_to_px(preset.height_mm, dpi)
    canvas_w=trim_w+2*bleed_px
    canvas_h=trim_h+2*bleed_px
    with Image.open(input_path) as im:
        src=im.convert("RGB")
        bg=cover_resize(src, (canvas_w, canvas_h)).filter(ImageFilter.GaussianBlur(radius=max(8, bleed_px//2)))
        main = cover_resize(src, (trim_w, trim_h)) if fit == "cover" else contain_resize(src, (trim_w, trim_h), bg_color=(255,255,255))
        bg.paste(main, (bleed_px, bleed_px))
        bg.save(out, dpi=(dpi,dpi))
    return {"canvas_px":[canvas_w,canvas_h],"trim_px":[trim_w,trim_h],"bleed_px":bleed_px,"dpi":dpi,"fit":fit}

def cover_resize(img: Image.Image, size: tuple[int,int]) -> Image.Image:
    tw,th=size; iw,ih=img.size
    scale=max(tw/iw, th/ih)
    nw,nh=round(iw*scale), round(ih*scale)
    r=img.resize((nw,nh), Image.Resampling.LANCZOS)
    left=(nw-tw)//2; top=(nh-th)//2
    return r.crop((left,top,left+tw,top+th))

def contain_resize(img: Image.Image, size: tuple[int,int], bg_color=(255,255,255)) -> Image.Image:
    tw,th=size; iw,ih=img.size
    scale=min(tw/iw, th/ih)
    nw,nh=round(iw*scale), round(ih*scale)
    r=img.resize((nw,nh), Image.Resampling.LANCZOS)
    bg=Image.new("RGB", size, bg_color)
    bg.paste(r, ((tw-nw)//2,(th-nh)//2))
    return bg
