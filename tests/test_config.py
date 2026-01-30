"""設定モジュールのテスト"""


class TestSessionManagerConfig:
    """SessionManagerConfigクラスのテスト"""

    def test_config_default_values(self):
        """デフォルト値が正しく設定される"""
        from claude_session_manager.config import SessionManagerConfig

        config = SessionManagerConfig()

        assert config.max_sessions == 4
        assert config.default_working_dir == "."
        assert config.output_buffer_size == 1000
        assert config.ui_update_interval_ms == 100
        assert config.window_width == 1200
        assert config.window_height == 800
        assert config.grid_spacing == 8
        assert config.button_min_size == (48, 48)
        assert config.font_size_min == 12

    def test_config_custom_values(self):
        """カスタム値で初期化できる"""
        from claude_session_manager.config import SessionManagerConfig

        config = SessionManagerConfig(
            max_sessions=8,
            default_working_dir="/tmp",
            ui_update_interval_ms=200,
        )

        assert config.max_sessions == 8
        assert config.default_working_dir == "/tmp"
        assert config.ui_update_interval_ms == 200
        # デフォルト値も保持される
        assert config.output_buffer_size == 1000
