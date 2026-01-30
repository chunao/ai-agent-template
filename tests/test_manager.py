"""SessionManagerクラスのテスト"""

from unittest.mock import MagicMock, patch

import pytest


class TestSessionManager:
    """SessionManagerクラスのテスト"""

    def test_manager_initialization(self):
        """マネージャーが正しく初期化される"""
        from claude_session_manager.core.manager import SessionManager

        manager = SessionManager(max_sessions=4)
        assert manager.max_sessions == 4
        assert len(manager.sessions) == 0

    @patch("claude_session_manager.core.manager.PowerShellSession")
    def test_create_session_success(self, mock_session_class):
        """セッション作成が成功する"""
        from claude_session_manager.core.manager import SessionManager

        # モックセッションを設定
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        manager = SessionManager(max_sessions=4)
        session = manager.create_session("session-1", ".")

        assert session is not None
        assert "session-1" in manager.sessions
        assert manager.sessions["session-1"] == session
        mock_session_class.assert_called_once_with("session-1", ".")

    @patch("claude_session_manager.core.manager.PowerShellSession")
    def test_get_session_success(self, mock_session_class):
        """セッション取得が成功する"""
        from claude_session_manager.core.manager import SessionManager

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        manager = SessionManager(max_sessions=4)
        created_session = manager.create_session("session-1", ".")
        retrieved_session = manager.get_session("session-1")

        assert retrieved_session == created_session

    def test_get_nonexistent_session(self):
        """存在しないセッションの取得がNoneを返す"""
        from claude_session_manager.core.manager import SessionManager

        manager = SessionManager(max_sessions=4)
        session = manager.get_session("nonexistent")

        assert session is None

    @patch("claude_session_manager.core.manager.PowerShellSession")
    def test_delete_session_success(self, mock_session_class):
        """セッション削除が成功する"""
        from claude_session_manager.core.manager import SessionManager

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        manager = SessionManager(max_sessions=4)
        manager.create_session("session-1", ".")
        manager.delete_session("session-1")

        assert "session-1" not in manager.sessions
        mock_session.stop.assert_called_once()

    def test_delete_nonexistent_session(self):
        """存在しないセッションの削除がエラーになる"""
        from claude_session_manager.core.manager import SessionManager

        manager = SessionManager(max_sessions=4)

        with pytest.raises(KeyError):
            manager.delete_session("nonexistent")

    @patch("claude_session_manager.core.manager.PowerShellSession")
    def test_list_sessions(self, mock_session_class):
        """セッション一覧が正しく取得できる"""
        from claude_session_manager.core.manager import SessionManager

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        manager = SessionManager(max_sessions=4)
        manager.create_session("session-1", ".")
        manager.create_session("session-2", ".")

        session_list = manager.list_sessions()
        assert len(session_list) == 2
        assert "session-1" in session_list
        assert "session-2" in session_list

    @patch("claude_session_manager.core.manager.PowerShellSession")
    def test_create_session_exceeds_limit(self, mock_session_class):
        """最大セッション数を超える作成がエラーになる"""
        from claude_session_manager.core.manager import SessionManager

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        manager = SessionManager(max_sessions=2)
        manager.create_session("session-1", ".")
        manager.create_session("session-2", ".")

        with pytest.raises(RuntimeError):
            manager.create_session("session-3", ".")

    @patch("claude_session_manager.core.manager.PowerShellSession")
    def test_create_duplicate_session_id(self, mock_session_class):
        """重複IDでのセッション作成がエラーになる"""
        from claude_session_manager.core.manager import SessionManager

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        manager = SessionManager(max_sessions=4)
        manager.create_session("session-1", ".")

        with pytest.raises(ValueError):
            manager.create_session("session-1", ".")

    @patch("claude_session_manager.core.manager.PowerShellSession")
    def test_create_at_max_sessions(self, mock_session_class):
        """最大セッション数ちょうどの作成が成功する"""
        from claude_session_manager.core.manager import SessionManager

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        manager = SessionManager(max_sessions=2)
        manager.create_session("session-1", ".")
        manager.create_session("session-2", ".")

        assert len(manager.sessions) == 2

    @patch("claude_session_manager.core.manager.PowerShellSession")
    def test_delete_all_sessions(self, mock_session_class):
        """全セッション削除後の状態が正しい"""
        from claude_session_manager.core.manager import SessionManager

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        manager = SessionManager(max_sessions=4)
        manager.create_session("session-1", ".")
        manager.create_session("session-2", ".")

        manager.delete_session("session-1")
        manager.delete_session("session-2")

        assert len(manager.sessions) == 0
        assert manager.list_sessions() == []
