"""Tests for token usage logger."""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.token_usage.logger import TokenUsageLogger


class TestTokenUsageLogger:
    """Test TokenUsageLogger functionality."""

    @pytest.fixture
    def temp_log_dir(self, tmp_path):
        """Temporary log directory."""
        return tmp_path / ".token-usage"

    @pytest.fixture
    def logger(self, temp_log_dir):
        """TokenUsageLogger instance with temporary directory."""
        return TokenUsageLogger(base_dir=str(temp_log_dir))

    def test_init_creates_directory_structure(self, temp_log_dir, logger):
        """ログディレクトリ構造が自動作成される."""
        assert temp_log_dir.exists()
        assert (temp_log_dir / "sessions").exists()
        assert temp_log_dir.is_dir()

    def test_session_start_creates_log_file(self, temp_log_dir, logger):
        """セッション開始時にログファイルが作成される."""
        session_id = logger.start_session(issue="123", worktree="/path/to/worktree")

        assert session_id is not None
        sessions_dir = temp_log_dir / "sessions"
        log_files = list(sessions_dir.glob("*.jsonl"))
        assert len(log_files) == 1
        assert session_id in log_files[0].name

    def test_session_start_logs_event(self, temp_log_dir, logger):
        """セッション開始イベントがJSONL形式で記録される."""
        session_id = logger.start_session(issue="123", worktree="/path/to/worktree")

        log_file = next((temp_log_dir / "sessions").glob("*.jsonl"))
        with open(log_file) as f:
            event = json.loads(f.readline())

        assert event["event"] == "session_start"
        assert event["session_id"] == session_id
        assert event["issue"] == "123"
        assert event["worktree"] == "/path/to/worktree"
        assert "timestamp" in event

    def test_log_tool_call_records_tokens(self, temp_log_dir, logger):
        """ツール呼び出しイベントがトークン数とともに記録される."""
        session_id = logger.start_session(issue="123")

        logger.log_tool_call(
            tool="Read",
            params={"file_path": "test.py"},
            input_tokens=1234,
            output_tokens=567,
            model="sonnet-4.5",
            context={"skill": "tdd-cycle", "phase": "RED"}
        )

        log_file = next((temp_log_dir / "sessions").glob("*.jsonl"))
        with open(log_file) as f:
            lines = f.readlines()

        assert len(lines) == 2  # session_start + tool_call
        event = json.loads(lines[1])
        assert event["event"] == "tool_call"
        assert event["tool"] == "Read"
        assert event["input_tokens"] == 1234
        assert event["output_tokens"] == 567
        assert event["cumulative_input"] == 1234
        assert event["cumulative_output"] == 567
        assert event["context"]["skill"] == "tdd-cycle"
        assert event["context"]["phase"] == "RED"

    def test_cumulative_tokens_accumulate(self, temp_log_dir, logger):
        """累積トークン数が正しく加算される."""
        session_id = logger.start_session(issue="123")

        logger.log_tool_call("Read", {}, input_tokens=1000, output_tokens=500, model="sonnet-4.5")
        logger.log_tool_call("Edit", {}, input_tokens=2000, output_tokens=800, model="sonnet-4.5")

        log_file = next((temp_log_dir / "sessions").glob("*.jsonl"))
        with open(log_file) as f:
            lines = f.readlines()

        event2 = json.loads(lines[2])
        assert event2["cumulative_input"] == 3000
        assert event2["cumulative_output"] == 1300

    def test_end_session_logs_summary(self, temp_log_dir, logger):
        """セッション終了時にサマリーが記録される."""
        session_id = logger.start_session(issue="123")
        logger.log_tool_call("Read", {}, input_tokens=1000, output_tokens=500, model="sonnet-4.5")
        logger.log_tool_call("Edit", {}, input_tokens=2000, output_tokens=800, model="sonnet-4.5")

        logger.end_session()

        log_file = next((temp_log_dir / "sessions").glob("*.jsonl"))
        with open(log_file) as f:
            lines = f.readlines()

        summary = json.loads(lines[-1])
        assert summary["event"] == "session_end"
        assert summary["total_input"] == 3000
        assert summary["total_output"] == 1300
        assert summary["total_tools"] == 2
        assert "duration_sec" in summary

    def test_skill_tracking(self, temp_log_dir, logger):
        """スキル開始・終了イベントが記録される."""
        session_id = logger.start_session(issue="123")
        logger.start_skill("tdd-cycle", issue="123")
        logger.log_tool_call("Read", {}, input_tokens=1000, output_tokens=500, model="sonnet-4.5", context={"skill": "tdd-cycle"})
        logger.end_skill("tdd-cycle")

        log_file = next((temp_log_dir / "sessions").glob("*.jsonl"))
        with open(log_file) as f:
            lines = f.readlines()

        skill_start = json.loads(lines[1])
        skill_end = json.loads(lines[-1])

        assert skill_start["event"] == "skill_start"
        assert skill_start["skill"] == "tdd-cycle"
        assert skill_end["event"] == "skill_end"
        assert skill_end["skill"] == "tdd-cycle"
        assert skill_end["total_input"] > 0
        assert skill_end["total_output"] > 0

    def test_external_delegation_tracking(self, temp_log_dir, logger):
        """外部AI委任イベントが記録される."""
        session_id = logger.start_session(issue="123")

        logger.log_external_delegation(
            delegate_to="codex-cli",
            task="code-review",
            estimated_tokens_saved=3000
        )

        log_file = next((temp_log_dir / "sessions").glob("*.jsonl"))
        with open(log_file) as f:
            lines = f.readlines()

        event = json.loads(lines[1])
        assert event["event"] == "external_delegation"
        assert event["delegate_to"] == "codex-cli"
        assert event["estimated_tokens_saved"] == 3000

    def test_zero_tokens(self, temp_log_dir, logger):
        """トークン数が0でも正しく記録される."""
        session_id = logger.start_session(issue="123")
        logger.log_tool_call("Bash", {}, input_tokens=0, output_tokens=0, model="sonnet-4.5")

        log_file = next((temp_log_dir / "sessions").glob("*.jsonl"))
        with open(log_file) as f:
            lines = f.readlines()

        event = json.loads(lines[1])
        assert event["input_tokens"] == 0
        assert event["output_tokens"] == 0
        assert event["cumulative_input"] == 0
        assert event["cumulative_output"] == 0

    def test_session_id_uniqueness(self, temp_log_dir, logger):
        """複数セッションでIDが一意である."""
        session_id1 = logger.start_session(issue="123")
        logger.end_session()

        session_id2 = logger.start_session(issue="124")
        logger.end_session()

        assert session_id1 != session_id2

    def test_invalid_event_validation(self, temp_log_dir, logger):
        """必須フィールドが欠けている場合にエラーが発生する."""
        session_id = logger.start_session(issue="123")

        with pytest.raises(ValueError, match="tool name is required"):
            logger.log_tool_call(tool=None, params={}, input_tokens=100, output_tokens=50, model="sonnet-4.5")

    def test_no_session_error(self, temp_log_dir, logger):
        """セッション開始前のログ記録でエラーが発生する."""
        with pytest.raises(RuntimeError, match="No active session"):
            logger.log_tool_call("Read", {}, input_tokens=100, output_tokens=50, model="sonnet-4.5")
