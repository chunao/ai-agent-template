"""文字列ユーティリティ関数のテスト"""

import pytest
from src.string_utils import slugify


class TestSlugify:
    """slugify関数のテスト"""

    def test_slugify_with_spaces_returns_hyphenated_string(self):
        # Arrange
        text = "Hello World"

        # Act
        result = slugify(text)

        # Assert
        assert result == "hello-world"

    def test_slugify_with_uppercase_returns_lowercase(self):
        # Arrange
        text = "HELLO"

        # Act
        result = slugify(text)

        # Assert
        assert result == "hello"

    def test_slugify_with_special_chars_removes_them(self):
        # Arrange
        text = "Hello, World!"

        # Act
        result = slugify(text)

        # Assert
        assert result == "hello-world"

    def test_slugify_with_multiple_spaces_returns_single_hyphen(self):
        # Arrange
        text = "Hello   World"

        # Act
        result = slugify(text)

        # Assert
        assert result == "hello-world"

    def test_slugify_with_empty_string_returns_empty(self):
        # Arrange
        text = ""

        # Act
        result = slugify(text)

        # Assert
        assert result == ""

    def test_slugify_with_japanese_preserves_characters(self):
        # Arrange
        text = "こんにちは World"

        # Act
        result = slugify(text)

        # Assert
        assert result == "こんにちは-world"
