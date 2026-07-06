from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
from pydantic import BaseModel, Field

class PrintPreset(BaseModel):
    id: str
    name: str
    width_mm: float = Field(gt=0)
    height_mm: float = Field(gt=0)
    target_dpi: int = Field(gt=0)
    bleed_mm: float = Field(ge=0)

@dataclass(frozen=True)
class ImageInfo:
    path: str
    width_px: int
    height_px: int
    mode: str
    format: str | None
    has_alpha: bool
    embedded_icc: bool
    dpi_metadata: tuple[float, float] | None
    high_saturation_percent: float
    color_status: str
    color_warning: str

@dataclass(frozen=True)
class DpiResult:
    effective_dpi_width: float
    effective_dpi_height: float
    effective_dpi: float
    status: str
    recommendation: str

@dataclass(frozen=True)
class AspectRatioResult:
    image_ratio: float
    target_ratio: float
    difference_percent: float
    status: str
    recommendation: str

@dataclass(frozen=True)
class ToolCapabilities:
    imagemagick: bool
    ghostscript: bool
    exiftool: bool
    qpdf: bool
    pdfinfo: bool
    pdftoppm: bool
    notes: list[str]

@dataclass(frozen=True)
class AnalysisBundle:
    job_name: str
    image: ImageInfo
    preset: dict[str, Any]
    dpi: DpiResult
    aspect: AspectRatioResult
    tools: ToolCapabilities
    limitations: list[str]

def dataclass_to_dict(obj):
    return asdict(obj)
