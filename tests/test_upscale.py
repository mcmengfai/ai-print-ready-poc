from pathlib import Path
from PIL import Image
from ai_print_ready.models import DpiResult
from ai_print_ready.upscale import choose_upscale_factor, upscale_image


def test_choose_upscale_auto_2x():
    dpi = DpiResult(77, 77, 77, 'fail', 'Suggest 2x upscale.')
    assert choose_upscale_factor('auto', dpi, 150) == 2


def test_choose_upscale_auto_4x():
    dpi = DpiResult(30, 30, 30, 'fail', 'Suggest 4x upscale.')
    assert choose_upscale_factor('auto', dpi, 150) == 4


def test_upscale_image_doubles_pixels(tmp_path):
    src = tmp_path / 'src.png'
    out = tmp_path / 'out.png'
    Image.new('RGB', (20, 30), (120, 30, 200)).save(src)
    meta = upscale_image(src, out, 2)
    assert out.exists()
    assert meta['factor'] == 2
    with Image.open(out) as im:
        assert im.size == (40, 60)
