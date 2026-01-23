"""search_with_gemini.py のテスト

Issue #62: ナレッジ検索(knowledge-retrieval)をGemini委任に変更してコンテキスト制約を解消する
"""

import json
import os
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# スクリプトのパスをsys.pathに追加
SCRIPT_DIR = Path(__file__).parent.parent / ".claude" / "skills" / "knowledge-retrieval" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


class TestSearchWithGemini:
    """Gemini APIによるナレッジ検索のテスト"""

    @pytest.fixture
    def sample_index_data(self) -> list:
        """テスト用のindex.jsonデータ"""
        return [
            {
                "id": "20260120_a1cce2",
                "title": "Claude Codeのサブエージェントで並列処理する方法",
                "tags": ["Claude Code", "並列処理", "サブエージェント"],
                "use_cases": ["複数タスクの同時実行", "パフォーマンス改善"],
                "decision_triggers": ["並列実行したい", "処理を高速化したい"],
                "anti_cases": ["単一タスクの場合"],
            },
            {
                "id": "20260121_63d325",
                "title": "MCPサーバーの実装ガイド",
                "tags": ["MCP", "サーバー実装"],
                "use_cases": ["外部ツール連携", "APIラッパー"],
                "decision_triggers": ["MCP対応したい"],
                "anti_cases": ["単純なスクリプト"],
            },
        ]

    @pytest.fixture
    def sample_index_file(self, tmp_path, sample_index_data) -> Path:
        """テスト用のindex.jsonファイル"""
        index_file = tmp_path / "index.json"
        index_file.write_text(
            json.dumps(sample_index_data, ensure_ascii=False), encoding="utf-8"
        )
        return index_file

    @pytest.fixture
    def mock_gemini_response(self):
        """正常なGemini APIレスポンスのモック"""
        mock_response = MagicMock()
        mock_response.text = (
            "SELECTED_ARTICLE_IDS:\n"
            "- 20260120_a1cce2\n"
            "- 20260121_63d325\n"
        )
        return mock_response

    @pytest.fixture
    def env_with_api_key(self):
        """GEMINI_API_KEYが設定された環境"""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-123"}):
            yield

    @pytest.fixture
    def mock_genai_with_response(self, mock_gemini_response):
        """正常応答のGemini APIモック"""
        with patch("search_with_gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_gemini_response
            mock_genai.GenerativeModel.return_value = mock_model
            yield mock_genai, mock_model

    # --- 正常系テスト ---

    def test_search_returns_list_of_article_ids(
        self, sample_index_file, env_with_api_key, mock_genai_with_response
    ):
        """正常なリクエストでarticle IDのリストが返却されること"""
        from search_with_gemini import search_knowledge

        result = search_knowledge(
            user_request="並列処理の方法",
            index_path=str(sample_index_file),
        )

        assert isinstance(result, list)
        assert "20260120_a1cce2" in result
        assert "20260121_63d325" in result

    def test_search_includes_user_request_in_prompt(
        self, sample_index_file, env_with_api_key, mock_genai_with_response
    ):
        """ユーザーリクエストがプロンプトに含まれること"""
        from search_with_gemini import search_knowledge

        _, mock_model = mock_genai_with_response
        search_knowledge(
            user_request="テスト用リクエスト",
            index_path=str(sample_index_file),
        )

        call_args = mock_model.generate_content.call_args[0][0]
        assert "テスト用リクエスト" in call_args

    def test_search_includes_index_data_in_prompt(
        self, sample_index_file, env_with_api_key, mock_genai_with_response
    ):
        """index.jsonのデータがプロンプトに含まれること"""
        from search_with_gemini import search_knowledge

        _, mock_model = mock_genai_with_response
        search_knowledge(
            user_request="テスト",
            index_path=str(sample_index_file),
        )

        call_args = mock_model.generate_content.call_args[0][0]
        # index dataの内容がプロンプトに含まれている
        assert "20260120_a1cce2" in call_args

    def test_search_uses_gemini_flash_model(
        self, sample_index_file, env_with_api_key, mock_genai_with_response
    ):
        """gemini-2.0-flashモデルが使用されること"""
        from search_with_gemini import search_knowledge

        mock_genai, _ = mock_genai_with_response
        search_knowledge(
            user_request="テスト",
            index_path=str(sample_index_file),
        )

        mock_genai.GenerativeModel.assert_called_once_with("gemini-2.0-flash")

    def test_search_respects_max_articles_parameter(
        self, sample_index_file, env_with_api_key, mock_genai_with_response
    ):
        """max_articlesパラメータがプロンプトに反映されること"""
        from search_with_gemini import search_knowledge

        _, mock_model = mock_genai_with_response
        search_knowledge(
            user_request="テスト",
            index_path=str(sample_index_file),
            max_articles=3,
        )

        call_args = mock_model.generate_content.call_args[0][0]
        assert "3" in call_args

    def test_search_configures_api_key_from_env(
        self, sample_index_file, mock_genai_with_response
    ):
        """GEMINI_API_KEY環境変数でAPIが設定されること"""
        from search_with_gemini import search_knowledge

        mock_genai, _ = mock_genai_with_response
        with patch.dict(os.environ, {"GEMINI_API_KEY": "my-secret-key"}):
            search_knowledge(
                user_request="テスト",
                index_path=str(sample_index_file),
            )

        mock_genai.configure.assert_called_once_with(api_key="my-secret-key")

    # --- 異常系テスト ---

    def test_search_raises_valueerror_when_api_key_missing(self, sample_index_file):
        """GEMINI_API_KEYが環境変数に存在しない場合にValueErrorが発生すること"""
        from search_with_gemini import search_knowledge

        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                search_knowledge(
                    user_request="テスト",
                    index_path=str(sample_index_file),
                )

    def test_search_raises_valueerror_when_api_key_empty(self, sample_index_file):
        """GEMINI_API_KEYが空文字の場合にValueErrorが発生すること"""
        from search_with_gemini import search_knowledge

        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                search_knowledge(
                    user_request="テスト",
                    index_path=str(sample_index_file),
                )

    def test_search_raises_filenotfounderror_when_index_missing(self, tmp_path):
        """index.jsonが存在しない場合にFileNotFoundErrorが発生すること"""
        from search_with_gemini import search_knowledge

        non_existent_path = str(tmp_path / "non_existent.json")

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with pytest.raises(FileNotFoundError):
                search_knowledge(
                    user_request="テスト",
                    index_path=non_existent_path,
                )

    def test_search_raises_runtimeerror_on_api_failure(self, sample_index_file):
        """Gemini APIエラー時にRuntimeErrorが発生すること"""
        from search_with_gemini import search_knowledge

        with patch("search_with_gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = Exception("API rate limit exceeded")
            mock_genai.GenerativeModel.return_value = mock_model

            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                with pytest.raises(RuntimeError, match="Gemini API"):
                    search_knowledge(
                        user_request="テスト",
                        index_path=str(sample_index_file),
                    )

    def test_search_raises_runtimeerror_on_timeout(self, sample_index_file):
        """タイムアウト時にRuntimeErrorが発生すること"""
        from search_with_gemini import search_knowledge

        with patch("search_with_gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = TimeoutError("Request timed out")
            mock_genai.GenerativeModel.return_value = mock_model

            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                with pytest.raises(RuntimeError, match="Gemini API"):
                    search_knowledge(
                        user_request="テスト",
                        index_path=str(sample_index_file),
                    )

    def test_search_raises_valueerror_on_invalid_json(self, tmp_path):
        """index.jsonが不正なJSONの場合にValueErrorが発生すること"""
        from search_with_gemini import search_knowledge

        index_file = tmp_path / "index.json"
        index_file.write_text("{broken json", encoding="utf-8")

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with pytest.raises(ValueError, match="JSON"):
                search_knowledge(
                    user_request="テスト",
                    index_path=str(index_file),
                )

    def test_search_raises_valueerror_on_non_list_json(self, tmp_path):
        """index.jsonがリスト形式でない場合にValueErrorが発生すること"""
        from search_with_gemini import search_knowledge

        index_file = tmp_path / "index.json"
        index_file.write_text('{"key": "value"}', encoding="utf-8")

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            with pytest.raises(ValueError, match="list"):
                search_knowledge(
                    user_request="テスト",
                    index_path=str(index_file),
                )

    # --- 境界値テスト ---

    def test_search_with_empty_request(
        self, sample_index_file, env_with_api_key, mock_genai_with_response
    ):
        """空のリクエストでもエラーにならずにリストが返ること"""
        from search_with_gemini import search_knowledge

        result = search_knowledge(
            user_request="",
            index_path=str(sample_index_file),
        )

        assert isinstance(result, list)

    def test_search_with_empty_index_returns_empty_list(self, tmp_path):
        """空のindex.json（空配列）の場合に空リストが返ること"""
        from search_with_gemini import search_knowledge

        index_file = tmp_path / "index.json"
        index_file.write_text("[]", encoding="utf-8")

        mock_response = MagicMock()
        mock_response.text = "SELECTED_ARTICLE_IDS:\n"

        with patch("search_with_gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                result = search_knowledge(
                    user_request="テスト",
                    index_path=str(index_file),
                )

            assert result == []

    def test_search_with_max_articles_one(self, sample_index_file):
        """max_articles=1の場合にプロンプトに1が含まれること"""
        from search_with_gemini import search_knowledge

        mock_response = MagicMock()
        mock_response.text = "SELECTED_ARTICLE_IDS:\n- 20260120_a1cce2\n"

        with patch("search_with_gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                result = search_knowledge(
                    user_request="テスト",
                    index_path=str(sample_index_file),
                    max_articles=1,
                )

            assert len(result) == 1

    # --- レスポンスパース耐性テスト ---

    def test_search_handles_no_ids_in_response(self, sample_index_file):
        """SELECTED_ARTICLE_IDSヘッダはあるがIDがない場合に空リストが返ること"""
        from search_with_gemini import search_knowledge

        mock_response = MagicMock()
        mock_response.text = "SELECTED_ARTICLE_IDS:\n"

        with patch("search_with_gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                result = search_knowledge(
                    user_request="テスト",
                    index_path=str(sample_index_file),
                )

            assert result == []

    def test_search_handles_response_without_header(self, sample_index_file):
        """SELECTED_ARTICLE_IDSヘッダがない応答の場合に空リストが返ること"""
        from search_with_gemini import search_knowledge

        mock_response = MagicMock()
        mock_response.text = "関連する記事は見つかりませんでした。"

        with patch("search_with_gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                result = search_knowledge(
                    user_request="テスト",
                    index_path=str(sample_index_file),
                )

            assert result == []

    def test_search_extracts_only_valid_id_format(self, sample_index_file):
        """YYYYMMDD_XXXXXX形式のIDのみが抽出されること"""
        from search_with_gemini import search_knowledge

        mock_response = MagicMock()
        mock_response.text = (
            "SELECTED_ARTICLE_IDS:\n"
            "- 20260120_a1cce2\n"
            "- invalid_id\n"
            "- 20260121_63d325\n"
            "- not_a_valid_format\n"
            "- 12345678_abcdef\n"
        )

        with patch("search_with_gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                result = search_knowledge(
                    user_request="テスト",
                    index_path=str(sample_index_file),
                )

            assert "20260120_a1cce2" in result
            assert "20260121_63d325" in result
            assert "12345678_abcdef" in result
            assert "invalid_id" not in result
            assert "not_a_valid_format" not in result

    def test_search_handles_extra_whitespace_in_response(self, sample_index_file):
        """レスポンスに余分な空白がある場合も正常にパースされること"""
        from search_with_gemini import search_knowledge

        mock_response = MagicMock()
        mock_response.text = (
            "SELECTED_ARTICLE_IDS:\n"
            "  - 20260120_a1cce2  \n"
            "-  20260121_63d325\n"
        )

        with patch("search_with_gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                result = search_knowledge(
                    user_request="テスト",
                    index_path=str(sample_index_file),
                )

            assert "20260120_a1cce2" in result
            assert "20260121_63d325" in result

    def test_search_handles_numbered_list_response(self, sample_index_file):
        """番号付きリスト形式のレスポンスも正常にパースされること"""
        from search_with_gemini import search_knowledge

        mock_response = MagicMock()
        mock_response.text = (
            "SELECTED_ARTICLE_IDS:\n"
            "1. 20260120_a1cce2\n"
            "2. 20260121_63d325\n"
        )

        with patch("search_with_gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                result = search_knowledge(
                    user_request="テスト",
                    index_path=str(sample_index_file),
                )

            assert "20260120_a1cce2" in result
            assert "20260121_63d325" in result


class TestSearchWithGeminiCLI:
    """コマンドラインインターフェースのテスト"""

    def test_cli_requires_request_argument(self):
        """--request引数が必須であること"""
        from search_with_gemini import parse_args

        with pytest.raises(SystemExit):
            parse_args([])

    def test_cli_accepts_request_argument(self):
        """--request引数を受け付けること"""
        from search_with_gemini import parse_args

        args = parse_args(["--request", "テストリクエスト"])
        assert args.request == "テストリクエスト"

    def test_cli_accepts_max_argument(self):
        """--max引数を受け付けること"""
        from search_with_gemini import parse_args

        args = parse_args(["--request", "テスト", "--max", "3"])
        assert args.max == 3

    def test_cli_default_max_is_five(self):
        """--max引数のデフォルト値が5であること"""
        from search_with_gemini import parse_args

        args = parse_args(["--request", "テスト"])
        assert args.max == 5

    def test_cli_accepts_index_path_argument(self):
        """--index-path引数を受け付けること"""
        from search_with_gemini import parse_args

        args = parse_args(["--request", "テスト", "--index-path", "/path/to/index.json"])
        assert args.index_path == "/path/to/index.json"

    def test_cli_default_index_path(self):
        """--index-path引数のデフォルト値がknowledge/index.jsonであること"""
        from search_with_gemini import parse_args

        args = parse_args(["--request", "テスト"])
        assert Path(args.index_path) == Path("knowledge/index.json")

    def test_main_prints_ids_to_stdout(self, tmp_path):
        """main関数がarticle IDを標準出力に表示すること"""
        from search_with_gemini import main

        index_file = tmp_path / "index.json"
        index_file.write_text(
            json.dumps([{"id": "20260120_a1cce2", "title": "Test", "tags": ["test"]}]),
            encoding="utf-8",
        )

        mock_response = MagicMock()
        mock_response.text = "SELECTED_ARTICLE_IDS:\n- 20260120_a1cce2\n"

        with patch("search_with_gemini.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
                with patch("sys.argv", [
                    "search_with_gemini.py",
                    "--request", "テスト",
                    "--index-path", str(index_file),
                ]):
                    captured = StringIO()
                    with patch("sys.stdout", captured):
                        main()

                    output = captured.getvalue()
                    assert "20260120_a1cce2" in output
