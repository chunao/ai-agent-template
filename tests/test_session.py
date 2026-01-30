"""PowerShellSessionクラスのテスト"""

import subprocess
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


class TestPowerShellSession:
    """PowerShellSessionクラスのテスト"""

    def test_session_initialization(self):
        """セッションが正しく初期化される"""
        from claude_session_manager.core.session import PowerShellSession

        session = PowerShellSession("test-session", ".")
        assert session.session_id == "test-session"
        assert session.working_dir == "."
        assert session.process is None
        assert not session.is_running()

    @patch("subprocess.Popen")
    def test_session_start_success(self, mock_popen):
        """セッション起動が成功する"""
        from claude_session_manager.core.session import PowerShellSession

        # モックプロセスを設定
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # 実行中
        mock_process.stdout.readline.return_value = ""
        mock_popen.return_value = mock_process

        session = PowerShellSession("test-session", ".")
        session.start()

        assert session.is_running()
        assert session.process is not None
        mock_popen.assert_called_once()

    @patch("subprocess.Popen")
    def test_send_command_success(self, mock_popen):
        """コマンド送信が成功する"""
        from claude_session_manager.core.session import PowerShellSession

        # モックプロセスを設定
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdin = MagicMock()
        mock_process.stdout.readline.return_value = ""
        mock_popen.return_value = mock_process

        session = PowerShellSession("test-session", ".")
        session.start()
        session.send_command("echo 'Hello'")

        # stdinにコマンドが書き込まれたか確認
        mock_process.stdin.write.assert_called()
        mock_process.stdin.flush.assert_called()

    @patch("subprocess.Popen")
    def test_get_output_success(self, mock_popen):
        """出力が正しく取得できる"""
        from claude_session_manager.core.session import PowerShellSession

        # モックプロセスを設定
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdout.readline.side_effect = ["Hello\n", "World\n", ""]
        mock_popen.return_value = mock_process

        session = PowerShellSession("test-session", ".")
        session.start()

        # 出力読み取りスレッドが動作する時間を待つ
        time.sleep(0.1)

        output = session.get_output()
        assert isinstance(output, str)

    @patch("subprocess.Popen")
    def test_session_stop_success(self, mock_popen):
        """セッション停止が成功する"""
        from claude_session_manager.core.session import PowerShellSession

        # モックプロセスを設定
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdout.readline.return_value = ""
        mock_popen.return_value = mock_process

        session = PowerShellSession("test-session", ".")
        session.start()
        session.stop()

        assert not session.is_running()
        mock_process.terminate.assert_called()

    def test_session_start_with_invalid_directory(self):
        """存在しないディレクトリでの起動がエラーになる"""
        from claude_session_manager.core.session import PowerShellSession

        session = PowerShellSession("test-session", "/nonexistent/path")

        with pytest.raises((FileNotFoundError, OSError)):
            session.start()

    @patch("subprocess.Popen")
    def test_send_command_to_stopped_session(self, mock_popen):
        """停止済みセッションへのコマンド送信がエラーになる"""
        from claude_session_manager.core.session import PowerShellSession

        # モックプロセスを設定
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdout.readline.return_value = ""
        mock_popen.return_value = mock_process

        session = PowerShellSession("test-session", ".")
        session.start()
        session.stop()

        with pytest.raises(RuntimeError):
            session.send_command("echo 'test'")

    @patch("subprocess.Popen")
    def test_send_empty_command(self, mock_popen):
        """空文字列コマンドの送信を処理できる"""
        from claude_session_manager.core.session import PowerShellSession

        # モックプロセスを設定
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdin = MagicMock()
        mock_process.stdout.readline.return_value = ""
        mock_popen.return_value = mock_process

        session = PowerShellSession("test-session", ".")
        session.start()

        # 空コマンドは送信されないか、エラーにならない
        try:
            session.send_command("")
        except ValueError:
            # ValueError が期待される場合
            pass

    @patch("subprocess.Popen")
    def test_output_thread_cleanup_on_stop(self, mock_popen):
        """停止時に出力読み取りスレッドが正常終了する"""
        from claude_session_manager.core.session import PowerShellSession

        # モックプロセスを設定
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdout.readline.return_value = ""
        mock_popen.return_value = mock_process

        session = PowerShellSession("test-session", ".")
        session.start()

        # スレッドが起動していることを確認
        time.sleep(0.1)
        if hasattr(session, "_output_thread") and session._output_thread:
            assert session._output_thread.is_alive()

        session.stop()

        # スレッドが停止していることを確認（最大1秒待機）
        time.sleep(0.2)
        if hasattr(session, "_output_thread") and session._output_thread:
            assert not session._output_thread.is_alive()

    @patch("subprocess.Popen")
    def test_is_running_returns_correct_state(self, mock_popen):
        """is_running()が正しい状態を返す"""
        from claude_session_manager.core.session import PowerShellSession

        # モックプロセスを設定
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # 実行中
        mock_process.stdout.readline.return_value = ""
        mock_popen.return_value = mock_process

        session = PowerShellSession("test-session", ".")
        assert not session.is_running()

        session.start()
        assert session.is_running()

        # プロセスが停止したことをシミュレート
        mock_process.poll.return_value = 0
        assert not session.is_running()
