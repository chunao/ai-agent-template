"""セッションマネージャーモジュール"""

from typing import Optional, Union

from .session import PowerShellSession
from .interactive_session import (
    InteractivePowerShellSession,
    PYWINPTY_AVAILABLE,
)


class SessionManager:
    """複数のPowerShellSessionを管理するクラス"""

    def __init__(self, max_sessions: int = 4):
        """
        Args:
            max_sessions: 最大セッション数
        """
        self.max_sessions = max_sessions
        self.sessions: dict[
            str, Union[PowerShellSession, InteractivePowerShellSession]
        ] = {}

    def create_session(
        self, session_id: str, working_dir: str, interactive: bool = False
    ) -> Union[PowerShellSession, InteractivePowerShellSession]:
        """
        新規セッションを作成する

        Args:
            session_id: セッション識別子
            working_dir: 作業ディレクトリパス
            interactive: インタラクティブモードを使用するか（デフォルト: False）

        Returns:
            作成されたセッション（PowerShellSession または InteractivePowerShellSession）

        Raises:
            RuntimeError: 最大セッション数を超える場合、
                         またはインタラクティブモードが利用不可の場合
            ValueError: 重複したセッションIDの場合
        """
        if len(self.sessions) >= self.max_sessions:
            raise RuntimeError(
                f"Maximum session limit reached: {self.max_sessions}"
            )

        if session_id in self.sessions:
            raise ValueError(f"Session ID already exists: {session_id}")

        # インタラクティブモード判定
        if interactive:
            if not PYWINPTY_AVAILABLE:
                raise RuntimeError(
                    "Interactive mode is not available. "
                    "pywinpty is required (Windows only)."
                )
            session = InteractivePowerShellSession(session_id, working_dir)
        else:
            session = PowerShellSession(session_id, working_dir)

        self.sessions[session_id] = session
        return session

    def get_session(
        self, session_id: str
    ) -> Optional[Union[PowerShellSession, InteractivePowerShellSession]]:
        """
        セッションを取得する

        Args:
            session_id: セッション識別子

        Returns:
            PowerShellSession または InteractivePowerShellSession、
            存在しない場合はNone
        """
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str) -> None:
        """
        セッションを削除する

        Args:
            session_id: セッション識別子

        Raises:
            KeyError: セッションが存在しない場合
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session not found: {session_id}")

        session = self.sessions[session_id]
        session.stop()
        del self.sessions[session_id]

    def list_sessions(self) -> list[str]:
        """
        セッション一覧を取得する

        Returns:
            セッションIDのリスト
        """
        return list(self.sessions.keys())
