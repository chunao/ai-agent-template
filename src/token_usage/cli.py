"""CLI entry point for token usage recording."""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional
from .logger import TokenUsageLogger


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """コマンドライン引数をパース.

    Args:
        args: 引数リスト（テスト用、Noneの場合はsys.argvを使用）

    Returns:
        パース済み引数
    """
    parser = argparse.ArgumentParser(description="Record token usage events")

    parser.add_argument("--event", required=True, help="Event type")
    parser.add_argument("--session-id", help="Session ID")
    parser.add_argument("--issue", help="Issue number")
    parser.add_argument("--worktree", help="Worktree path")
    parser.add_argument("--skill", help="Skill name")
    parser.add_argument("--tool", help="Tool name")
    parser.add_argument("--input-tokens", type=int, help="Input tokens")
    parser.add_argument("--output-tokens", type=int, help="Output tokens")
    parser.add_argument("--model", help="Model name")

    if args is None:
        return parser.parse_args()
    return parser.parse_args(args)


# グローバルロガーインスタンス（ディレクトリごとに管理）
_loggers: dict[str, TokenUsageLogger] = {}


def get_logger() -> TokenUsageLogger:
    """ロガーインスタンスを取得.

    環境変数TOKEN_USAGE_DIRに基づいてロガーを取得または作成します。
    異なるディレクトリに対しては別のロガーインスタンスを使用します。

    Returns:
        TokenUsageLogger インスタンス
    """
    base_dir = os.environ.get("TOKEN_USAGE_DIR", "D:/projects/P010/.token-usage")

    if base_dir not in _loggers:
        _loggers[base_dir] = TokenUsageLogger(base_dir=base_dir)

    return _loggers[base_dir]


def record_usage_cli(args: Optional[List[str]] = None):
    """CLIエントリーポイント.

    Args:
        args: 引数リスト（テスト用）
    """
    parsed = parse_args(args)
    logger = get_logger()

    event_type = parsed.event

    if event_type == "session_start":
        if not parsed.session_id:
            raise ValueError("--session-id is required for session_start")
        logger.start_session(
            session_id=parsed.session_id,
            issue=parsed.issue,
            worktree=parsed.worktree
        )

    elif event_type == "skill_start":
        if not parsed.skill:
            raise ValueError("--skill is required for skill_start")
        logger.start_skill(
            skill=parsed.skill,
            issue=parsed.issue
        )

    elif event_type == "skill_end":
        if not parsed.skill:
            raise ValueError("--skill is required for skill_end")
        logger.end_skill(skill=parsed.skill)

    elif event_type == "tool_call":
        if not parsed.tool:
            raise ValueError("--tool is required for tool_call")
        if parsed.input_tokens is None:
            raise ValueError("--input-tokens is required for tool_call")
        if parsed.output_tokens is None:
            raise ValueError("--output-tokens is required for tool_call")
        if not parsed.model:
            raise ValueError("--model is required for tool_call")

        logger.log_tool_call(
            tool=parsed.tool,
            params={},
            input_tokens=parsed.input_tokens,
            output_tokens=parsed.output_tokens,
            model=parsed.model,
            context=None
        )

    elif event_type == "session_end":
        logger.end_session()

    else:
        raise ValueError(f"Invalid event type: {event_type}")


def main():
    """メインエントリーポイント."""
    try:
        record_usage_cli()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
