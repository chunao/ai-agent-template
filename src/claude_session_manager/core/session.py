"""PowerShellセッション管理モジュール"""

import queue
import subprocess
import threading
from pathlib import Path
from typing import Optional


class PowerShellSession:
    """PowerShellプロセスを管理するクラス"""

    def __init__(self, session_id: str, working_dir: str):
        """
        Args:
            session_id: セッション識別子
            working_dir: 作業ディレクトリパス
        """
        self.session_id = session_id
        self.working_dir = working_dir
        self.process: Optional[subprocess.Popen] = None
        self._output_queue: queue.Queue = queue.Queue()
        self._output_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()

    def start(self) -> None:
        """PowerShellプロセスを起動する"""
        # 作業ディレクトリの存在確認
        working_path = Path(self.working_dir)
        if not working_path.exists():
            raise FileNotFoundError(f"Working directory not found: {self.working_dir}")

        # PowerShellプロセスを起動
        self.process = subprocess.Popen(
            ["powershell", "-NoLogo", "-NoProfile", "-NonInteractive"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # 行バッファリング
            cwd=self.working_dir,
        )

        # 出力読み取りスレッドを起動
        self._stop_flag.clear()
        self._output_thread = threading.Thread(
            target=self._read_output_loop, daemon=True
        )
        self._output_thread.start()

    def send_command(self, command: str) -> None:
        """
        コマンドをPowerShellに送信する

        Args:
            command: 実行するコマンド

        Raises:
            RuntimeError: セッションが実行中でない場合
            ValueError: コマンドが空文字列の場合
        """
        if not self.is_running():
            raise RuntimeError("Session is not running")

        if not command or command.strip() == "":
            raise ValueError("Command cannot be empty")

        if self.process and self.process.stdin:
            # clsコマンドの場合は特別な制御シーケンスとしてマーク
            if command.strip().lower() == "cls" or command.strip().lower() == "clear":
                self._output_queue.put("[CLEAR_SCREEN]\n")

            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

    def get_output(self) -> str:
        """
        出力を取得する（非ブロッキング）

        Returns:
            キューに溜まっている出力（複数行を結合）
        """
        output_lines = []
        try:
            while True:
                line = self._output_queue.get_nowait()
                output_lines.append(line)
        except queue.Empty:
            pass

        return "".join(output_lines)

    def stop(self) -> None:
        """プロセスを停止する"""
        if self.process:
            self._stop_flag.set()
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()

            self.process = None

        # スレッドの終了を待つ
        if self._output_thread and self._output_thread.is_alive():
            self._output_thread.join(timeout=1)
            self._output_thread = None

    def is_running(self) -> bool:
        """
        プロセスが実行中かチェックする

        Returns:
            実行中ならTrue
        """
        if self.process is None:
            return False
        return self.process.poll() is None

    def _read_output_loop(self) -> None:
        """出力読み取りループ（別スレッドで実行）"""
        if not self.process or not self.process.stdout:
            return

        while not self._stop_flag.is_set() and self.is_running():
            try:
                line = self.process.stdout.readline()
                if line:
                    self._output_queue.put(line)
                else:
                    # 出力がない場合は少し待つ
                    self._stop_flag.wait(0.1)
            except Exception:
                # エラー時はループを抜ける
                break
