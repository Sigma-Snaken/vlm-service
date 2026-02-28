import json
from vlm_service.schema import build_inspection_schema, build_report_schema


class TestBuildInspectionSchema:
    """Test dynamic inspection schema construction."""

    def test_core_only(self):
        """No venue config → only is_ng + analysis."""
        schema = build_inspection_schema()
        assert schema["type"] == "OBJECT"
        props = schema["properties"]
        assert "is_ng" in props
        assert props["is_ng"]["type"] == "BOOLEAN"
        assert "analysis" in props
        assert props["analysis"]["type"] == "STRING"
        assert set(schema["required"]) == {"is_ng", "analysis"}

    def test_with_scores(self, sample_venue_config):
        """Venue config with scores → adds score properties."""
        schema = build_inspection_schema(sample_venue_config)
        props = schema["properties"]
        assert "is_ng" in props
        assert "analysis" in props
        assert "hygiene" in props
        assert props["hygiene"]["type"] == "INTEGER"
        assert "safety" in props

    def test_with_categories(self, sample_venue_config):
        """Venue config with categories → adds category enum field."""
        schema = build_inspection_schema(sample_venue_config)
        props = schema["properties"]
        assert "categories" in props
        assert props["categories"]["type"] == "ARRAY"
        items = props["categories"]["items"]
        assert set(items["enum"]) == {"cleanliness", "equipment", "fire_safety", "access"}

    def test_with_custom_fields(self, sample_venue_config):
        """Venue config with custom_fields → adds them to properties."""
        schema = build_inspection_schema(sample_venue_config)
        props = schema["properties"]
        assert "ward_id" in props
        assert props["ward_id"]["type"] == "STRING"

    def test_different_venues_produce_different_schemas(self, sample_venue_config, sample_factory_config):
        """Two different venue configs produce different schemas."""
        hospital = build_inspection_schema(sample_venue_config)
        factory = build_inspection_schema(sample_factory_config)
        assert "hygiene" in hospital["properties"]
        assert "hygiene" not in factory["properties"]
        assert "fire_risk" in factory["properties"]
        assert "fire_risk" not in hospital["properties"]

    def test_core_fields_always_required(self, sample_venue_config):
        """is_ng and analysis are always in required."""
        schema = build_inspection_schema(sample_venue_config)
        assert "is_ng" in schema["required"]
        assert "analysis" in schema["required"]


class TestBuildReportSchema:
    """Test dynamic report schema construction."""

    def test_default_report_schema(self):
        """No config → basic summary + details structure."""
        schema = build_report_schema()
        props = schema["properties"]
        assert "summary" in props
        assert "details" in props
        assert schema["type"] == "OBJECT"

    def test_report_with_sections(self):
        """Config with sections → adds section fields."""
        config = {
            "sections": ["overview", "findings", "recommendations"],
            "custom_sections": {
                "risk_assessment": {"type": "STRING", "description": "Risk assessment summary"},
            },
        }
        schema = build_report_schema(config)
        props = schema["properties"]
        assert "overview" in props
        assert "findings" in props
        assert "recommendations" in props
        assert "risk_assessment" in props
