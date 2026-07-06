from pathlib import Path
from PIL import Image
from ai_print_ready.presets import get_preset
from ai_print_ready.analyzer import calculate_dpi, analyze_aspect_ratio, read_image_info
from ai_print_ready.bleed import make_print_canvas


def test_dpi_pass_for_large_a1():
    p=get_preset('A1-poster')
    r=calculate_dpi(4000, 6000, p)
    assert r.status == 'pass'


def test_aspect_ratio_pass_a_series():
    p=get_preset('A1-poster')
    r=analyze_aspect_ratio(2480, 3508, p)
    assert r.status == 'pass'


def test_high_saturation_warning(tmp_path):
    img=Image.new('RGB',(100,100),(255,0,180))
    path=tmp_path/'neon.png'; img.save(path)
    info=read_image_info(path)
    assert info.high_saturation_percent > 90
    assert info.color_status == 'warn'


def test_make_canvas(tmp_path):
    img=Image.new('RGB',(200,300),(255,255,255))
    src=tmp_path/'in.png'; out=tmp_path/'out.png'; img.save(src)
    p=get_preset('A3-poster')
    meta=make_print_canvas(src,out,p)
    assert out.exists()
    assert meta['canvas_px'][0] > meta['trim_px'][0]
