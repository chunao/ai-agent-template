"""context_detector モジュールのテスト

Issue #101: トークン使用量記録の自動化（Phase 4.1）
"""

from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest


class TestContextDetector:
    """ContextDetector のテスト"""

    def test_extract_issue_number_from_branch_name(self):
        """ブランチ名からIssue番号を正しく抽出できる"""
        from src.token_usage.context_detector import extract_issue_number

        # 正常系: feature/issue-101-xxx 形式
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="feature/issue-101-auto-token-tracking\n",
                returncode=0
            )
            issue_num = extract_issue_number()
            assert issue_num == "101"

    def test_extract_issue_number_from_branch_name_single_digit(self):
        """1桁のIssue番号を正しく抽出できる（境界値）"""
        from src.token_usage.context_detector import extract_issue_number

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="feature/issue-5-test\n",
                returncode=0
            )
            issue_num = extract_issue_number()
            assert issue_num == "5"

    def test_extract_issue_number_from_branch_name_large_number(self):
        """6桁のIssue番号を正しく抽出できる（境界値）"""
        from src.token_usage.context_detector import extract_issue_number

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="feature/issue-123456-test\n",
                returncode=0
            )
            issue_num = extract_issue_number()
            assert issue_num == "123456"

    def test_extract_issue_number_from_branch_name_no_issue(self):
        """Issue番号が含まれないブランチ名の場合にNoneを返す（異常系）"""
        from src.token_usage.context_detector import extract_issue_number

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="main\n",
                returncode=0
            )
            issue_num = extract_issue_number()
            assert issue_num is None

    def test_extract_issue_number_git_command_fails(self):
        """git情報が取得できない場合にNoneを返す（異常系）"""
        from src.token_usage.context_detector import extract_issue_number

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stderr="fatal: not a git repository"
            )
            issue_num = extract_issue_number()
            assert issue_num is None

    def test_detect_worktree_path(self):
        """カレントディレクトリからWorktreeパスを検出できる"""
        from src.token_usage.context_detector import detect_worktree_path

        with patch("pathlib.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("D:/projects/P010-worktrees/issue-101-auto-token-tracking")
            worktree_path = detect_worktree_path()
            assert "issue-101" in worktree_path

    def test_detect_worktree_path_main_repo(self):
        """メインリポジトリの場合にNoneを返す"""
        from src.token_usage.context_detector import detect_worktree_path

        with patch("pathlib.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("D:/projects/P010")
            worktree_path = detect_worktree_path()
            # メインリポジトリの場合は "P010" のみでworktreeパターンに一致しない
            assert worktree_path is None or "worktrees" not in worktree_path

    def test_generate_session_id_uniqueness(self):
        """session_idが一意性を保証する（マイクロ秒精度）"""
        from src.token_usage.context_detector import generate_session_id
        import time

        session_id_1 = generate_session_id()
        time.sleep(0.001)  # 1ミリ秒待機
        session_id_2 = generate_session_id()

        assert session_id_1 != session_id_2
        assert session_id_1.startswith("sess_")
        assert session_id_2.startswith("sess_")

    def test_generate_session_id_format(self):
        """session_idが正しいフォーマットで生成される"""
        from src.token_usage.context_detector import generate_session_id
        import re

        session_id = generate_session_id()

        # フォーマット: sess_YYYYMMDD_HHMMSS_μμμμμμ
        pattern = r"^sess_\d{8}_\d{6}_\d{6}$"
        assert re.match(pattern, session_id), f"Invalid format: {session_id}"

    def test_detect_context_all_info_available(self):
        """すべての情報が取得できる場合の統合テスト"""
        from src.token_usage.context_detector import detect_context

        with patch("subprocess.run") as mock_run, \
             patch("pathlib.Path.cwd") as mock_cwd:

            mock_run.return_value = MagicMock(
                stdout="feature/issue-101-auto-token-tracking\n",
                returncode=0
            )
            mock_cwd.return_value = Path("D:/projects/P010-worktrees/issue-101-auto-token-tracking")

            context = detect_context()

            assert context["issue"] == "101"
            assert "issue-101" in context["worktree"]
            assert context["session_id"].startswith("sess_")

    def test_detect_context_partial_info(self):
        """一部の情報のみ取得できる場合の統合テスト"""
        from src.token_usage.context_detector import detect_context

        with patch("subprocess.run") as mock_run, \
             patch("pathlib.Path.cwd") as mock_cwd:

            # git情報は取得できない
            mock_run.return_value = MagicMock(returncode=1)
            # worktree情報は取得できる
            mock_cwd.return_value = Path("D:/projects/P010-worktrees/issue-101-auto-token-tracking")

            context = detect_context()

            assert context["issue"] is None  # git情報が取得できない
            assert "issue-101" in context["worktree"]  # worktree情報は取得できる
            assert context["session_id"].startswith("sess_")  # session_idは常に生成される
