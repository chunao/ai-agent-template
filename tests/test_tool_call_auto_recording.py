"""tool_call 自動記録機能のテスト

Issue #101: トークン使用量記録の自動化（Phase 4.2）
"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from src.token_usage.logger import TokenUsageLogger
from src.token_usage.estimator import TokenEstimator


class TestToolCallAutoRecording:
    """tool_call 自動記録のテスト"""

    @pytest.fixture
    def temp_log_dir(self, tmp_path):
        """一時ログディレクトリ"""
        return tmp_path / ".token-usage"

    @pytest.fixture
    def logger(self, temp_log_dir):
        """TokenUsageLogger インスタンス"""
        return TokenUsageLogger(base_dir=str(temp_log_dir))

    @pytest.fixture
    def estimator(self):
        """TokenEstimator インスタンス"""
        return TokenEstimator(model="gpt-4")

    def test_log_tool_call_with_estimated_flag(self, logger, temp_log_dir):
        """tool_callイベントが is_estimated フラグ付きで記録される"""
        # セッション開始
        session_id = logger.start_session(issue="101")

        # tool_call を記録（推定値フラグ付き）
        logger.log_tool_call(
            tool="Read",
            params={"file_path": "/path/to/file.py"},
            input_tokens=100,
            output_tokens=50,
            model="claude-sonnet-4.5",
            context={"is_estimated": True}  # 推定値フラグ
        )

        # JONLファイルを読み込んで確認
        log_file = temp_log_dir / "sessions" / f"{session_id}.jsonl"
        assert log_file.exists()

        with open(log_file, "r") as f:
            lines = f.readlines()

        # 2行目（tool_callイベント）を確認
        tool_call_event = json.loads(lines[1])

        assert tool_call_event["event"] == "tool_call"
        assert tool_call_event.get("context", {}).get("is_estimated") is True

    def test_cumulative_tokens_calculation(self, logger):
        """cumulative_input/output が正しく計算される"""
        logger.start_session(issue="101")

        # 1回目のtool_call
        logger.log_tool_call(
            tool="Read",
            params={"file_path": "/path/to/file1.py"},
            input_tokens=100,
            output_tokens=50,
            model="claude-sonnet-4.5"
        )

        assert logger.cumulative_input == 100
        assert logger.cumulative_output == 50

        # 2回目のtool_call
        logger.log_tool_call(
            tool="Write",
            params={"file_path": "/path/to/file2.py"},
            input_tokens=150,
            output_tokens=75,
            model="claude-sonnet-4.5"
        )

        assert logger.cumulative_input == 250  # 100 + 150
        assert logger.cumulative_output == 125  # 50 + 75

    def test_auto_estimate_tokens_for_tool_call(self, logger, estimator):
        """ツール呼び出し時にトークン数を自動推定する"""
        logger.start_session(issue="101")

        # 入力テキスト
        input_text = "Read file: /path/to/file.py"
        # 出力テキスト（ファイル内容）
        output_text = "def test():\n    pass"

        # トークン数を推定
        input_tokens = estimator.estimate(input_text)
        output_tokens = estimator.estimate(output_text)

        # tool_call を記録
        logger.log_tool_call(
            tool="Read",
            params={"file_path": "/path/to/file.py"},
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model="claude-sonnet-4.5",
            context={"is_estimated": True}
        )

        assert logger.cumulative_input == input_tokens
        assert logger.cumulative_output == output_tokens

    def test_tool_call_without_estimated_flag(self, logger, temp_log_dir):
        """is_estimated フラグがない場合（実測値）の記録"""
        session_id = logger.start_session(issue="101")

        # tool_call を記録（is_estimatedフラグなし = 実測値）
        logger.log_tool_call(
            tool="Bash",
            params={"command": "git status"},
            input_tokens=200,
            output_tokens=100,
            model="claude-sonnet-4.5"
        )

        # JONLファイルを読み込んで確認
        log_file = temp_log_dir / "sessions" / f"{session_id}.jsonl"
        with open(log_file, "r") as f:
            lines = f.readlines()

        tool_call_event = json.loads(lines[1])

        # is_estimatedフラグがない、またはfalse
        assert tool_call_event.get("context", {}).get("is_estimated") is None or \
               tool_call_event.get("context", {}).get("is_estimated") is False

    def test_multiple_tool_calls_with_mixed_flags(self, logger):
        """推定値と実測値が混在する場合の記録"""
        logger.start_session(issue="101")

        # 1回目: 推定値
        logger.log_tool_call(
            tool="Read",
            params={},
            input_tokens=100,
            output_tokens=50,
            model="claude-sonnet-4.5",
            context={"is_estimated": True}
        )

        # 2回目: 実測値
        logger.log_tool_call(
            tool="Bash",
            params={},
            input_tokens=200,
            output_tokens=100,
            model="claude-sonnet-4.5"
        )

        # cumulative値は両方の合計
        assert logger.cumulative_input == 300  # 100 + 200
        assert logger.cumulative_output == 150  # 50 + 100


class TestToolCallAutoRecordingBoundary:
    """tool_call 自動記録の境界値テスト"""

    @pytest.fixture
    def temp_log_dir(self, tmp_path):
        """一時ログディレクトリ"""
        return tmp_path / ".token-usage"

    @pytest.fixture
    def logger(self, temp_log_dir):
        """TokenUsageLogger インスタンス"""
        return TokenUsageLogger(base_dir=str(temp_log_dir))

    def test_zero_tokens_estimation(self, logger):
        """0トークンの推定値を記録（境界値）"""
        logger.start_session(issue="101")

        logger.log_tool_call(
            tool="Read",
            params={},
            input_tokens=0,
            output_tokens=0,
            model="claude-sonnet-4.5",
            context={"is_estimated": True}
        )

        assert logger.cumulative_input == 0
        assert logger.cumulative_output == 0

    def test_negative_tokens_not_allowed(self, logger):
        """負のトークン数は0に補正される（境界値 - バリデーション）"""
        logger.start_session(issue="101")

        # 負のトークン数を渡した場合、0に補正される
        logger.log_tool_call(
            tool="Read",
            params={},
            input_tokens=-100,  # 負の値
            output_tokens=-50,   # 負の値
            model="claude-sonnet-4.5",
            context={"is_estimated": True}
        )

        # 負の値は0に補正される
        assert logger.cumulative_input == 0
        assert logger.cumulative_output == 0
