"""インタラクティブPowerShellセッション（Windows専用）"""

import os
import platform
import queue
import threading
import time
from typing import Optional

# Windows環境でのみpywinptyをインポート
if platform.system() == "Windows":
    try:
        from pywinpty import PtyProcess

        PYWINPTY_AVAILABLE = True
    except ImportError:
        PYWINPTY_AVAILABLE = False
        PtyProcess = None  # type: ignore
else:
    PYWINPTY_AVAILABLE = False
    PtyProcess = None  # type: ignore


class InteractivePowerShellSession:
    """インタラクティブPowerShellセッション（Windows専用）"""

    def __init__(self, session_id: str, working_dir: str):
        """
        Args:
            session_id: セッション識別子
            working_dir: 作業ディレクトリパス

        Raises:
            RuntimeError: Windows以外のOSで実行した場合、
                         またはpywinptyが利用不可の場合
        """
        # OS検知
        if platform.system() != "Windows":
            raise RuntimeError(
                "InteractivePowerShellSession is only supported on Windows. "
                f"Current OS: {platform.system()}"
            )

        # pywinpty可用性チェック
        if not PYWINPTY_AVAILABLE:
            raise RuntimeError(
                "pywinpty is not available. "
                "Please install it: pip install pywinpty"
            )

        self.session_id = session_id
        self.working_dir = working_dir
        self.env = os.environ.copy()  # 環境変数を完全継承
        self.process: Optional[PtyProcess] = None

        # タイムアウト制御用
        self._output_queue: queue.Queue = queue.Queue()
        self._output_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()

    def start(self) -> None:
        """疑似端末でPowerShellを起動"""
        try:
            self.process = PtyProcess.spawn(
                ["powershell", "-NoLogo", "-NoProfile"],
                cwd=self.working_dir,
                env=self.env,
            )
        except FileNotFoundError:
            raise RuntimeError("PowerShell not found in PATH")
        except Exception as e:
            raise RuntimeError(f"Failed to start interactive session: {e}")

        # 出力読み取りスレッドを起動
        # バックグラウンドでプロセスの出力を継続的に読み取り、
        # キューに格納することでタイムアウト制御を実現
        self._stop_flag.clear()
        self._output_thread = threading.Thread(
            target=self._read_output_loop, daemon=True
        )
        self._output_thread.start()

    def _read_output_loop(self) -> None:
        """バックグラウンドで出力を読み取り、キューに格納

        このメソッドは別スレッドで実行され、プロセスの出力を
        ノンブロッキングで継続的に読み取ります。
        """
        while not self._stop_flag.is_set() and self.process:
            try:
                # ノンブロッキングで1024バイトずつ読み取り
                chunk = self.process.read(1024)
                if chunk:
                    self._output_queue.put(chunk)
            except Exception:
                break

    def send_command(self, command: str) -> None:
        """コマンドを送信

        Args:
            command: 実行するコマンド

        Raises:
            RuntimeError: セッションが実行中でない場合
        """
        if not self.is_running():
            raise RuntimeError("Session is not running")
        self.process.write(command + "\n")

    def read_output(self, timeout: Optional[int] = None) -> str:
        """出力を読み取り（タイムアウト付き）

        Args:
            timeout: タイムアウト秒数（Noneの場合は即座に返す）

        Returns:
            読み取った出力（タイムアウト時は現在までのバッファ）

        Raises:
            RuntimeError: セッションが実行中でない場合
        """
        if not self.is_running():
            raise RuntimeError("Session is not running")

        output_chunks = []

        if timeout is None:
            # タイムアウトなし：現在のキューをすべて取得
            while not self._output_queue.empty():
                try:
                    output_chunks.append(self._output_queue.get_nowait())
                except queue.Empty:
                    break
        else:
            # タイムアウトあり：指定時間待機して取得
            end_time = time.time() + timeout
            while time.time() < end_time:
                try:
                    chunk = self._output_queue.get(timeout=0.1)
                    output_chunks.append(chunk)
                except queue.Empty:
                    continue

        return "".join(output_chunks)

    def is_running(self) -> bool:
        """セッションが実行中か確認

        Returns:
            実行中の場合True、それ以外の場合False
        """
        return self.process is not None and self.process.isalive()

    def stop(self) -> None:
        """セッションを終了

        出力読み取りスレッドを停止し、プロセスを終了します。
        """
        self._stop_flag.set()

        if self._output_thread and self._output_thread.is_alive():
            self._output_thread.join(timeout=2)

        if self.process:
            try:
                self.process.terminate(force=True)
            except Exception:
                pass
