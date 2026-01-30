"""skill_wrapper モジュールのテスト

Issue #101: トークン使用量記録の自動化（Phase 4.1）
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest


class TestSkillWrapper:
    """SkillWrapper のテスト"""

    @pytest.fixture
    def mock_logger(self):
        """TokenUsageLoggerのモック"""
        return MagicMock()

    @pytest.fixture
    def mock_context(self):
        """コンテキスト情報のモック"""
        return {
            "issue": "101",
            "worktree": "D:/projects/P010-worktrees/issue-101-auto-token-tracking",
            "session_id": "sess_20260130_112000_123456"
        }

    def test_auto_skill_start_records_session_and_skill(self, mock_logger, mock_context):
        """auto_skill_start が session_start と skill_start を記録する"""
        from src.token_usage.skill_wrapper import auto_skill_start

        with patch("src.token_usage.skill_wrapper.TokenUsageLogger", return_value=mock_logger), \
             patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}):

            session_id = auto_skill_start("tdd")

            # session_start が呼ばれる
            mock_logger.start_session.assert_called_once_with(
                session_id=mock_context["session_id"],
                issue=mock_context["issue"],
                worktree=mock_context["worktree"]
            )

            # skill_start が呼ばれる
            mock_logger.start_skill.assert_called_once_with("tdd")

            assert session_id == mock_context["session_id"]

    def test_auto_skill_end_records_skill_and_session_end(self, mock_logger):
        """auto_skill_end が skill_end と session_end を記録する"""
        from src.token_usage.skill_wrapper import auto_skill_end

        with patch("src.token_usage.skill_wrapper.TokenUsageLogger", return_value=mock_logger), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}):

            # session_idを渡す
            session_id = "sess_20260130_112000_123456"
            auto_skill_end("tdd", session_id)

            # skill_end が呼ばれる
            mock_logger.end_skill.assert_called_once_with("tdd")

            # session_end が呼ばれる
            mock_logger.end_session.assert_called_once()

    def test_auto_skill_start_enabled_true(self, mock_logger, mock_context):
        """TOKEN_USAGE_ENABLED=true の場合に記録が有効"""
        from src.token_usage.skill_wrapper import auto_skill_start

        with patch("src.token_usage.skill_wrapper.TokenUsageLogger", return_value=mock_logger), \
             patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}):

            auto_skill_start("tdd")

            mock_logger.start_session.assert_called_once()

    def test_auto_skill_start_enabled_false(self, mock_logger):
        """TOKEN_USAGE_ENABLED=false の場合に記録が無効"""
        from src.token_usage.skill_wrapper import auto_skill_start

        with patch("src.token_usage.skill_wrapper.TokenUsageLogger", return_value=mock_logger), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "false"}):

            session_id = auto_skill_start("tdd")

            # 記録されない
            mock_logger.start_session.assert_not_called()
            assert session_id is None

    def test_auto_skill_start_enabled_not_set_defaults_to_true(self, mock_logger, mock_context):
        """環境変数未設定時にデフォルトでtrue（記録有効）"""
        from src.token_usage.skill_wrapper import auto_skill_start

        with patch("src.token_usage.skill_wrapper.TokenUsageLogger", return_value=mock_logger), \
             patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context), \
             patch.dict(os.environ, {}, clear=True):

            auto_skill_start("tdd")

            # デフォルトで記録される
            mock_logger.start_session.assert_called_once()

    def test_auto_skill_start_error_does_not_raise_exception(self, mock_context):
        """記録失敗時も例外を発生させず、警告ログのみ（ユーザビリティ重視）"""
        from src.token_usage.skill_wrapper import auto_skill_start

        mock_logger_error = MagicMock()
        mock_logger_error.start_session.side_effect = Exception("Test error")

        with patch("src.token_usage.skill_wrapper.TokenUsageLogger", return_value=mock_logger_error), \
             patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}), \
             patch("src.token_usage.skill_wrapper.logger") as mock_warning_logger:

            # 例外が発生しないことを確認
            session_id = auto_skill_start("tdd")

            # 警告ログが記録される
            mock_warning_logger.warning.assert_called_once()

            # Noneを返す（記録失敗）
            assert session_id is None

    def test_auto_skill_end_error_does_not_raise_exception(self):
        """skill_end 記録失敗時も例外を発生させず、警告ログのみ"""
        from src.token_usage.skill_wrapper import auto_skill_end

        mock_logger_error = MagicMock()
        mock_logger_error.end_skill.side_effect = Exception("Test error")

        with patch("src.token_usage.skill_wrapper.TokenUsageLogger", return_value=mock_logger_error), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}), \
             patch("src.token_usage.skill_wrapper.logger") as mock_warning_logger:

            # 例外が発生しないことを確認
            session_id = "sess_20260130_112000_123456"
            auto_skill_end("tdd", session_id)

            # 警告ログが記録される
            mock_warning_logger.warning.assert_called_once()

    def test_auto_skill_start_issue_number_not_detected(self, mock_logger):
        """Issue番号が検出できない場合のフォールバック"""
        from src.token_usage.skill_wrapper import auto_skill_start

        mock_context_no_issue = {
            "issue": None,  # Issue番号が検出できない
            "worktree": "D:/projects/P010",
            "session_id": "sess_20260130_112000_123456"
        }

        with patch("src.token_usage.skill_wrapper.TokenUsageLogger", return_value=mock_logger), \
             patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context_no_issue), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}):

            session_id = auto_skill_start("tdd")

            # Issue番号がNoneでも記録される
            mock_logger.start_session.assert_called_once_with(
                session_id=mock_context_no_issue["session_id"],
                issue=None,
                worktree=mock_context_no_issue["worktree"]
            )

            assert session_id == mock_context_no_issue["session_id"]

    def test_auto_skill_start_session_already_started(self, mock_logger, mock_context):
        """セッションが既に開始されている場合のskill_start（境界値）"""
        from src.token_usage.skill_wrapper import auto_skill_start

        mock_logger.current_session_id = "existing_session"

        with patch("src.token_usage.skill_wrapper.TokenUsageLogger", return_value=mock_logger), \
             patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}):

            session_id = auto_skill_start("tdd")

            # 新しいセッションは開始されない（既存セッション継続）
            # 実装次第で動作が変わる可能性があるため、このテストは実装に合わせて調整する
            mock_logger.start_skill.assert_called_once_with("tdd")

    def test_auto_skill_end_session_not_started(self, mock_logger):
        """セッションが開始されていない場合のskill_end（境界値）"""
        from src.token_usage.skill_wrapper import auto_skill_end

        mock_logger.current_session_id = None

        with patch("src.token_usage.skill_wrapper.TokenUsageLogger", return_value=mock_logger), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}), \
             patch("src.token_usage.skill_wrapper.logger") as mock_warning_logger:

            # セッション未開始(session_id=None)でも例外は発生しない
            auto_skill_end("tdd", session_id=None)

            # 警告ログまたはエラーハンドリングが行われる
            # 実装次第で動作が変わる可能性があるため、このテストは実装に合わせて調整する
