"""pr-merge コマンド定義のテスト

Issue #15: PRマージとブランチ削除を自動化する
"""

from pathlib import Path

import pytest


class TestPrMergeCommand:
    """/pr-merge コマンド定義のテスト"""

    @pytest.fixture
    def command_path(self) -> Path:
        """コマンドファイルのパスを返す"""
        return Path(__file__).parent.parent / ".claude" / "commands" / "pr-merge.md"

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
        assert "# /pr-merge" in command_content, "Command should have a title"

    def test_command_has_usage_section(self, command_content: str):
        """使い方セクションがあること"""
        assert "使い方" in command_content or "Usage" in command_content, \
            "Command should have usage section"

    def test_command_accepts_pr_number(self, command_content: str):
        """PR番号を引数として受け取れること"""
        assert "PR番号" in command_content or "pr number" in command_content.lower() or \
               "<pr" in command_content.lower(), \
            "Command should accept PR number as argument"

    def test_command_uses_gh_pr_merge(self, command_content: str):
        """gh pr merge コマンドを使用すること"""
        assert "gh pr merge" in command_content, \
            "Command should use 'gh pr merge' to merge PR"

    def test_command_uses_delete_branch_flag(self, command_content: str):
        """--delete-branch フラグを使用すること"""
        assert "--delete-branch" in command_content, \
            "Command should use '--delete-branch' flag to delete remote branch"

    def test_command_has_error_handling_section(self, command_content: str):
        """エラーハンドリングセクションがあること"""
        assert "エラーハンドリング" in command_content or "Error" in command_content, \
            "Command should have error handling section"

    def test_command_handles_ci_failure(self, command_content: str):
        """CI失敗時の対応が記載されていること"""
        content_lower = command_content.lower()
        has_ci_failure = ("ci" in content_lower and "失敗" in command_content) or \
                         ("ci" in content_lower and "failure" in content_lower)
        assert has_ci_failure, "Command should handle CI failure case"

    def test_command_handles_already_merged(self, command_content: str):
        """マージ済みPRの対応が記載されていること"""
        assert "マージ済み" in command_content or "already merged" in command_content.lower(), \
            "Command should handle already merged PR case"

    def test_command_handles_conflict(self, command_content: str):
        """コンフリクト時の対応が記載されていること"""
        assert "コンフリクト" in command_content or "conflict" in command_content.lower(), \
            "Command should handle conflict case"

    def test_command_guides_local_branch_deletion(self, command_content: str):
        """ローカルブランチ削除の案内があること"""
        has_local_branch = "ローカルブランチ" in command_content or "local branch" in command_content.lower()
        has_git_branch_d = "git branch -d" in command_content or "git branch -D" in command_content
        assert has_local_branch or has_git_branch_d, \
            "Command should guide local branch deletion"

    def test_command_has_output_example(self, command_content: str):
        """出力例があること"""
        assert "出力例" in command_content or "Output" in command_content or \
               "```" in command_content, \
            "Command should have output example"
