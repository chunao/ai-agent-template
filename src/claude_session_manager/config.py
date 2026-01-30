"""設定管理モジュール"""

from dataclasses import dataclass


@dataclass
class SessionManagerConfig:
    """セッションマネージャー設定"""

    max_sessions: int = 4
    default_working_dir: str = "."
    output_buffer_size: int = 1000
    ui_update_interval_ms: int = 100
    window_width: int = 1200
    window_height: int = 800

    # GUI設計指針に基づく設定
    grid_spacing: int = 8  # 8ptグリッドシステム
    button_min_size: tuple[int, int] = (48, 48)  # アクセシビリティ基準
    font_size_min: int = 12  # 最小フォントサイズ
