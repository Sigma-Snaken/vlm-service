"""Dynamic JSON schema builder for Gemini structured output.

Constructs `response_json_schema` dicts at runtime from venue config.
Uses Gemini's JSON schema subset (OBJECT, STRING, BOOLEAN, INTEGER, NUMBER, ARRAY).

Key principle: fixed core (is_ng + analysis) + dynamic fields from config.
"""

# Gemini uses uppercase type names in its JSON schema format
_TYPE_MAP = {
    "string": "STRING",
    "integer": "INTEGER",
    "number": "NUMBER",
    "boolean": "BOOLEAN",
    "array": "ARRAY",
    "object": "OBJECT",
}


def _map_type(t: str) -> str:
    """Map standard JSON schema types to Gemini uppercase format."""
    return _TYPE_MAP.get(t.lower(), "STRING")


def build_inspection_schema(venue_config: dict | None = None) -> dict:
    """Build a Gemini response_json_schema for image inspection.

    Args:
        venue_config: Optional venue-specific config with keys:
            - scores: dict of {name: {type, description, ...}}
            - categories: list of category strings (becomes enum array)
            - custom_fields: dict of {name: {type, description}}

    Returns:
        dict suitable for passing as response_json_schema to Gemini.
    """
    properties = {
        "is_ng": {
            "type": "BOOLEAN",
            "description": "True if abnormal/NG condition detected, False if normal/OK",
        },
        "analysis": {
            "type": "STRING",
            "description": "Detailed analysis description. Empty string if OK.",
        },
    }
    required = ["is_ng", "analysis"]

    if venue_config:
        # Add score fields
        for name, spec in venue_config.get("scores", {}).items():
            prop = {
                "type": _map_type(spec.get("type", "integer")),
                "description": spec.get("description", name),
            }
            if "minimum" in spec:
                prop["minimum"] = spec["minimum"]
            if "maximum" in spec:
                prop["maximum"] = spec["maximum"]
            properties[name] = prop

        # Add categories enum array
        cats = venue_config.get("categories", [])
        if cats:
            properties["categories"] = {
                "type": "ARRAY",
                "description": "Applicable issue categories",
                "items": {
                    "type": "STRING",
                    "enum": cats,
                },
            }

        # Add custom fields
        for name, spec in venue_config.get("custom_fields", {}).items():
            properties[name] = {
                "type": _map_type(spec.get("type", "string")),
                "description": spec.get("description", name),
            }

    return {
        "type": "OBJECT",
        "properties": properties,
        "required": required,
    }


def build_report_schema(report_config: dict | None = None) -> dict:
    """Build a Gemini response_json_schema for report generation.

    Args:
        report_config: Optional config with keys:
            - sections: list of section names (each becomes a STRING property)
            - custom_sections: dict of {name: {type, description}}

    Returns:
        dict suitable for passing as response_json_schema to Gemini.
    """
    properties = {
        "summary": {
            "type": "STRING",
            "description": "Executive summary of the patrol report",
        },
        "details": {
            "type": "STRING",
            "description": "Detailed findings and observations",
        },
    }
    required = ["summary", "details"]

    if report_config:
        for section_name in report_config.get("sections", []):
            properties[section_name] = {
                "type": "STRING",
                "description": f"{section_name.replace('_', ' ').title()} section",
            }
            required.append(section_name)

        for name, spec in report_config.get("custom_sections", {}).items():
            properties[name] = {
                "type": _map_type(spec.get("type", "string")),
                "description": spec.get("description", name),
            }

    return {
        "type": "OBJECT",
        "properties": properties,
        "required": required,
    }
