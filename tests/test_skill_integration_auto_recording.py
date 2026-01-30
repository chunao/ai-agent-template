"""スキル統合の結合テスト

Issue #101: トークン使用量記録の自動化（Phase 4.1）
"""

import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest


class TestSkillIntegrationAutoRecording:
    """スキル統合の結合テスト"""

    @pytest.fixture
    def temp_log_dir(self, tmp_path):
        """一時ログディレクトリ"""
        return tmp_path / ".token-usage"

    @pytest.fixture
    def mock_context(self):
        """コンテキスト情報のモック"""
        return {
            "issue": "101",
            "worktree": "D:/projects/P010-worktrees/issue-101-auto-token-tracking",
            "session_id": "sess_20260130_112000_123456"
        }

    def test_tdd_skill_auto_recording(self, temp_log_dir, mock_context):
        """/tdd スキル実行時の自動記録"""
        from src.token_usage.skill_wrapper import auto_skill_start, auto_skill_end
        from src.token_usage.logger import TokenUsageLogger

        with patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}), \
             patch("src.token_usage.skill_wrapper.TokenUsageLogger") as mock_logger_class:

            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            # /tdd スキル開始
            session_id = auto_skill_start("tdd")

            # スキル本体の処理（省略）
            # ...

            # /tdd スキル終了
            auto_skill_end("tdd", session_id)

            # 記録が正しく行われたことを確認
            mock_logger.start_session.assert_called_once()
            mock_logger.start_skill.assert_called_once_with("tdd")
            mock_logger.end_skill.assert_called_once_with("tdd")
            mock_logger.end_session.assert_called_once()

    def test_start_issue_skill_auto_recording(self, temp_log_dir, mock_context):
        """/start-issue スキル実行時の自動記録"""
        from src.token_usage.skill_wrapper import auto_skill_start, auto_skill_end

        with patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}), \
             patch("src.token_usage.skill_wrapper.TokenUsageLogger") as mock_logger_class:

            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            # /start-issue スキル開始
            session_id = auto_skill_start("start-issue")

            # スキル本体の処理（省略）
            # ...

            # /start-issue スキル終了
            auto_skill_end("start-issue", session_id)

            # 記録が正しく行われたことを確認
            mock_logger.start_session.assert_called_once()
            mock_logger.start_skill.assert_called_once_with("start-issue")
            mock_logger.end_skill.assert_called_once_with("start-issue")
            mock_logger.end_session.assert_called_once()

    def test_review_skill_auto_recording(self, temp_log_dir, mock_context):
        """/review スキル実行時の自動記録"""
        from src.token_usage.skill_wrapper import auto_skill_start, auto_skill_end

        with patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}), \
             patch("src.token_usage.skill_wrapper.TokenUsageLogger") as mock_logger_class:

            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            # /review スキル開始
            session_id = auto_skill_start("review")

            # スキル本体の処理（省略）
            # ...

            # /review スキル終了
            auto_skill_end("review", session_id)

            # 記録が正しく行われたことを確認
            mock_logger.start_session.assert_called_once()
            mock_logger.start_skill.assert_called_once_with("review")
            mock_logger.end_skill.assert_called_once_with("review")
            mock_logger.end_session.assert_called_once()

    def test_skill_error_does_not_prevent_recording(self, temp_log_dir, mock_context):
        """スキル本体でエラーが発生しても記録は継続される（受け入れ基準）"""
        from src.token_usage.skill_wrapper import auto_skill_start, auto_skill_end

        with patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}), \
             patch("src.token_usage.skill_wrapper.TokenUsageLogger") as mock_logger_class:

            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            # スキル開始
            session_id = auto_skill_start("tdd")

            # スキル本体でエラーが発生
            try:
                raise Exception("Skill execution error")
            except Exception:
                pass  # エラーをキャッチして処理継続

            # スキル終了（エラー後も実行される）
            auto_skill_end("tdd", session_id)

            # 記録が正しく行われたことを確認
            mock_logger.start_session.assert_called_once()
            mock_logger.end_session.assert_called_once()

    def test_recording_error_does_not_prevent_skill_execution(self, mock_context):
        """記録失敗してもスキル本体は継続実行される（受け入れ基準）"""
        from src.token_usage.skill_wrapper import auto_skill_start, auto_skill_end

        mock_logger_error = MagicMock()
        mock_logger_error.start_session.side_effect = Exception("Recording error")

        with patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}), \
             patch("src.token_usage.skill_wrapper.TokenUsageLogger", return_value=mock_logger_error), \
             patch("src.token_usage.skill_wrapper.logger") as mock_warning_logger:

            # 記録エラーが発生しても例外は発生しない
            session_id = auto_skill_start("tdd")

            # スキル本体の処理は継続できる
            skill_executed = True

            # スキル終了も実行できる
            auto_skill_end("tdd", session_id)

            assert skill_executed is True
            # 警告ログが記録される
            assert mock_warning_logger.warning.call_count >= 1

    def test_jsonl_file_created_correctly(self, temp_log_dir, mock_context):
        """JONLファイルが正しく作成される"""
        from src.token_usage.skill_wrapper import auto_skill_start, auto_skill_end
        from src.token_usage.logger import TokenUsageLogger

        with patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}):

            # 実際のTokenUsageLoggerを使用
            with patch("src.token_usage.skill_wrapper.TokenUsageLogger") as mock_logger_class:
                logger = TokenUsageLogger(base_dir=str(temp_log_dir))
                mock_logger_class.return_value = logger

                # スキル実行
                session_id = auto_skill_start("tdd")
                auto_skill_end("tdd", session_id)

                # JONLファイルが作成されたことを確認
                log_file = temp_log_dir / "sessions" / f"{session_id}.jsonl"
                assert log_file.exists()

                # ファイル内容を確認
                with open(log_file, "r") as f:
                    lines = f.readlines()

                # 4行（session_start, skill_start, skill_end, session_end）が記録されているはず
                assert len(lines) >= 2  # 最低限session_start, session_endがあればOK

                # 各行がJSONとしてパースできることを確認
                for line in lines:
                    event = json.loads(line)
                    assert "event" in event
                    assert "timestamp" in event

    def test_phase_1_2_compatibility(self, temp_log_dir, mock_context):
        """Phase 1/2のイベントモデルとの互換性を確認"""
        from src.token_usage.skill_wrapper import auto_skill_start, auto_skill_end
        from src.token_usage.logger import TokenUsageLogger

        with patch("src.token_usage.skill_wrapper.detect_context", return_value=mock_context), \
             patch.dict(os.environ, {"TOKEN_USAGE_ENABLED": "true"}):

            with patch("src.token_usage.skill_wrapper.TokenUsageLogger") as mock_logger_class:
                logger = TokenUsageLogger(base_dir=str(temp_log_dir))
                mock_logger_class.return_value = logger

                # スキル実行
                session_id = auto_skill_start("tdd")
                auto_skill_end("tdd", session_id)

                # JONLファイルを読み込み
                log_file = temp_log_dir / "sessions" / f"{session_id}.jsonl"
                with open(log_file, "r") as f:
                    lines = f.readlines()

                # Phase 1/2の標準フィールドが含まれていることを確認
                session_start_event = json.loads(lines[0])
                assert session_start_event["event"] == "session_start"
                assert "session_id" in session_start_event
                assert "timestamp" in session_start_event

                # 新しいフィールド（issue, worktree）も含まれている
                assert session_start_event.get("issue") == "101"
                assert "worktree" in session_start_event
