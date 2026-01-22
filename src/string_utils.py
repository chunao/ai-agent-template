"""文字列ユーティリティ関数"""

import re


def slugify(text: str) -> str:
    """テキストをURLスラッグに変換する

    Args:
        text: 変換する文字列

    Returns:
        スラッグ化された文字列
    """
    if not text:
        return ""

    # 小文字に変換
    text = text.lower()

    # ASCII以外の文字（日本語など）を保持しつつ、特殊記号を除去
    # 英数字、日本語文字、スペース、ハイフン以外を除去
    text = re.sub(r"[^\w\s\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff-]", "", text)

    # 連続するスペースを1つのハイフンに置換
    text = re.sub(r"\s+", "-", text)

    # 連続するハイフンを1つに
    text = re.sub(r"-+", "-", text)

    # 先頭と末尾のハイフンを除去
    text = text.strip("-")

    return text
