"""UIコンポーネントのテスト"""

import tkinter as tk
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestMainWindow:
    """MainWindowクラスのテスト"""

    @patch("tkinter.Tk")
    def test_main_window_initialization(self, mock_tk):
        """メインウィンドウが正しく初期化される"""
        from claude_session_manager.core.manager import SessionManager
        from claude_session_manager.ui.main_window import MainWindow

        manager = SessionManager(max_sessions=4)
        window = MainWindow(manager)

        assert window.session_manager == manager
        assert window.session_panels == []
        assert window.active_session_id is None

    @patch("tkinter.Tk")
    @patch("claude_session_manager.ui.session_panel.SessionPanel")
    @patch("claude_session_manager.ui.input_bar.InputBar")
    def test_setup_ui_creates_grid(self, mock_input_bar, mock_session_panel, mock_tk):
        """setup_ui()が2x2グリッドを作成する"""
        from claude_session_manager.core.manager import SessionManager
        from claude_session_manager.ui.main_window import MainWindow

        manager = SessionManager(max_sessions=4)
        window = MainWindow(manager)
        window.setup_ui()

        # 4つのSessionPanelが作成される
        assert len(window.session_panels) == 4
        # InputBarが作成される
        assert window.input_bar is not None

    @patch("tkinter.Tk")
    def test_set_active_session(self, mock_tk):
        """アクティブセッションが正しく設定される"""
        from claude_session_manager.core.manager import SessionManager
        from claude_session_manager.ui.main_window import MainWindow

        manager = SessionManager(max_sessions=4)
        window = MainWindow(manager)
        window.set_active_session("session-1")

        assert window.active_session_id == "session-1"


class TestSessionPanel:
    """SessionPanelクラスのテスト"""

    @patch("tkinter.Frame")
    def test_session_panel_initialization(self, mock_frame):
        """SessionPanelが正しく初期化される"""
        from claude_session_manager.ui.session_panel import SessionPanel

        mock_parent = MagicMock()
        mock_session = MagicMock()
        mock_session.session_id = "test-session"
        mock_session.working_dir = "."

        panel = SessionPanel(mock_parent, mock_session, on_click=lambda: None)

        assert panel.session == mock_session
        assert callable(panel.on_click)

    @patch("tkinter.Frame")
    @patch("tkinter.Label")
    @patch("tkinter.Text")
    @patch("tkinter.Scrollbar")
    @patch("tkinter.Button")
    def test_setup_ui_creates_components(
        self, mock_button, mock_scrollbar, mock_text, mock_label, mock_frame
    ):
        """setup_ui()が必要なコンポーネントを作成する"""
        from claude_session_manager.ui.session_panel import SessionPanel

        mock_parent = MagicMock()
        mock_session = MagicMock()
        mock_session.session_id = "test-session"
        mock_session.working_dir = "."

        panel = SessionPanel(mock_parent, mock_session, on_click=lambda: None)
        panel.setup_ui()

        # UI要素が作成されたか確認
        assert panel.output_text is not None

    @patch("tkinter.Frame")
    def test_update_output(self, mock_frame):
        """update_output()が出力を更新する"""
        from claude_session_manager.ui.session_panel import SessionPanel

        mock_parent = MagicMock()
        mock_session = MagicMock()
        mock_session.session_id = "test-session"
        mock_session.working_dir = "."
        mock_session.get_output.return_value = "Test output"

        panel = SessionPanel(mock_parent, mock_session, on_click=lambda: None)
        panel.output_text = MagicMock()

        panel.update_output()

        # get_output()が呼ばれたか確認
        mock_session.get_output.assert_called()

    @patch("tkinter.Frame")
    def test_on_click_callback(self, mock_frame):
        """クリック時にコールバックが呼ばれる"""
        from claude_session_manager.ui.session_panel import SessionPanel

        mock_parent = MagicMock()
        mock_session = MagicMock()
        mock_session.session_id = "test-session"
        mock_session.working_dir = "."

        callback_called = False

        def on_click_handler():
            nonlocal callback_called
            callback_called = True

        panel = SessionPanel(mock_parent, mock_session, on_click=on_click_handler)
        panel.on_click()

        assert callback_called


class TestInputBar:
    """InputBarクラスのテスト"""

    @patch("tkinter.Frame")
    def test_input_bar_initialization(self, mock_frame):
        """InputBarが正しく初期化される"""
        from claude_session_manager.ui.input_bar import InputBar

        mock_parent = MagicMock()
        on_submit = lambda text: None

        input_bar = InputBar(mock_parent, on_submit)

        assert callable(input_bar.on_submit)

    @patch("tkinter.Frame")
    @patch("tkinter.Label")
    @patch("tkinter.Entry")
    @patch("tkinter.Button")
    def test_setup_ui_creates_components(
        self, mock_button, mock_entry, mock_label, mock_frame
    ):
        """setup_ui()が必要なコンポーネントを作成する"""
        from claude_session_manager.ui.input_bar import InputBar

        mock_parent = MagicMock()
        on_submit = lambda text: None

        input_bar = InputBar(mock_parent, on_submit)
        input_bar.setup_ui()

        assert input_bar.entry is not None
        assert input_bar.session_label is not None

    @patch("tkinter.Frame")
    def test_set_active_session_updates_label(self, mock_frame):
        """set_active_session()がラベルを更新する"""
        from claude_session_manager.ui.input_bar import InputBar

        mock_parent = MagicMock()
        on_submit = lambda text: None

        input_bar = InputBar(mock_parent, on_submit)
        input_bar.session_label = MagicMock()

        input_bar.set_active_session("session-1")

        # ラベルの更新が呼ばれたか確認
        input_bar.session_label.config.assert_called()

    @patch("tkinter.Frame")
    def test_submit_calls_callback(self, mock_frame):
        """submit()がコールバックを呼ぶ"""
        from claude_session_manager.ui.input_bar import InputBar

        mock_parent = MagicMock()
        submitted_text = None

        def on_submit_handler(text):
            nonlocal submitted_text
            submitted_text = text

        input_bar = InputBar(mock_parent, on_submit_handler)
        input_bar.entry = MagicMock()
        input_bar.entry.get.return_value = "test command"

        input_bar.submit()

        assert submitted_text == "test command"
        # 入力欄がクリアされたか確認
        input_bar.entry.delete.assert_called()

    @patch("tkinter.Frame")
    def test_submit_empty_text(self, mock_frame):
        """空のテキストでsubmit()を呼んでも問題ない"""
        from claude_session_manager.ui.input_bar import InputBar

        mock_parent = MagicMock()
        callback_called = False

        def on_submit_handler(text):
            nonlocal callback_called
            callback_called = True

        input_bar = InputBar(mock_parent, on_submit_handler)
        input_bar.entry = MagicMock()
        input_bar.entry.get.return_value = ""

        input_bar.submit()

        # 空文字列でもコールバックは呼ばれる（または呼ばれない設計も可）
        # ここでは呼ばれないことを期待
        assert not callback_called or submitted_text == ""
