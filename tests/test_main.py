"""main.pyのテスト"""

from unittest.mock import MagicMock, patch

import pytest


class TestMain:
    """main()関数のテスト"""

    @patch("claude_session_manager.main.MainWindow")
    @patch("claude_session_manager.main.SessionManager")
    def test_main_creates_manager_and_window(self, mock_manager_class, mock_window_class):
        """main()がSessionManagerとMainWindowを作成する"""
        from claude_session_manager.main import main

        # モックを設定
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_window = MagicMock()
        mock_window_class.return_value = mock_window

        main()

        # SessionManagerが作成された
        mock_manager_class.assert_called_once()
        # MainWindowが作成された
        mock_window_class.assert_called_once_with(mock_manager)
        # setup_ui()とrun()が呼ばれた
        mock_window.setup_ui.assert_called_once()
        mock_window.run.assert_called_once()

    @patch("claude_session_manager.main.SessionManagerConfig")
    @patch("claude_session_manager.main.MainWindow")
    @patch("claude_session_manager.main.SessionManager")
    def test_main_uses_config(
        self, mock_manager_class, mock_window_class, mock_config_class
    ):
        """main()が設定を使用する"""
        from claude_session_manager.main import main

        # モック設定
        mock_config = MagicMock()
        mock_config.max_sessions = 4
        mock_config_class.return_value = mock_config

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_window = MagicMock()
        mock_window_class.return_value = mock_window

        main()

        # 設定が読み込まれた
        mock_config_class.assert_called_once()
        # SessionManagerに設定が渡された
        mock_manager_class.assert_called_once_with(max_sessions=mock_config.max_sessions)
