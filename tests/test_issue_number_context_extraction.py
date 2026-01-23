"""Issue番号のコンテキスト優先抽出のテスト

Issue #34: Issue番号の自動抽出コマンドを廃止し、会話コンテキストから取得する
"""

from pathlib import Path

import pytest


class TestTddCommandIssueExtraction:
    """/tdd コマンドのIssue番号抽出方式テスト"""

    @pytest.fixture
    def command_path(self) -> Path:
        """コマンドファイルのパスを返す"""
        return Path(__file__).parent.parent / ".claude" / "commands" / "tdd.md"

    @pytest.fixture
    def command_content(self, command_path: Path) -> str:
        """コマンドファイルの内容を読み込む"""
        if not command_path.exists():
            pytest.skip(f"Command file not found: {command_path}")
        return command_path.read_text(encoding="utf-8")

    def test_context_priority_over_bash(self, command_content: str):
        """会話コンテキストからの取得がBashコマンドより優先されること"""
        context_patterns = [
            "会話",
            "コンテキスト",
        ]
        has_context_priority = any(
            pattern in command_content for pattern in context_patterns
        )
        assert has_context_priority, (
            "tdd.md should mention context-based issue number extraction"
        )

    def test_bash_command_is_fallback(self, command_content: str):
        """Bashコマンドがフォールバックとして記述されていること"""
        fallback_patterns = [
            "フォールバック",
            "特定できない場合",
        ]
        has_fallback = any(
            pattern in command_content for pattern in fallback_patterns
        )
        assert has_fallback, (
            "tdd.md should describe bash command as fallback"
        )

    def test_context_before_bash_in_order(self, command_content: str):
        """コンテキスト取得がBashコマンドより前に記述されていること"""
        context_pos = command_content.find("会話")
        bash_pos = command_content.find("git branch --show-current")

        assert context_pos != -1, (
            "tdd.md should contain context-based extraction description"
        )
        assert bash_pos != -1, (
            "tdd.md should still contain bash fallback command"
        )
        assert context_pos < bash_pos, (
            "Context extraction should appear before bash fallback"
        )

    def test_flow_diagram_updated(self, command_content: str):
        """自動処理フロー図がコンテキスト優先に更新されていること"""
        # フロー図に「ブランチ名から」だけでなく
        # コンテキスト優先の記述があること
        old_flow = "Issue番号抽出（ブランチ名から）"
        assert old_flow not in command_content, (
            "Flow diagram should not describe extraction as branch-name only"
        )

    def test_failure_table_updated(self, command_content: str):
        """自動処理失敗テーブルが更新されていること"""
        # 失敗テーブルにコンテキスト取得の失敗ケースが含まれること
        assert "コンテキスト" in command_content or "特定失敗" in command_content, (
            "Failure table should mention context extraction failure"
        )


class TestReviewCommandIssueExtraction:
    """/review コマンドのIssue番号抽出方式テスト"""

    @pytest.fixture
    def command_path(self) -> Path:
        """コマンドファイルのパスを返す"""
        return Path(__file__).parent.parent / ".claude" / "commands" / "review.md"

    @pytest.fixture
    def command_content(self, command_path: Path) -> str:
        """コマンドファイルの内容を読み込む"""
        if not command_path.exists():
            pytest.skip(f"Command file not found: {command_path}")
        return command_path.read_text(encoding="utf-8")

    def test_context_priority_over_bash(self, command_content: str):
        """会話コンテキストからの取得がBashコマンドより優先されること"""
        context_patterns = [
            "会話",
            "コンテキスト",
        ]
        has_context_priority = any(
            pattern in command_content for pattern in context_patterns
        )
        assert has_context_priority, (
            "review.md should mention context-based issue number extraction"
        )

    def test_bash_command_is_fallback(self, command_content: str):
        """Bashコマンドがフォールバックとして記述されていること"""
        fallback_patterns = [
            "フォールバック",
            "特定できない場合",
        ]
        has_fallback = any(
            pattern in command_content for pattern in fallback_patterns
        )
        assert has_fallback, (
            "review.md should describe bash command as fallback"
        )

    def test_context_before_bash_in_order(self, command_content: str):
        """コンテキスト取得がBashコマンドより前に記述されていること"""
        context_pos = command_content.find("会話")
        bash_pos = command_content.find("git branch --show-current")

        assert context_pos != -1, (
            "review.md should contain context-based extraction description"
        )
        assert bash_pos != -1, (
            "review.md should still contain bash fallback command"
        )
        assert context_pos < bash_pos, (
            "Context extraction should appear before bash fallback"
        )

    def test_no_bash_first_workflow(self, command_content: str):
        """通常のワークフローでBashコマンドが最初に実行されない構造であること"""
        # Step 1 の中で、会話コンテキストが最初に来ること
        step1_start = command_content.find("### Step 1")
        if step1_start == -1:
            step1_start = command_content.find("#### Step 1")
        assert step1_start != -1, "Should have Step 1 section"

        step1_section = command_content[step1_start:]
        # Step 1内で会話コンテキストがbashより前に来ること
        context_in_step = step1_section.find("会話")
        bash_in_step = step1_section.find("git branch")

        assert context_in_step != -1, (
            "Step 1 should mention context-based extraction"
        )
        assert bash_in_step != -1, (
            "Step 1 should still have bash fallback"
        )
        assert context_in_step < bash_in_step, (
            "In Step 1, context extraction should come before bash command"
        )
