"""pr-merge コマンド定義のテスト

Issue #15: PRマージとブランチ削除を自動化する
Issue #22: ローカルブランチも自動削除する（git worktree対応）
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

    def test_command_auto_deletes_local_branch(self, command_content: str):
        """ローカルブランチが自動削除されること"""
        assert "git branch -d" in command_content, \
            "Command should use 'git branch -d' for local branch deletion"
        # 「案内」ではなく「自動削除」であること
        assert "自動削除" in command_content or "ローカルブランチの自動削除" in command_content, \
            "Command should auto-delete local branch, not just guide"

    def test_command_checks_worktree_before_branch_delete(self, command_content: str):
        """worktreeの存在確認を行ってからブランチ削除すること"""
        assert "git worktree list" in command_content, \
            "Command should check worktree existence with 'git worktree list'"
        # worktree確認がブランチ削除より前にあること
        worktree_pos = command_content.find("git worktree list")
        branch_delete_pos = command_content.find("git branch -d")
        assert worktree_pos < branch_delete_pos, \
            "Worktree check should come before branch deletion"

    def test_command_removes_worktree_if_exists(self, command_content: str):
        """worktreeが存在する場合に削除すること"""
        assert "git worktree remove" in command_content, \
            "Command should remove worktree with 'git worktree remove'"
        # worktree削除がブランチ削除より前にあること
        worktree_remove_pos = command_content.find("git worktree remove")
        branch_delete_pos = command_content.find("git branch -d")
        assert worktree_remove_pos < branch_delete_pos, \
            "Worktree removal should come before branch deletion"

    def test_command_switches_to_main_if_on_target_branch(self, command_content: str):
        """削除対象が現在ブランチの場合、mainに切り替えること"""
        assert "git checkout main" in command_content, \
            "Command should switch to main branch if on target branch"
        # checkout mainがブランチ削除より前にあること
        checkout_pos = command_content.rfind("git checkout main")
        branch_delete_pos = command_content.find("git branch -d")
        assert checkout_pos < branch_delete_pos, \
            "Checkout main should come before branch deletion"

    def test_command_pulls_main_before_branch_delete(self, command_content: str):
        """ブランチ削除前にmain最新化を行うこと"""
        assert "git pull origin main" in command_content, \
            "Command should pull latest main before branch deletion"

    def test_command_reports_deletion_result(self, command_content: str):
        """削除結果がユーザーに報告されること"""
        assert "削除" in command_content and "報告" in command_content or \
               "削除結果" in command_content or \
               "ローカルブランチ" in command_content and "削除しました" in command_content, \
            "Command should report branch deletion result to user"

    def test_command_does_not_use_force_delete(self, command_content: str):
        """強制削除（-D）を使用しないこと"""
        # git branch -D は使用しない（安全策）
        # ただし「使用しない」という説明文中に含まれる可能性があるため、
        # 実際のコマンドとして使われていないことを確認
        lines = command_content.split("\n")
        for line in lines:
            stripped = line.strip()
            # bashコードブロック内のコマンド行でgit branch -Dが使われていないこと
            if stripped.startswith("git branch -D"):
                pytest.fail("Command should not use 'git branch -D' (force delete)")

    def test_command_handles_branch_delete_failure(self, command_content: str):
        """ブランチ削除失敗時のエラーハンドリングがあること"""
        has_delete_failure = ("ブランチ削除" in command_content and "失敗" in command_content) or \
                             ("ローカルブランチ" in command_content and "削除失敗" in command_content) or \
                             "削除できない" in command_content or \
                             "削除に失敗" in command_content
        assert has_delete_failure, \
            "Command should handle branch deletion failure case"

    def test_command_handles_worktree_remove_failure(self, command_content: str):
        """worktree削除失敗時のエラーハンドリングがあること"""
        has_worktree_failure = "worktree" in command_content.lower() and \
                               ("削除失敗" in command_content or "削除に失敗" in command_content or
                                "削除できない" in command_content or "失敗" in command_content)
        assert has_worktree_failure, \
            "Command should handle worktree removal failure case"

    def test_command_has_output_example(self, command_content: str):
        """出力例があること"""
        assert "出力例" in command_content or "Output" in command_content or \
               "```" in command_content, \
            "Command should have output example"

    def test_command_output_example_shows_auto_deletion(self, command_content: str):
        """出力例にローカルブランチの自動削除完了が含まれること"""
        # 出力例セクション内でローカルブランチ削除完了のメッセージがあること
        output_section_start = command_content.find("## 出力例")
        assert output_section_start != -1, "Should have output example section"
        output_section = command_content[output_section_start:]
        assert "ローカルブランチ" in output_section and "削除" in output_section, \
            "Output example should show local branch auto-deletion result"
