"""セッションパネルモジュール"""

import tkinter as tk
from tkinter import scrolledtext
from typing import Callable, Optional

from ..core.session import PowerShellSession


class SessionPanel:
    """セッション表示パネル"""

    def __init__(
        self,
        parent: tk.Widget,
        session: PowerShellSession,
        on_click: Callable[[], None],
    ):
        """
        Args:
            parent: 親ウィジェット
            session: PowerShellSession
            on_click: クリック時のコールバック
        """
        self.frame = tk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        self.session = session
        self.on_click = on_click
        self.output_text: Optional[scrolledtext.ScrolledText] = None

    def setup_ui(self) -> None:
        """パネルUIを構築する"""
        # クリックイベントをバインド
        self.frame.bind("<Button-1>", lambda e: self.on_click())

        # 上部: セッション情報
        info_frame = tk.Frame(self.frame)
        info_frame.pack(fill=tk.X, padx=4, pady=4)

        session_label = tk.Label(
            info_frame,
            text=f"Session: {self.session.session_id}",
            font=("Arial", 10, "bold"),
        )
        session_label.pack(side=tk.LEFT)

        dir_label = tk.Label(
            info_frame,
            text=f"Working Dir: {self.session.working_dir}",
            font=("Arial", 8),
            fg="gray",
        )
        dir_label.pack(side=tk.LEFT, padx=8)

        # 中央: 出力テキスト（スクロール可能）
        self.output_text = scrolledtext.ScrolledText(
            self.frame,
            wrap=tk.WORD,
            width=40,
            height=15,
            font=("Courier", 9),
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.output_text.bind("<Button-1>", lambda e: self.on_click())

        # 下部: 制御ボタン
        button_frame = tk.Frame(self.frame)
        button_frame.pack(fill=tk.X, padx=4, pady=4)

        start_button = tk.Button(
            button_frame,
            text="Start",
            command=self._on_start,
            width=8,
        )
        start_button.pack(side=tk.LEFT, padx=2)

        stop_button = tk.Button(
            button_frame,
            text="Stop",
            command=self._on_stop,
            width=8,
        )
        stop_button.pack(side=tk.LEFT, padx=2)

    def update_output(self) -> None:
        """出力を更新する（定期的に呼び出し）"""
        if not self.output_text:
            return

        output = self.session.get_output()
        if output:
            # [CLEAR_SCREEN]マーカーを検出して画面をクリア
            if "[CLEAR_SCREEN]" in output:
                self.output_text.delete("1.0", tk.END)
                # マーカーを除去した残りの出力を表示
                output = output.replace("[CLEAR_SCREEN]\n", "")

            if output:  # マーカー除去後も出力がある場合のみ挿入
                self.output_text.insert(tk.END, output)
                self.output_text.see(tk.END)  # 最下部にスクロール

    def _on_start(self) -> None:
        """Startボタン押下時のハンドラー"""
        if not self.session.is_running():
            try:
                self.session.start()
                if self.output_text:
                    import os
                    cwd = os.path.abspath(self.session.working_dir)
                    self.output_text.insert(
                        tk.END, f"[Session started: {self.session.session_id}]\n"
                    )
                    # PowerShellプロンプト風の表示
                    self.output_text.insert(
                        tk.END, f"PS {cwd}> "
                    )
            except Exception as e:
                if self.output_text:
                    self.output_text.insert(tk.END, f"[Error: {e}]\n")

    def _on_stop(self) -> None:
        """Stopボタン押下時のハンドラー"""
        if self.session.is_running():
            self.session.stop()
            if self.output_text:
                # 出力エリアをクリア
                self.output_text.delete("1.0", tk.END)
                self.output_text.insert(
                    tk.END, f"[Session stopped: {self.session.session_id}]\n"
                )
