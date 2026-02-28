import json
from unittest.mock import MagicMock, patch
import pytest
from vlm_service.provider import GeminiProvider
from vlm_service.types import InspectionResult


class TestGeminiProviderConfigure:

    def test_configure_creates_client(self):
        with patch("vlm_service.provider.genai") as mock_genai:
            provider = GeminiProvider()
            provider.configure(api_key="test-key", model="gemini-2.0-flash")
            mock_genai.Client.assert_called_once_with(api_key="test-key")
            assert provider.is_configured()

    def test_configure_without_key(self):
        provider = GeminiProvider()
        provider.configure(api_key="", model="gemini-2.0-flash")
        assert not provider.is_configured()

    def test_reconfigure_only_on_change(self):
        with patch("vlm_service.provider.genai") as mock_genai:
            provider = GeminiProvider()
            provider.configure(api_key="key1", model="gemini-2.0-flash")
            provider.configure(api_key="key1", model="gemini-2.0-flash")
            assert mock_genai.Client.call_count == 1

    def test_reconfigure_on_key_change(self):
        with patch("vlm_service.provider.genai") as mock_genai:
            provider = GeminiProvider()
            provider.configure(api_key="key1", model="gemini-2.0-flash")
            provider.configure(api_key="key2", model="gemini-2.0-flash")
            assert mock_genai.Client.call_count == 2


class TestGeminiProviderInspection:

    def _make_mock_response(self, result_dict, prompt_tokens=100, output_tokens=50):
        response = MagicMock()
        response.text = json.dumps(result_dict)
        response.usage_metadata.prompt_token_count = prompt_tokens
        response.usage_metadata.candidates_token_count = output_tokens
        response.usage_metadata.total_token_count = prompt_tokens + output_tokens
        return response

    def test_generate_inspection_basic(self):
        with patch("vlm_service.provider.genai") as mock_genai:
            mock_client = MagicMock()
            mock_genai.Client.return_value = mock_client
            result_data = {"is_ng": True, "analysis": "Fire hazard"}
            mock_client.models.generate_content.return_value = self._make_mock_response(result_data)

            provider = GeminiProvider()
            provider.configure(api_key="test-key", model="gemini-2.0-flash")

            schema = {"type": "OBJECT", "properties": {"is_ng": {"type": "BOOLEAN"}, "analysis": {"type": "STRING"}}, "required": ["is_ng", "analysis"]}
            result = provider.generate_inspection(
                image=b"fake-image-bytes",
                user_prompt="Check this area",
                schema=schema,
            )

            assert isinstance(result, InspectionResult)
            assert result.is_ng is True
            assert result.analysis == "Fire hazard"
            assert result.total_tokens == 150

    def test_generate_inspection_with_system_prompt(self):
        with patch("vlm_service.provider.genai") as mock_genai:
            mock_client = MagicMock()
            mock_genai.Client.return_value = mock_client
            mock_client.models.generate_content.return_value = self._make_mock_response({"is_ng": False, "analysis": ""})

            provider = GeminiProvider()
            provider.configure(api_key="test-key", model="gemini-2.0-flash")

            schema = {"type": "OBJECT", "properties": {"is_ng": {"type": "BOOLEAN"}, "analysis": {"type": "STRING"}}, "required": ["is_ng", "analysis"]}
            provider.generate_inspection(
                image=b"fake-image-bytes",
                user_prompt="Check this area",
                system_prompt="You are an inspector",
                schema=schema,
            )

            call_kwargs = mock_client.models.generate_content.call_args
            config = call_kwargs.kwargs.get("config") or call_kwargs[1].get("config")
            assert config.system_instruction == "You are an inspector"

    def test_generate_inspection_not_configured_raises(self):
        provider = GeminiProvider()
        with pytest.raises(RuntimeError, match="not configured"):
            provider.generate_inspection(image=b"data", user_prompt="test", schema={})

    def test_generate_inspection_with_file_parts(self):
        """Test that file Parts (from Files API) are included in contents."""
        with patch("vlm_service.provider.genai") as mock_genai:
            mock_client = MagicMock()
            mock_genai.Client.return_value = mock_client
            mock_client.models.generate_content.return_value = self._make_mock_response({"is_ng": False, "analysis": ""})

            provider = GeminiProvider()
            provider.configure(api_key="test-key", model="gemini-2.0-flash")

            file_parts = [MagicMock(), MagicMock()]  # Simulated Part.from_uri() objects
            schema = {"type": "OBJECT", "properties": {"is_ng": {"type": "BOOLEAN"}, "analysis": {"type": "STRING"}}, "required": ["is_ng", "analysis"]}
            provider.generate_inspection(
                image=b"data",
                user_prompt="Check",
                schema=schema,
                file_parts=file_parts,
            )

            call_args = mock_client.models.generate_content.call_args
            contents = call_args.kwargs.get("contents") or call_args[1].get("contents")
            # file_parts should be in the contents list
            assert len(contents) >= 4  # file_part1 + file_part2 + user_prompt + image
