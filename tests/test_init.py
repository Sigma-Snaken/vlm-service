"""Test that the public API is accessible from vlm_service."""


def test_imports():
    from vlm_service import GeminiProvider, PromptBuilder, FileManager
    from vlm_service import build_inspection_schema, build_report_schema
    from vlm_service import InspectionResult, ReportResult, VideoResult

    assert GeminiProvider is not None
    assert PromptBuilder is not None
    assert FileManager is not None
    assert build_inspection_schema is not None
    assert build_report_schema is not None
    assert InspectionResult is not None


def test_version():
    import vlm_service
    assert hasattr(vlm_service, "__version__")
