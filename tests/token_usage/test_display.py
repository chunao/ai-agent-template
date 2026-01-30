"""Tests for token usage display."""

import json
from pathlib import Path

import pytest

from src.token_usage.display import TokenUsageDisplay


class TestTokenUsageDisplay:
    """Test TokenUsageDisplay functionality."""

    @pytest.fixture
    def temp_log_dir(self, tmp_path):
        """Temporary log directory."""
        return tmp_path / ".token-usage"

    @pytest.fixture
    def display(self, temp_log_dir):
        """TokenUsageDisplay instance with temporary directory."""
        temp_log_dir.mkdir(parents=True, exist_ok=True)
        return TokenUsageDisplay(base_dir=str(temp_log_dir))

    @pytest.fixture
    def sample_current_data(self):
        """サンプルcurrent.jsonデータ."""
        return {
            "session_id": "sess_abc123",
            "timestamp": "2026-01-29T14:35:22Z",
            "current_context": "/tdd-cycle (Issue #123)",
            "cumulative": {
                "input": 12345,
                "output": 5678,
                "total": 18023
            },
            "latest": {
                "timestamp": "2026-01-29T14:35:22Z",
                "tool": "Edit",
                "file": "test.py",
                "input": 1234,
                "output": 567
            }
        }

    def test_update_current_creates_file(self, temp_log_dir, display):
        """current.jsonが作成される."""
        display.update_current(
            session_id="sess_abc123",
            context="/tdd-cycle (Issue #123)",
            cumulative_input=1000,
            cumulative_output=500,
            latest_tool="Read",
            latest_input=100,
            latest_output=50
        )

        current_file = temp_log_dir / "current.json"
        assert current_file.exists()

        with open(current_file) as f:
            data = json.load(f)

        assert data["session_id"] == "sess_abc123"
        assert data["current_context"] == "/tdd-cycle (Issue #123)"
        assert data["cumulative"]["input"] == 1000
        assert data["cumulative"]["output"] == 500

    def test_format_display_output(self, temp_log_dir, display, sample_current_data):
        """表示フォーマットが正しく生成される."""
        current_file = temp_log_dir / "current.json"
        with open(current_file, "w") as f:
            json.dump(sample_current_data, f)

        output = display.format_display()

        assert "Token Usage" in output
        assert "Session: sess_abc123" in output
        assert "Current Context: /tdd-cycle (Issue #123)" in output
        assert "Input:  12,345 tokens" in output
        assert "Output:  5,678 tokens" in output
        assert "Total:  18,023 tokens" in output
        assert "Tool: Edit (test.py)" in output

    def test_format_display_with_unicode_box(self, temp_log_dir, display, sample_current_data):
        """ボックス描画にUnicode罫線を使用する."""
        current_file = temp_log_dir / "current.json"
        with open(current_file, "w") as f:
            json.dump(sample_current_data, f)

        output = display.format_display()

        assert "━" in output  # 水平線
        assert "📊" in output  # アイコン

    def test_format_display_no_current_file(self, temp_log_dir, display):
        """current.jsonが存在しない場合のフォールバック."""
        output = display.format_display()

        assert "No active session" in output or "Token Usage" not in output

    def test_format_display_with_zero_tokens(self, temp_log_dir, display):
        """トークン数が0の場合の表示."""
        data = {
            "session_id": "sess_test",
            "timestamp": "2026-01-29T14:35:22Z",
            "current_context": "/test",
            "cumulative": {
                "input": 0,
                "output": 0,
                "total": 0
            },
            "latest": {
                "timestamp": "2026-01-29T14:35:22Z",
                "tool": "Bash",
                "file": "test.sh",
                "input": 0,
                "output": 0
            }
        }

        current_file = temp_log_dir / "current.json"
        with open(current_file, "w") as f:
            json.dump(data, f)

        output = display.format_display()

        assert "Input:  0 tokens" in output
        assert "Output:  0 tokens" in output
        assert "Total:  0 tokens" in output

    def test_format_number_with_commas(self, display):
        """数値がカンマ区切りでフォーマットされる."""
        formatted = display._format_number(12345)
        assert formatted == "12,345"

        formatted = display._format_number(1234567890)
        assert formatted == "1,234,567,890"

        formatted = display._format_number(0)
        assert formatted == "0"

    def test_clear_current(self, temp_log_dir, display):
        """current.jsonをクリアできる."""
        current_file = temp_log_dir / "current.json"
        with open(current_file, "w") as f:
            json.dump({"test": "data"}, f)

        display.clear_current()

        assert not current_file.exists() or current_file.stat().st_size == 0
