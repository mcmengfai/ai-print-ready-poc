from ai_print_ready.profiles import find_icc_profiles


def test_find_icc_profiles_flags_likely_cmyk(tmp_path):
    p = tmp_path / 'FOGRA39-test.icc'
    p.write_bytes(b'fake')
    profiles = find_icc_profiles([tmp_path])
    assert any(item['path'] == str(p.resolve()) and item['likely_cmyk'] for item in profiles)


def test_find_icc_profiles_finds_icm(tmp_path):
    p = tmp_path / 'sRGB.icm'
    p.write_bytes(b'fake')
    profiles = find_icc_profiles([tmp_path])
    assert any(item['path'] == str(p.resolve()) for item in profiles)
