"""TokenEstimator 拡張機能のテスト

Issue #101: トークン使用量記録の自動化（Phase 4.2）
"""

import pytest
from src.token_usage.estimator import TokenEstimator


class TestTokenEstimatorExtension:
    """TokenEstimator 拡張機能のテスト"""

    @pytest.fixture
    def estimator(self):
        """TokenEstimator インスタンス"""
        return TokenEstimator(model="gpt-4")

    def test_estimate_input_text_tokens(self, estimator):
        """入力テキストのトークン数を推定できる"""
        input_text = "This is a test input for token estimation."
        tokens = estimator.estimate(input_text)

        assert tokens > 0
        assert isinstance(tokens, int)

    def test_estimate_output_text_tokens(self, estimator):
        """出力テキストのトークン数を推定できる"""
        output_text = "This is a test output response from the model."
        tokens = estimator.estimate(output_text)

        assert tokens > 0
        assert isinstance(tokens, int)

    def test_estimate_empty_text_returns_zero(self, estimator):
        """空テキストの場合に0を返す（異常系）"""
        tokens = estimator.estimate("")
        assert tokens == 0

    def test_estimate_none_text_returns_zero(self, estimator):
        """Noneの場合に0を返す（異常系）"""
        # 既存実装では `if not text:` でNoneもチェックされる
        tokens = estimator.estimate(None)
        assert tokens == 0

    def test_estimate_accuracy_within_30_percent(self, estimator):
        """推定精度が±30%以内であることを確認（受け入れ基準）"""
        # 既知のトークン数を持つテキストでテスト
        # "Hello, world!" は約3-4トークン（GPT-4 tokenizer）
        test_text = "Hello, world!"
        estimated = estimator.estimate(test_text)

        # 期待値: 約3-4トークン
        expected = 3.5
        tolerance = expected * 0.3  # 30%の許容誤差

        assert abs(estimated - expected) <= tolerance, \
            f"Estimated {estimated} tokens, expected ~{expected} ±{tolerance}"

    def test_estimate_accuracy_with_longer_text(self, estimator):
        """長いテキストでの推定精度を確認"""
        # 約100トークンのテキスト
        long_text = " ".join(["word"] * 100)
        estimated = estimator.estimate(long_text)

        # 100単語は約100-150トークン程度
        assert 70 <= estimated <= 180, \
            f"Expected 70-180 tokens for 100 words, got {estimated}"

    def test_estimate_with_different_models(self):
        """複数モデルでの推定テスト"""
        models = ["gpt-4", "gpt-3.5-turbo", "claude-sonnet-4.5"]
        test_text = "This is a test sentence for token estimation."

        results = {}
        for model in models:
            try:
                estimator = TokenEstimator(model=model)
                tokens = estimator.estimate(test_text)
                results[model] = tokens
            except Exception:
                # モデルがサポートされていない場合はスキップ
                continue

        # 少なくとも1つのモデルで推定できることを確認
        assert len(results) > 0
        # すべての推定値が0より大きいことを確認
        assert all(tokens > 0 for tokens in results.values())

    def test_estimate_japanese_text(self, estimator):
        """日本語テキストのトークン推定"""
        japanese_text = "これはトークン推定のテストです。"
        tokens = estimator.estimate(japanese_text)

        # 日本語は1文字あたり複数トークンになることが多い
        assert tokens > len(japanese_text) / 2

    def test_estimate_code_text(self, estimator):
        """コードテキストのトークン推定"""
        code_text = """
def test_function():
    return "Hello, world!"
"""
        tokens = estimator.estimate(code_text)
        assert tokens > 0

    def test_estimate_markdown_text(self, estimator):
        """Markdownテキストのトークン推定"""
        markdown_text = """
# Title

This is a **test** markdown document.

- Item 1
- Item 2
"""
        tokens = estimator.estimate(markdown_text)
        assert tokens > 0


class TestTokenEstimatorBoundaryValues:
    """TokenEstimator 境界値テスト"""

    def test_estimate_zero_tokens(self):
        """0トークンのテキスト（境界値）"""
        estimator = TokenEstimator()
        assert estimator.estimate("") == 0

    def test_estimate_very_long_text(self):
        """非常に長いテキストのパフォーマンステスト（境界値）"""
        estimator = TokenEstimator()

        # 10,000単語のテキスト
        very_long_text = " ".join(["word"] * 10000)
        tokens = estimator.estimate(very_long_text)

        # 10,000単語は約10,000-15,000トークン程度
        assert 7000 <= tokens <= 18000

    def test_estimate_max_context_length(self):
        """最大コンテキスト長に近いテキスト（境界値）"""
        estimator = TokenEstimator()

        # Claude Sonnet 4.5の最大コンテキスト: 200,000トークン
        # 約15万単語で20万トークン程度になると推定
        # テストでは5,000単語で確認（パフォーマンス考慮）
        large_text = " ".join(["word"] * 5000)
        tokens = estimator.estimate(large_text)

        assert tokens > 0
        assert tokens < 200000  # 最大コンテキストを超えていないことを確認
