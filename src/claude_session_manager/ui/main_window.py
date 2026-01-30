"""メインウィンドウモジュール"""

import tkinter as tk
from typing import Optional

from ..core.manager import SessionManager
from .input_bar import InputBar
from .session_panel import SessionPanel


class MainWindow:
    """メインウィンドウ（2x2グリッド）"""

    def __init__(self, session_manager: SessionManager):
        """
        Args:
            session_manager: セッションマネージャー
        """
        self.root = tk.Tk()
        self.session_manager = session_manager
        self.session_panels: list[SessionPanel] = []
        self.input_bar: Optional[InputBar] = None
        self.active_session_id: Optional[str] = None

    def setup_ui(self) -> None:
        """UIを構築する"""
        self.root.title("Claude Code Session Manager")
        self.root.geometry("1200x800")

        # メインフレーム
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 2x2グリッドフレーム
        grid_frame = tk.Frame(main_frame)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # 4つのセッションパネルを作成
        for i in range(4):
            row = i // 2
            col = i % 2

            # ダミーセッションを作成（後で実際のセッションに差し替え可能）
            session_id = f"session-{i+1}"
            try:
                session = self.session_manager.create_session(session_id, ".")
            except RuntimeError:
                # セッション数上限の場合は既存のセッションを使用
                session = self.session_manager.get_session(session_id)

            if session:
                panel = SessionPanel(
                    grid_frame,
                    session,
                    on_click=lambda sid=session_id: self.set_active_session(sid),
                )
                panel.setup_ui()
                panel.frame.grid(
                    row=row, column=col, sticky="nsew", padx=4, pady=4
                )
                self.session_panels.append(panel)

        # グリッドの重み設定（均等に分割）
        grid_frame.grid_rowconfigure(0, weight=1)
        grid_frame.grid_rowconfigure(1, weight=1)
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)

        # 下部の共通入力欄
        self.input_bar = InputBar(main_frame, self._on_input_submit)
        self.input_bar.setup_ui()
        self.input_bar.frame.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=8)

        # 最初のセッションをアクティブに設定
        if self.session_panels:
            self.set_active_session("session-1")

        # 定期的に出力を更新
        self._update_all_sessions()

    def set_active_session(self, session_id: str) -> None:
        """
        アクティブセッションを設定する

        Args:
            session_id: セッション識別子
        """
        self.active_session_id = session_id
        if self.input_bar:
            self.input_bar.set_active_session(session_id)

    def run(self) -> None:
        """メインループを開始する"""
        self.root.mainloop()

    def _on_input_submit(self, text: str) -> None:
        """
        入力送信時のコールバック

        Args:
            text: 入力されたテキスト
        """
        if not self.active_session_id:
            return

        session = self.session_manager.get_session(self.active_session_id)
        if session and session.is_running():
            try:
                session.send_command(text)
            except (RuntimeError, ValueError):
                pass  # エラーは無視（最小実装）

    def _update_all_sessions(self) -> None:
        """全セッションの出力を更新する（定期実行）"""
        for panel in self.session_panels:
            panel.update_output()

        # 100ms後に再実行
        self.root.after(100, self._update_all_sessions)
