"""Skill wrapper for automatic token usage tracking.

Issue #101: トークン使用量記録の自動化（Phase 4.1）
"""

import os
import logging
from typing import Optional

from src.token_usage.logger import TokenUsageLogger
from src.token_usage.context_detector import detect_context


# ロガー設定
logger = logging.getLogger(__name__)


def is_token_usage_enabled() -> bool:
    """環境変数でトークン記録が有効かどうかを確認する.

    Returns:
        トークン記録が有効な場合True、無効な場合False
        デフォルト: True（環境変数未設定時）
    """
    enabled = os.environ.get("TOKEN_USAGE_ENABLED", "true")
    return enabled.lower() not in ("false", "0", "no")


def auto_skill_start(skill_name: str) -> Optional[str]:
    """スキル開始時に自動的にsession_start/skill_startを記録する.

    Args:
        skill_name: スキル名（例: "tdd", "start-issue", "review"）

    Returns:
        セッションID（記録成功時）、記録失敗時またはTOKEN_USAGE_ENABLED=false時はNone
    """
    if not is_token_usage_enabled():
        return None

    try:
        # コンテキスト情報を自動検出
        context = detect_context()

        # TokenUsageLoggerを初期化
        logger_instance = TokenUsageLogger()

        # セッション開始
        logger_instance.start_session(
            session_id=context["session_id"],
            issue=context["issue"],
            worktree=context["worktree"]
        )

        # スキル開始
        logger_instance.start_skill(skill_name)

        # コンテキストのsession_idを返す
        return context["session_id"]

    except Exception as e:
        logger.warning(f"Failed to record skill start: {e}")
        return None


def auto_skill_end(skill_name: str, session_id: Optional[str] = None) -> None:
    """スキル終了時に自動的にskill_end/session_endを記録する.

    Args:
        skill_name: スキル名（例: "tdd", "start-issue", "review"）
        session_id: セッションID（auto_skill_startの戻り値）
                   Noneの場合は記録をスキップ
    """
    if not is_token_usage_enabled():
        return

    # session_idがNoneの場合は記録をスキップ（start時に失敗したケース）
    if session_id is None:
        logger.warning(f"Skipping skill end recording: session_id is None")
        return

    try:
        # session_idを使ってTokenUsageLoggerを初期化し、セッションを再開
        logger_instance = TokenUsageLogger()
        logger_instance.resume_session(session_id)

        # スキル終了
        logger_instance.end_skill(skill_name)

        # セッション終了
        logger_instance.end_session()

    except Exception as e:
        logger.warning(f"Failed to record skill end: {e}")
