"""メインエントリーポイント"""

from .config import SessionManagerConfig
from .core.manager import SessionManager
from .ui.main_window import MainWindow


def main() -> None:
    """メイン関数"""
    # 設定を読み込み
    config = SessionManagerConfig()

    # セッションマネージャーを作成
    manager = SessionManager(max_sessions=config.max_sessions)

    # メインウィンドウを作成
    window = MainWindow(manager)
    window.setup_ui()
    window.run()


if __name__ == "__main__":
    main()
