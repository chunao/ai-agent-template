"""Gemini APIを使用したナレッジ検索スクリプト

knowledge/index.json をGemini 2.0 Flash APIに送信し、
ユーザーリクエストに関連する記事IDを検索する。
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import google.generativeai as genai

# article IDの正規表現パターン（YYYYMMDD_XXXXXX形式）
ID_PATTERN = re.compile(r"\d{8}_[a-f0-9]{6}")


def parse_args(args: list[str]) -> argparse.Namespace:
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(
        description="Gemini APIを使用してナレッジインデックスを検索する"
    )
    parser.add_argument(
        "--request",
        required=True,
        help="検索リクエスト（ユーザーの質問やタスク内容）",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=5,
        help="最大記事数（デフォルト: 5）",
    )
    parser.add_argument(
        "--index-path",
        default=str(Path("knowledge/index.json")),
        help="index.jsonのパス（デフォルト: knowledge/index.json）",
    )
    return parser.parse_args(args)


def search_knowledge(
    user_request: str,
    index_path: str,
    max_articles: int = 5,
) -> list[str]:
    """Gemini APIを使用してナレッジを検索し、関連する記事IDのリストを返す

    Args:
        user_request: ユーザーの検索リクエスト
        index_path: index.jsonファイルのパス
        max_articles: 最大取得記事数

    Returns:
        関連する記事IDのリスト

    Raises:
        ValueError: APIキーが未設定、またはindex.jsonが不正な場合
        FileNotFoundError: index.jsonが存在しない場合
        RuntimeError: Gemini API呼び出しに失敗した場合
    """
    # APIキーの検証
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY 環境変数が設定されていません。"
            ".env ファイルまたは環境変数にGEMINI_API_KEYを設定してください。"
        )

    # index.jsonの読み込み
    index_file = Path(index_path)
    if not index_file.exists():
        raise FileNotFoundError(f"index.jsonが見つかりません: {index_path}")

    try:
        index_data = json.loads(index_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"index.jsonのJSON解析に失敗しました: {e}") from e

    if not isinstance(index_data, list):
        raise ValueError(
            f"index.jsonはlist形式である必要があります（実際: {type(index_data).__name__}）"
        )

    # Gemini API設定
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    # プロンプト構築
    prompt = _build_prompt(user_request, index_data, max_articles)

    # API呼び出し
    try:
        response = model.generate_content(prompt)
    except Exception as e:
        raise RuntimeError(f"Gemini API呼び出しに失敗しました: {e}") from e

    # レスポンスからIDを抽出
    return _extract_ids(response.text)


def _build_prompt(user_request: str, index_data: list, max_articles: int) -> str:
    """Gemini APIに送信するプロンプトを構築する"""
    return f"""以下のナレッジインデックスを分析し、ユーザーリクエストに関連する記事を最大{max_articles}件選択してください。

【インデックスデータ】
{json.dumps(index_data, ensure_ascii=False, indent=2)}

【分析観点】
- tags: 現在のトピックとの一致度
- use_cases: 現在の状況との適合性
- decision_triggers: 類似したトリガーの存在
- anti_cases: 避けるべき条件の確認

【出力フォーマット】
以下の形式で、選択した記事のIDのみを出力してください：

SELECTED_ARTICLE_IDS:
- 20260120_a1cce2
- 20260121_63d325

【ユーザーリクエスト】
{user_request}
"""


def _extract_ids(response_text: str) -> list[str]:
    """レスポンステキストからarticle IDを抽出する"""
    return ID_PATTERN.findall(response_text)


def main():
    """メインエントリーポイント"""
    args = parse_args(sys.argv[1:])
    ids = search_knowledge(
        user_request=args.request,
        index_path=args.index_path,
        max_articles=args.max,
    )
    for article_id in ids:
        print(article_id)


if __name__ == "__main__":
    main()
