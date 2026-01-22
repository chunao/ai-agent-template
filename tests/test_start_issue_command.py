"""start-issue コマンド定義のテスト

Issue #29: ワークフロー違反防止: start-issue後の自動実装開始を禁止
"""

from pathlib import Path

import pytest


class TestStartIssueCommand:
    """/start-issue コマンド定義のテスト"""

    @pytest.fixture
    def command_path(self) -> Path:
        """コマンドファイルのパスを返す"""
        return Path(__file__).parent.parent / ".claude" / "commands" / "start-issue.md"

    @pytest.fixture
    def command_content(self, command_path: Path) -> str:
        """コマンドファイルの内容を読み込む"""
        if not command_path.exists():
            pytest.skip(f"Command file not found: {command_path}")
        return command_path.read_text(encoding="utf-8")

    def test_command_file_exists(self, command_path: Path):
        """コマンドファイルが存在すること"""
        assert command_path.exists(), f"Command file should exist at {command_path}"

    def test_command_has_title(self, command_content: str):
        """コマンドにタイトルが設定されていること"""
        assert "# /start-issue" in command_content, "Command should have a title"

    def test_command_has_stop_instruction_after_report(self, command_content: str):
        """作業開始レポート投稿後に停止する指示があること

        受け入れ基準1: /start-issue 実行後、作業開始レポート投稿で停止することが明記されている
        """
        # 停止を指示する文言が含まれているかチェック
        stop_keywords = ["停止", "ここで終了", "待つ", "stop"]
        content_lower = command_content.lower()

        # 「作業開始レポート」と「停止」の関連が明記されているか
        has_stop_after_report = any(
            keyword in command_content or keyword in content_lower
            for keyword in stop_keywords
        )

        # より具体的なチェック：停止指示が明確に書かれているか
        explicit_stop_patterns = [
            "ここで停止",
            "停止してください",
            "実装を開始しない",
            "ユーザーの指示を待",
        ]
        has_explicit_stop = any(
            pattern in command_content for pattern in explicit_stop_patterns
        )

        assert (
            has_stop_after_report and has_explicit_stop
        ), "Command should explicitly state to stop after posting the work start report"

    def test_command_requires_user_instruction_for_pr(self, command_content: str):
        """PR作成にユーザーの明示的な指示が必要であることが明記されていること

        受け入れ基準2: PR作成にはユーザーの明示的な指示が必要であることが明記されている
        """
        pr_instruction_patterns = [
            "PR作成はユーザーの明示的な指示",
            "PRの作成はユーザーの",
            "ユーザーの指示がある場合のみ",
        ]
        has_pr_instruction = any(
            pattern in command_content for pattern in pr_instruction_patterns
        )
        assert (
            has_pr_instruction
        ), "Command should state that PR creation requires explicit user instruction"

    def test_command_documents_progress_reporting_timing(self, command_content: str):
        """進捗報告のタイミングが明記されていること

        受け入れ基準3: 進捗報告のタイミングが明記されている
        """
        # /issue-sync での進捗報告について言及があるか
        has_issue_sync = "/issue-sync" in command_content

        # TDD後やreview後のタイミングが明記されているか
        timing_patterns = ["TDD後", "review後", "TDD完了後", "レビュー後"]
        has_timing = any(pattern in command_content for pattern in timing_patterns)

        assert (
            has_issue_sync and has_timing
        ), "Command should document when to report progress using /issue-sync (after TDD, after review)"

    def test_command_has_workflow_constraints_section(self, command_content: str):
        """注意事項セクションにワークフロー制約があること"""
        assert (
            "注意事項" in command_content or "## 注意" in command_content
        ), "Command should have a notes/constraints section"

    def test_command_mentions_tdd_command(self, command_content: str):
        """/tdd コマンドへの言及があること"""
        assert "/tdd" in command_content, "Command should mention /tdd command"
