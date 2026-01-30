"""Token usage estimator using tiktoken."""

import tiktoken


class TokenEstimator:
    """トークン数を推定するクラス."""

    def __init__(self, model: str = "gpt-4"):
        """Initialize estimator.

        Args:
            model: モデル名（デフォルト: gpt-4）
        """
        self.model = model
        self.estimation_method = "tiktoken"

        try:
            # モデル名からエンコーダーを取得
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # フォールバック: cl100k_base（GPT-4の標準エンコーディング）
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def estimate(self, text: str) -> int:
        """テキストのトークン数を推定.

        Args:
            text: 推定対象のテキスト

        Returns:
            推定トークン数
        """
        if not text:
            return 0

        tokens = self.encoding.encode(text)
        return len(tokens)
