"""Tests for token usage estimator."""

import pytest
from src.token_usage.estimator import TokenEstimator


class TestTokenEstimator:
    """トークン数推定機能のテスト."""

    def test_estimate_tokens_success(self):
        """正常系: トークン数を正しく推定できること."""
        estimator = TokenEstimator()
        text = "Hello, world! This is a test message."
        tokens = estimator.estimate(text)

        assert tokens > 0
        assert isinstance(tokens, int)

    def test_estimate_tokens_with_model(self):
        """正常系: モデル指定でトークン数を推定できること."""
        estimator = TokenEstimator(model="gpt-4")
        text = "Test message"
        tokens = estimator.estimate(text)

        assert tokens > 0

    def test_estimate_empty_string(self):
        """境界値: 空文字列のトークン数は0."""
        estimator = TokenEstimator()
        tokens = estimator.estimate("")

        assert tokens == 0

    def test_estimate_long_text(self):
        """境界値: 非常に長いテキストのトークン数推定."""
        estimator = TokenEstimator()
        text = "Test " * 10000  # 50000文字程度
        tokens = estimator.estimate(text)

        assert tokens > 0
        assert isinstance(tokens, int)

    def test_estimate_japanese_text(self):
        """正常系: 日本語テキストのトークン数推定."""
        estimator = TokenEstimator()
        text = "こんにちは、世界！これはテストメッセージです。"
        tokens = estimator.estimate(text)

        assert tokens > 0

    def test_estimate_mixed_text(self):
        """正常系: 英日混在テキストのトークン数推定."""
        estimator = TokenEstimator()
        text = "Hello, こんにちは! This is 混在テキスト."
        tokens = estimator.estimate(text)

        assert tokens > 0

    def test_invalid_model_name(self):
        """異常系: 不正なモデル名はフォールバック."""
        estimator = TokenEstimator(model="invalid-model")
        text = "Test message"
        tokens = estimator.estimate(text)

        # フォールバックでcl100k_baseが使われる
        assert tokens > 0

    def test_estimation_method_recording(self):
        """正常系: 推定方法を記録できること."""
        estimator = TokenEstimator()
        text = "Test message"
        _ = estimator.estimate(text)

        assert estimator.estimation_method == "tiktoken"
