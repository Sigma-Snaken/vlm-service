"""vlm-service — Generic VLM image/video analysis + report generation."""

__version__ = "0.1.0"

from vlm_service.types import InspectionResult, ReportResult, VideoResult
from vlm_service.schema import build_inspection_schema, build_report_schema
from vlm_service.prompt import PromptBuilder
from vlm_service.provider import GeminiProvider
from vlm_service.files import FileManager

__all__ = [
    "GeminiProvider",
    "PromptBuilder",
    "FileManager",
    "build_inspection_schema",
    "build_report_schema",
    "InspectionResult",
    "ReportResult",
    "VideoResult",
]
