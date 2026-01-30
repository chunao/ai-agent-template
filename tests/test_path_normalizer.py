"""
プロジェクトパス正規化のテスト

Claude Codeのプロジェクトパス形式（D--projects-P010）とWindowsパス形式の相互変換をテストする。
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from claude_session_manager.utils.path_normalizer import (
    normalize_path,
    denormalize_path,
)


class TestNormalizePath:
    """Windowsパス → Claude Code形式変換のテスト"""

    def test_normalize_simple_path(self):
        """正常系: 単純なパスの変換"""
        # Arrange
        windows_path = r"D:\projects\P010"

        # Act
        result = normalize_path(windows_path)

        # Assert
        assert result == "D--projects-P010"

    def test_normalize_nested_path(self):
        """正常系: ネストされたパスの変換"""
        # Arrange
        windows_path = r"D:\projects\P010\worktrees\issue-105-session-manager"

        # Act
        result = normalize_path(windows_path)

        # Assert
        assert result == "D--projects-P010-worktrees-issue-105-session-manager"

    def test_normalize_path_with_special_chars(self):
        """境界値: 特殊文字を含むパス"""
        # Arrange
        windows_path = r"C:\Users\test user\Documents\project_name"

        # Act
        result = normalize_path(windows_path)

        # Assert
        assert result == "C--Users-test user-Documents-project_name"

    def test_normalize_empty_string(self):
        """異常系: 空文字列"""
        # Arrange
        windows_path = ""

        # Act & Assert
        with pytest.raises(ValueError, match="Path cannot be empty"):
            normalize_path(windows_path)

    def test_normalize_pathlib_path(self):
        """正常系: pathlibのPathオブジェクト"""
        # Arrange
        windows_path = Path(r"D:\projects\P010")

        # Act
        result = normalize_path(windows_path)

        # Assert
        assert result == "D--projects-P010"

    def test_normalize_very_long_path(self):
        """境界値: 非常に長いパス"""
        # Arrange
        long_segments = ["segment"] * 50
        windows_path = r"D:\projects\P010\\" + "\\".join(long_segments)

        # Act
        result = normalize_path(windows_path)

        # Assert
        expected = "D--projects-P010-" + "-".join(long_segments)
        assert result == expected

    def test_normalize_rejects_forward_slash(self):
        """異常系: /区切り入力の拒否"""
        # Arrange
        unix_path = "D:/projects/P010"

        # Act & Assert
        with pytest.raises(ValueError, match="Forward slashes are not allowed"):
            normalize_path(unix_path)

    def test_normalize_rejects_relative_path_dotdot(self):
        """異常系: 相対パス（..）の拒否"""
        # Arrange
        relative_path = r"D:\projects\..\P010"

        # Act & Assert
        with pytest.raises(ValueError, match=r"Relative path components \(\. or \.\.\) are not allowed"):
            normalize_path(relative_path)

    def test_normalize_rejects_relative_path_dot(self):
        """異常系: 相対パス（.）の拒否"""
        # Arrange
        relative_path = r"D:\projects\.\P010"

        # Act & Assert
        with pytest.raises(ValueError, match=r"Relative path components \(\. or \.\.\) are not allowed"):
            normalize_path(relative_path)

    def test_normalize_rejects_unc_path(self):
        """異常系: UNCパスの拒否"""
        # Arrange
        unc_path = r"\\server\share\folder"

        # Act & Assert
        with pytest.raises(ValueError, match="UNC paths are not allowed"):
            normalize_path(unc_path)


class TestDenormalizePath:
    """Claude Code形式 → Windowsパス変換のテスト"""

    @patch('claude_session_manager.utils.path_normalizer.Path.exists')
    def test_denormalize_simple_path(self, mock_exists):
        """正常系: 単純なパスの変換"""
        # Arrange
        normalized_path = "D--projects-P010"
        mock_exists.return_value = True

        # Act
        result = denormalize_path(normalized_path)

        # Assert
        assert result == Path(r"D:\projects\P010")

    @patch('claude_session_manager.utils.path_normalizer.Path.exists')
    def test_denormalize_nested_path(self, mock_exists):
        """正常系: ネストされたパスの変換（ヒューリスティック）"""
        # Arrange
        normalized_path = "D--projects-P010-worktrees-issue-105-session-manager"
        # すべてのパスが存在しないと仮定（ヒューリスティックを使用）
        mock_exists.return_value = False

        # Act
        result = denormalize_path(normalized_path)

        # Assert
        # ヒューリスティック: 最初の3セグメントは独立、残りは結合
        # ["projects", "P010", "worktrees", "issue", "105", "session", "manager"]
        # → ["projects", "P010", "worktrees", "issue-105-session-manager"]
        assert result == Path(
            r"D:\projects\P010\worktrees\issue-105-session-manager"
        )

    @patch('claude_session_manager.utils.path_normalizer.Path.exists')
    def test_denormalize_path_with_spaces(self, mock_exists):
        """境界値: スペースを含むパス"""
        # Arrange
        normalized_path = "C--Users-test user-Documents-project_name"
        mock_exists.return_value = True

        # Act
        result = denormalize_path(normalized_path)

        # Assert
        assert result == Path(r"C:\Users\test user\Documents\project_name")

    def test_denormalize_empty_string(self):
        """異常系: 空文字列"""
        # Arrange
        normalized_path = ""

        # Act & Assert
        with pytest.raises(ValueError, match="Path cannot be empty"):
            denormalize_path(normalized_path)

    def test_denormalize_invalid_format(self):
        """異常系: 不正なフォーマット（ドライブレターなし）"""
        # Arrange
        normalized_path = "projects-P010"  # ドライブレターがない

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid normalized path format"):
            denormalize_path(normalized_path)

    def test_denormalize_rejects_path_traversal_dotdot(self):
        """異常系: パス逸脱（..セグメント）の拒否"""
        # Arrange
        normalized_path = "D--projects-..-P010"

        # Act & Assert
        with pytest.raises(ValueError, match=r"Path traversal components \(\. or \.\.\) are not allowed"):
            denormalize_path(normalized_path)

    def test_denormalize_rejects_path_traversal_dot(self):
        """異常系: パス逸脱（.セグメント）の拒否"""
        # Arrange
        normalized_path = "D--projects-.-P010"

        # Act & Assert
        with pytest.raises(ValueError, match=r"Path traversal components \(\. or \.\.\) are not allowed"):
            denormalize_path(normalized_path)

    def test_denormalize_rejects_invalid_drive_letter_digit(self):
        """異常系: 不正なドライブレター（数字）の拒否"""
        # Arrange
        normalized_path = "1--projects-P010"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid drive letter"):
            denormalize_path(normalized_path)

    def test_denormalize_rejects_invalid_drive_letter_lowercase(self):
        """異常系: 不正なドライブレター（小文字）の拒否"""
        # Arrange
        normalized_path = "d--projects-P010"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid drive letter"):
            denormalize_path(normalized_path)

    def test_denormalize_rejects_invalid_drive_letter_symbol(self):
        """異常系: 不正なドライブレター（記号）の拒否"""
        # Arrange
        normalized_path = "@--projects-P010"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid drive letter"):
            denormalize_path(normalized_path)

    def test_denormalize_rejects_empty_segment(self):
        """異常系: 空セグメントの拒否"""
        # Arrange
        normalized_path = "D--projects--P010"  # 連続する--は空セグメントを意味する

        # Act & Assert
        with pytest.raises(ValueError, match="Empty path segments are not allowed"):
            denormalize_path(normalized_path)


class TestRoundTrip:
    """相互変換の整合性テスト"""

    @patch('claude_session_manager.utils.path_normalizer.Path.exists')
    def test_normalize_denormalize_round_trip(self, mock_exists):
        """正常系: 正規化 → 非正規化のラウンドトリップ（ヒューリスティック）"""
        # Arrange
        original_path = Path(r"D:\projects\P010\worktrees\issue-109")
        # すべてのパスが存在しないと仮定（ヒューリスティックを使用）
        mock_exists.return_value = False

        # Act
        normalized = normalize_path(original_path)
        result = denormalize_path(normalized)

        # Assert
        # ヒューリスティック: 最初の3セグメントは独立、残りは結合
        # ["projects", "P010", "worktrees", "issue", "109"]
        # → ["projects", "P010", "worktrees", "issue-109"]
        assert result == original_path

    @patch('claude_session_manager.utils.path_normalizer.Path.exists')
    def test_denormalize_normalize_round_trip(self, mock_exists):
        """正常系: 非正規化 → 正規化のラウンドトリップ"""
        # Arrange
        original_normalized = "D--projects-P010-worktrees-issue-109"
        mock_exists.return_value = True

        # Act
        denormalized = denormalize_path(original_normalized)
        result = normalize_path(denormalized)

        # Assert
        assert result == original_normalized
