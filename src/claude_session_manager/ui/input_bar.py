"""共通入力欄モジュール"""

import tkinter as tk
from typing import Callable, Optional


class InputBar:
    """共通入力欄"""

    def __init__(self, parent: tk.Widget, on_submit: Callable[[str], None]):
        """
        Args:
            parent: 親ウィジェット
            on_submit: 送信時のコールバック（入力テキストを引数に取る）
        """
        self.frame = tk.Frame(parent)
        self.on_submit = on_submit
        self.entry: Optional[tk.Entry] = None
        self.session_label: Optional[tk.Label] = None

    def setup_ui(self) -> None:
        """入力欄UIを構築する"""
        # 左: アクティブセッション名表示
        self.session_label = tk.Label(
            self.frame,
            text="Active: None",
            font=("Arial", 10, "bold"),
            width=20,
            anchor="w",
        )
        self.session_label.pack(side=tk.LEFT, padx=4)

        # 中央: テキスト入力欄
        self.entry = tk.Entry(self.frame, font=("Courier", 10))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # Enterキーで送信
        self.entry.bind("<Return>", lambda e: self.submit())

        # 右: 送信ボタン
        send_button = tk.Button(
            self.frame,
            text="Send",
            command=self.submit,
            width=10,
        )
        send_button.pack(side=tk.LEFT, padx=4)

    def set_active_session(self, session_id: str) -> None:
        """
        アクティブセッションを表示する

        Args:
            session_id: セッション識別子
        """
        if self.session_label:
            self.session_label.config(text=f"Active: {session_id}")

    def submit(self) -> None:
        """入力を送信する"""
        if not self.entry:
            return

        text = self.entry.get()

        # 空文字列の場合はコールバックを呼ばない
        if text and text.strip():
            self.on_submit(text)
            # 入力欄をクリア
            self.entry.delete(0, tk.END)
