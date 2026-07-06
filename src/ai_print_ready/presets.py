from .models import PrintPreset

PRESETS: dict[str, PrintPreset] = {
    "A3-poster": PrintPreset(id="A3-poster", name="A3 poster", width_mm=297, height_mm=420, target_dpi=300, bleed_mm=3),
    "A2-poster": PrintPreset(id="A2-poster", name="A2 poster", width_mm=420, height_mm=594, target_dpi=200, bleed_mm=3),
    "A1-poster": PrintPreset(id="A1-poster", name="A1 poster", width_mm=594, height_mm=841, target_dpi=150, bleed_mm=3),
    "rollup-80x200": PrintPreset(id="rollup-80x200", name="Roll-up banner 80x200cm", width_mm=800, height_mm=2000, target_dpi=120, bleed_mm=5),
    "kt-board-custom": PrintPreset(id="kt-board-custom", name="KT/Foam board default", width_mm=600, height_mm=900, target_dpi=120, bleed_mm=5),
}

def get_preset(preset_id: str) -> PrintPreset:
    if preset_id not in PRESETS:
        raise ValueError(f"Unknown preset '{preset_id}'. Valid presets: {', '.join(PRESETS)}")
    return PRESETS[preset_id]

def apply_overrides(preset: PrintPreset, width_mm=None, height_mm=None, target_dpi=None, bleed_mm=None) -> PrintPreset:
    return preset.model_copy(update={
        "width_mm": width_mm if width_mm is not None else preset.width_mm,
        "height_mm": height_mm if height_mm is not None else preset.height_mm,
        "target_dpi": target_dpi if target_dpi is not None else preset.target_dpi,
        "bleed_mm": bleed_mm if bleed_mm is not None else preset.bleed_mm,
    })
