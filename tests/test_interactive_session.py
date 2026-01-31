"""InteractivePowerShellSessionのテスト"""

import platform
import queue
import pytest
from unittest.mock import patch, MagicMock

from claude_session_manager.core.interactive_session import (
    InteractivePowerShellSession,
    PYWINPTY_AVAILABLE,
)


# Windows専用テストマーカー
windows_only = pytest.mark.skipif(
    platform.system() != "Windows",
    reason="InteractivePowerShellSession is Windows-only",
)

# 統合テストマーカー
integration = pytest.mark.integration


class TestInteractivePowerShellSession:
    """InteractivePowerShellSessionのテスト"""

    def test_non_windows_raises_error(self):
        """Windows以外のOSでエラーが発生することを確認"""
        if platform.system() == "Windows":
            pytest.skip("This test is for non-Windows platforms")

        with pytest.raises(RuntimeError, match="only supported on Windows"):
            InteractivePowerShellSession("test-session", ".")

    @windows_only
    def test_pywinpty_unavailable_raises_error(self):
        """pywinpty利用不可時にエラーが発生することを確認"""
        with patch(
            "claude_session_manager.core.interactive_session.PYWINPTY_AVAILABLE",
            False,
        ):
            with pytest.raises(RuntimeError, match="pywinpty is not available"):
                InteractivePowerShellSession("test-session", ".")

    @windows_only
    @patch("claude_session_manager.core.interactive_session.PYWINPTY_AVAILABLE", True)
    @patch("claude_session_manager.core.interactive_session.PtyProcess")
    def test_start_success(self, mock_ptyprocess):
        """起動成功テスト（モック）"""
        mock_process = MagicMock()
        mock_process.isalive.return_value = True
        mock_ptyprocess.spawn.return_value = mock_process

        session = InteractivePowerShellSession("test-session", ".")
        session.start()

        assert session.is_running()
        mock_ptyprocess.spawn.assert_called_once()

        # スレッドの起動確認
        assert session._output_thread is not None
        assert session._output_thread.is_alive()

        session.stop()

    @windows_only
    @patch("claude_session_manager.core.interactive_session.PYWINPTY_AVAILABLE", True)
    @patch("claude_session_manager.core.interactive_session.PtyProcess")
    def test_send_command_when_not_running_raises_error(self, mock_ptyprocess):
        """セッション未起動時のコマンド送信でエラー"""
        session = InteractivePowerShellSession("test-session", ".")
        # start()を呼ばない

        with pytest.raises(RuntimeError, match="Session is not running"):
            session.send_command("test")

    @windows_only
    @patch("claude_session_manager.core.interactive_session.PYWINPTY_AVAILABLE", True)
    @patch("claude_session_manager.core.interactive_session.PtyProcess")
    def test_read_output_when_not_running_raises_error(self, mock_ptyprocess):
        """セッション未起動時の出力読み取りでエラー"""
        session = InteractivePowerShellSession("test-session", ".")
        # start()を呼ばない

        with pytest.raises(RuntimeError, match="Session is not running"):
            session.read_output()

    @windows_only
    @patch("claude_session_manager.core.interactive_session.PYWINPTY_AVAILABLE", True)
    @patch("claude_session_manager.core.interactive_session.PtyProcess")
    def test_read_output_with_timeout(self, mock_ptyprocess):
        """タイムアウト付き出力読み取りテスト"""
        mock_process = MagicMock()
        mock_process.isalive.return_value = True
        mock_process.read.return_value = ""  # 空文字列を返すようにモック
        mock_ptyprocess.spawn.return_value = mock_process

        session = InteractivePowerShellSession("test-session", ".")
        session.start()

        # キューに出力を追加
        session._output_queue.put("test output")

        # タイムアウト指定で読み取り
        output = session.read_output(timeout=1)
        assert "test output" in output

        session.stop()

    @windows_only
    @patch("claude_session_manager.core.interactive_session.PYWINPTY_AVAILABLE", True)
    @patch("claude_session_manager.core.interactive_session.PtyProcess")
    def test_read_output_without_timeout(self, mock_ptyprocess):
        """タイムアウトなし（即座に返す)での出力読み取りテスト"""
        mock_process = MagicMock()
        mock_process.isalive.return_value = True
        mock_process.read.return_value = ""  # 空文字列を返すようにモック
        mock_ptyprocess.spawn.return_value = mock_process

        session = InteractivePowerShellSession("test-session", ".")
        session.start()

        # キューに出力を追加
        session._output_queue.put("output1")
        session._output_queue.put("output2")

        # タイムアウトなしで読み取り
        output = session.read_output(timeout=None)
        assert "output1" in output
        assert "output2" in output

        session.stop()

    @windows_only
    @patch("claude_session_manager.core.interactive_session.PYWINPTY_AVAILABLE", True)
    @patch("claude_session_manager.core.interactive_session.PtyProcess")
    def test_stop_terminates_process(self, mock_ptyprocess):
        """stop()でプロセスが終了することを確認"""
        mock_process = MagicMock()
        mock_process.isalive.return_value = True
        mock_ptyprocess.spawn.return_value = mock_process

        session = InteractivePowerShellSession("test-session", ".")
        session.start()

        session.stop()

        # 停止フラグがセットされている
        assert session._stop_flag.is_set()
        # プロセスのterminateが呼ばれている
        mock_process.terminate.assert_called_once()

    @integration
    @windows_only
    @pytest.mark.timeout(10)
    def test_basic_command_execution(self):
        """基本的なコマンド実行テスト（統合テスト）"""
        if not PYWINPTY_AVAILABLE:
            pytest.skip("pywinpty not available")

        session = InteractivePowerShellSession("test-session", ".")
        session.start()

        # シンプルな計算コマンド
        session.send_command("1+1")
        output = session.read_output(timeout=5)
        assert "2" in output

        session.stop()

    @integration
    @windows_only
    @pytest.mark.timeout(10)
    def test_environment_variable_inheritance(self):
        """環境変数継承テスト（統合テスト）"""
        if not PYWINPTY_AVAILABLE:
            pytest.skip("pywinpty not available")

        session = InteractivePowerShellSession("test-session", ".")
        session.start()

        # PATH環境変数の確認
        session.send_command("$env:PATH")
        output = session.read_output(timeout=5)
        # 何らかのパスが含まれていることを確認
        assert len(output) > 0

        session.stop()
