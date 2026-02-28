# Real Integration Test Design

**Date:** 2026-02-28
**Status:** Approved

## Goal

Verify all vlm-service modules work end-to-end with real Gemini API calls and real patrol photos/videos from visual-patrol.

## Design

Single script `scripts/real_test.py` with `--module` selection and `--all` option.

### Modules

| Module | What it does | API needed |
|--------|-------------|------------|
| `schema` | Build schemas from 3 venue configs (hospital/factory/office), print full JSON dicts | No |
| `prompt` | Build prompts from same 3 configs with placeholder injection, print full strings | No |
| `inspect` | Run 1 NG + 1 OK photo through GeminiProvider with assembled schema+prompt, print results | Yes |
| `video` | Upload + analyze 1 patrol video, print results | Yes |
| `report` | Generate structured report from mock inspection data, print results | Yes |

### CLI Interface

```bash
python scripts/real_test.py --module schema          # no API key needed
python scripts/real_test.py --module prompt           # no API key needed
python scripts/real_test.py --module inspect --api-key KEY
python scripts/real_test.py --module video --api-key KEY
python scripts/real_test.py --module report --api-key KEY
python scripts/real_test.py --all --api-key KEY
```

### Test Data

- **Photos:** `/home/snaken/CodeBase/visual-patrol/data/robot-a/report/images/42_20260213_093558/`
  - NG: `__1_NG_ffb8d5f8-facf-4c3e-85a2-2c67396f9111.jpg`
  - OK: `AED1_OK_889d98cf-4de1-43d0-9a4f-35047b4d3a98.jpg`
- **Video:** `/home/snaken/CodeBase/visual-patrol/data/robot-a/report/video/44_20260213_234753.mp4` (3.3MB, smallest)

### Venue Configs

3 configs for schema/prompt testing:

1. **Hospital** — scores: hygiene + safety, categories: cleanliness/equipment/fire_safety/access, custom: ward_id, language: zh-TW
2. **Factory** — scores: fire_risk, categories: fire_prevention/machinery/ppe/chemical_storage, custom: zone + line_number, language: en
3. **Office** — scores: tidiness, categories: desk_area/meeting_room/entrance, no custom fields, language: ja

### Verification

- **schema**: Check properties/required/type for each venue config. Confirm dynamic fields appear and core fields (is_ng, analysis) are always present.
- **prompt**: Check section ordering ([Role] before [Instructions] before [Language]), placeholder replacement, language tag.
- **inspect**: Print is_ng, analysis, dynamic fields, token usage. Sanity check is_ng against filename OK/NG label.
- **video**: Print analysis + token usage. Confirm no crash on upload+poll cycle.
- **report**: Print summary + all sections. Confirm structured output matches schema.

### Output Format

Each module prints a header, then structured output:

```
=== SCHEMA: hospital ===
{
  "type": "OBJECT",
  "properties": { ... },
  "required": [...]
}

=== INSPECT: NG photo ===
is_ng: True
analysis: "..."
hygiene: 3
tokens: {prompt: 100, output: 50, total: 150}
raw: { ... }
```
