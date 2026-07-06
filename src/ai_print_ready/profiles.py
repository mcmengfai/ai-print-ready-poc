from __future__ import annotations
from pathlib import Path

DEFAULT_PROFILE_DIRS = [
    Path('/usr/share/color'),
    Path('/usr/local/share/color'),
    Path('/app/profiles'),
    Path('/profiles'),
]


def find_icc_profiles(extra_dirs: list[str | Path] | None = None) -> list[dict]:
    dirs = list(DEFAULT_PROFILE_DIRS)
    if extra_dirs:
        dirs.extend(Path(p) for p in extra_dirs)
    seen=set()
    profiles=[]
    for d in dirs:
        if not d.exists():
            continue
        for p in sorted(list(d.rglob('*.icc')) + list(d.rglob('*.icm'))):
            rp=str(p.resolve())
            if rp in seen:
                continue
            seen.add(rp)
            lower=p.name.lower()
            likely_cmyk=any(token in lower for token in ['cmyk','fogra','gracol','swop','iso_coated','eci','japan'])
            profiles.append({
                'path': rp,
                'name': p.name,
                'likely_cmyk': likely_cmyk,
                'source_dir': str(d),
            })
    return profiles
