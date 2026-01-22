"""check-ci コマンド定義のテスト

Issue #13: PR作成後のCI結果自動確認機能を追加する
"""

from pathlib import Path

import pytest


class TestCheckCiCommand:
    """/check-ci コマンド定義のテスト"""

    @pytest.fixture
    def command_path(self) -> Path:
        """コマンドファイルのパスを返す"""
        return Path(__file__).parent.parent / ".claude" / "commands" / "check-ci.md"

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
        assert "# /check-ci" in command_content, "Command should have a title"

    def test_command_has_usage_section(self, command_content: str):
        """使い方セクションがあること"""
        assert "使い方" in command_content or "Usage" in command_content, \
            "Command should have usage section"

    def test_command_accepts_pr_number(self, command_content: str):
        """PR番号を引数として受け取れること"""
        assert "<pr" in command_content.lower() or "pr番号" in command_content or "pr number" in command_content.lower(), \
            "Command should accept PR number as argument"

    def test_command_uses_gh_run_list(self, command_content: str):
        """gh run list コマンドを使用すること"""
        assert "gh run list" in command_content, \
            "Command should use 'gh run list' to get workflow runs"

    def test_command_uses_gh_run_view(self, command_content: str):
        """gh run view コマンドを使用すること"""
        assert "gh run view" in command_content, \
            "Command should use 'gh run view' to check status"

    def test_command_has_timeout_setting(self, command_content: str):
        """タイムアウト設定があること"""
        assert "タイムアウト" in command_content or "timeout" in command_content.lower(), \
            "Command should have timeout setting"

    def test_command_handles_ci_status(self, command_content: str):
        """CI結果のステータス（success/failure/pending）を処理すること"""
        content_lower = command_content.lower()
        has_success = "success" in content_lower or "成功" in command_content
        has_failure = "failure" in content_lower or "fail" in content_lower or "失敗" in command_content
        has_pending = "pending" in content_lower or "progress" in content_lower or "実行中" in command_content

        assert has_success and has_failure and has_pending, \
            "Command should handle CI status (success/failure/pending)"

    def test_command_can_wait_for_completion(self, command_content: str):
        """完了まで待機する機能があること"""
        has_wait = "待機" in command_content or "wait" in command_content.lower() or \
                   "watch" in command_content.lower() or "ポーリング" in command_content
        assert has_wait, "Command should have wait/watch functionality"

    def test_command_can_get_logs(self, command_content: str):
        """ログ取得機能があること"""
        has_log = "ログ" in command_content or "--log" in command_content or "log" in command_content.lower()
        assert has_log, "Command should have log retrieval functionality"
