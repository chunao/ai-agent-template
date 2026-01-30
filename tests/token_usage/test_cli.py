"""Tests for CLI entry point."""

import pytest
import tempfile
import os
from pathlib import Path
from src.token_usage.cli import parse_args, record_usage_cli


class TestParseArgs:
    """コマンドライン引数パースのテスト."""

    def test_session_start_args(self):
        """正常系: session_start引数をパースできること."""
        args = parse_args([
            "--event", "session_start",
            "--session-id", "sess_test",
            "--issue", "94"
        ])

        assert args.event == "session_start"
        assert args.session_id == "sess_test"
        assert args.issue == "94"

    def test_skill_start_args(self):
        """正常系: skill_start引数をパースできること."""
        args = parse_args([
            "--event", "skill_start",
            "--skill", "tdd-cycle",
            "--issue", "94"
        ])

        assert args.event == "skill_start"
        assert args.skill == "tdd-cycle"

    def test_tool_call_args(self):
        """正常系: tool_call引数をパースできること."""
        args = parse_args([
            "--event", "tool_call",
            "--tool", "Read",
            "--input-tokens", "1234",
            "--output-tokens", "567",
            "--model", "sonnet-4.5"
        ])

        assert args.event == "tool_call"
        assert args.tool == "Read"
        assert args.input_tokens == 1234
        assert args.output_tokens == 567

    def test_minimal_args(self):
        """正常系: 最小限の引数でパースできること."""
        args = parse_args([
            "--event", "session_start",
            "--session-id", "test"
        ])

        assert args.event == "session_start"
        assert args.session_id == "test"


class TestRecordUsageCLI:
    """CLIエントリーポイントのテスト."""

    @pytest.fixture
    def temp_log_dir(self):
        """一時ログディレクトリを作成."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_session_start_via_cli(self, temp_log_dir):
        """正常系: CLIからsession_startを記録できること."""
        # 環境変数を設定
        os.environ["TOKEN_USAGE_DIR"] = temp_log_dir

        # CLIを実行
        record_usage_cli([
            "--event", "session_start",
            "--session-id", "sess_cli_test",
            "--issue", "94"
        ])

        # ログファイルが作成されたことを確認
        sessions_dir = Path(temp_log_dir) / "sessions"
        assert sessions_dir.exists()

        log_files = list(sessions_dir.glob("*.jsonl"))
        assert len(log_files) > 0

    def test_skill_start_via_cli(self, temp_log_dir):
        """正常系: CLIからskill_startを記録できること."""
        os.environ["TOKEN_USAGE_DIR"] = temp_log_dir
        os.environ["CLAUDE_SESSION_ID"] = "sess_cli_test"

        # まずセッションを開始
        record_usage_cli([
            "--event", "session_start",
            "--session-id", "sess_cli_test"
        ])

        # スキルを開始
        record_usage_cli([
            "--event", "skill_start",
            "--skill", "tdd-cycle"
        ])

        # ログファイルにskill_startが記録されたことを確認
        sessions_dir = Path(temp_log_dir) / "sessions"
        log_files = list(sessions_dir.glob("*.jsonl"))
        assert len(log_files) > 0

    def test_error_handling_no_session(self, temp_log_dir):
        """異常系: セッション未開始時はエラー."""
        os.environ["TOKEN_USAGE_DIR"] = temp_log_dir

        # セッションを開始せずにスキルを開始
        with pytest.raises(RuntimeError, match="No active session"):
            record_usage_cli([
                "--event", "skill_start",
                "--skill", "tdd-cycle"
            ])

    def test_invalid_event_type(self, temp_log_dir):
        """異常系: 不正なイベントタイプはエラー."""
        os.environ["TOKEN_USAGE_DIR"] = temp_log_dir

        with pytest.raises(ValueError, match="Invalid event type"):
            record_usage_cli([
                "--event", "invalid_event"
            ])
