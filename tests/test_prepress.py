from ai_print_ready.prepress import build_imagemagick_cmyk_command, build_ghostscript_cmyk_pdf_command


def test_build_imagemagick_cmyk_command_with_profiles(monkeypatch):
    monkeypatch.setattr('ai_print_ready.prepress.imagemagick_binary', lambda: 'magick')
    cmd = build_imagemagick_cmyk_command('in.png', 'out.tif', '/profiles/cmyk.icc', '/profiles/srgb.icc')
    assert cmd == ['magick', 'in.png', '-profile', '/profiles/srgb.icc', '-profile', '/profiles/cmyk.icc', 'out.tif']


def test_build_imagemagick_cmyk_command_without_srgb(monkeypatch):
    monkeypatch.setattr('ai_print_ready.prepress.imagemagick_binary', lambda: 'magick')
    cmd = build_imagemagick_cmyk_command('in.png', 'out.tif', '/profiles/cmyk.icc')
    assert cmd == ['magick', 'in.png', '-profile', '/profiles/cmyk.icc', 'out.tif']


def test_build_ghostscript_cmyk_pdf_command():
    cmd = build_ghostscript_cmyk_pdf_command('in.pdf', 'out.pdf', '/profiles/cmyk.icc')
    assert cmd[:6] == ['gs', '-dSAFER', '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite', '-sColorConversionStrategy=CMYK']
    assert '-dProcessColorModel=/DeviceCMYK' in cmd
    assert '-sOutputICCProfile=/profiles/cmyk.icc' in cmd
    assert '-sOutputFile=out.pdf' in cmd
    assert cmd[-1] == 'in.pdf'
