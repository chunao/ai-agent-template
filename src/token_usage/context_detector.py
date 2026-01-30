"""Context detector for automatic token usage tracking.

Issue #101: トークン使用量記録の自動化（Phase 4.1）
"""

import logging
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict


# ロガー設定
logger = logging.getLogger(__name__)


def extract_issue_number() -> Optional[str]:
    """ブランチ名からIssue番号を抽出する.

    Returns:
        Issue番号（文字列）、取得できない場合はNone
    """
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10
        )

        if result.returncode != 0:
            return None

        branch_name = result.stdout.strip()

        # パターン: feature/issue-123-xxx → 123
        match = re.search(r'issue-(\d+)', branch_name)
        if match:
            return match.group(1)

        return None
    except subprocess.TimeoutExpired:
        logger.warning("Git command timed out while extracting issue number")
        return None
    except Exception as e:
        logger.warning(f"Failed to extract issue number: {e}")
        return None


def detect_worktree_path() -> Optional[str]:
    """カレントディレクトリからWorktreeパスを検出する.

    Returns:
        Worktreeパス（文字列）、検出できない場合はNone
    """
    try:
        cwd = Path.cwd()
        cwd_str = str(cwd)

        # worktreesディレクトリが含まれているかチェック
        if "worktrees" in cwd_str or "issue-" in cwd_str:
            return cwd_str

        return None
    except Exception as e:
        logger.warning(f"Failed to detect worktree path: {e}")
        return None


def generate_session_id() -> str:
    """一意なセッションIDを生成する（マイクロ秒精度）.

    Returns:
        セッションID（フォーマット: sess_YYYYMMDD_HHMMSS_μμμμμμ）
    """
    now = datetime.now(timezone.utc)
    return f"sess_{now.strftime('%Y%m%d_%H%M%S')}_{now.microsecond:06d}"


def detect_context() -> Dict[str, Optional[str]]:
    """Issue番号、Worktree情報、セッションIDを自動検出する.

    Returns:
        コンテキスト情報の辞書
        {
            "issue": Issue番号（Optional[str]）,
            "worktree": Worktreeパス（Optional[str]）,
            "session_id": セッションID（str）
        }
    """
    return {
        "issue": extract_issue_number(),
        "worktree": detect_worktree_path(),
        "session_id": generate_session_id()
    }
