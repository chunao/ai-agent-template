"""Token usage logger."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional


def _now_iso() -> str:
    """現在時刻をISO形式で取得."""
    return datetime.now(timezone.utc).isoformat()


class TokenUsageLogger:
    """トークン消費量を記録するロガー."""

    def __init__(self, base_dir: str = "D:/projects/P010/.token-usage"):
        """Initialize logger.

        Args:
            base_dir: ログを保存するベースディレクトリ
        """
        self.base_dir = Path(base_dir)
        self.sessions_dir = self.base_dir / "sessions"
        self.current_session_id: Optional[str] = None
        self.current_log_file: Optional[Path] = None
        self.cumulative_input = 0
        self.cumulative_output = 0
        self.tool_count = 0
        self.session_start_time: Optional[datetime] = None
        self.skill_start_times: Dict[str, datetime] = {}
        self.skill_tokens: Dict[str, Dict[str, int]] = {}

        # ディレクトリ作成
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def start_session(self, session_id: Optional[str] = None, issue: Optional[str] = None, worktree: Optional[str] = None) -> str:
        """セッションを開始.

        Args:
            session_id: セッションID（Noneの場合は自動生成）
            issue: Issue番号
            worktree: Worktreeパス

        Returns:
            セッションID
        """
        now = datetime.now(timezone.utc)
        self.session_start_time = now

        # セッションIDが指定されていない場合は自動生成
        if session_id is None:
            session_id = f"sess_{now.strftime('%Y%m%d_%H%M%S')}_{now.microsecond:06d}"

        self.current_session_id = session_id
        self.current_log_file = self.sessions_dir / f"{self.current_session_id}.jsonl"
        self.cumulative_input = 0
        self.cumulative_output = 0
        self.tool_count = 0

        # session_startイベントを記録
        event = {
            "timestamp": _now_iso(),
            "event": "session_start",
            "session_id": self.current_session_id,
        }
        if issue:
            event["issue"] = issue
        if worktree:
            event["worktree"] = worktree

        self._write_event(event)
        return self.current_session_id

    def log_tool_call(
        self,
        tool: Optional[str],
        params: Dict[str, Any],
        input_tokens: int,
        output_tokens: int,
        model: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        """ツール呼び出しを記録.

        Args:
            tool: ツール名
            params: パラメータ
            input_tokens: 入力トークン数
            output_tokens: 出力トークン数
            model: モデル名
            context: コンテキスト情報
        """
        if tool is None:
            raise ValueError("tool name is required")

        if self.current_session_id is None:
            raise RuntimeError("No active session")

        self.cumulative_input += input_tokens
        self.cumulative_output += output_tokens
        self.tool_count += 1

        # スキル別トークン集計
        if context and "skill" in context:
            skill = context["skill"]
            if skill not in self.skill_tokens:
                self.skill_tokens[skill] = {"input": 0, "output": 0, "tools": 0}
            self.skill_tokens[skill]["input"] += input_tokens
            self.skill_tokens[skill]["output"] += output_tokens
            self.skill_tokens[skill]["tools"] += 1

        event = {
            "timestamp": _now_iso(),
            "event": "tool_call",
            "tool": tool,
            "params": params,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model": model,
            "cumulative_input": self.cumulative_input,
            "cumulative_output": self.cumulative_output,
        }
        if context:
            event["context"] = context

        self._write_event(event)

    def start_skill(self, skill: str, issue: Optional[str] = None):
        """スキル開始を記録.

        Args:
            skill: スキル名
            issue: Issue番号
        """
        if self.current_session_id is None:
            raise RuntimeError("No active session")

        now = datetime.now(timezone.utc)
        self.skill_start_times[skill] = now
        self.skill_tokens[skill] = {"input": 0, "output": 0, "tools": 0}

        event = {
            "timestamp": _now_iso(),
            "event": "skill_start",
            "skill": skill,
        }
        if issue:
            event["issue"] = issue

        self._write_event(event)

    def end_skill(self, skill: str):
        """スキル終了を記録.

        Args:
            skill: スキル名
        """
        if self.current_session_id is None:
            raise RuntimeError("No active session")

        now = datetime.now(timezone.utc)
        duration = 0
        if skill in self.skill_start_times:
            duration = int((now - self.skill_start_times[skill]).total_seconds())

        tokens = self.skill_tokens.get(skill, {"input": 0, "output": 0, "tools": 0})

        event = {
            "timestamp": _now_iso(),
            "event": "skill_end",
            "skill": skill,
            "duration_sec": duration,
            "total_input": tokens["input"],
            "total_output": tokens["output"],
            "tool_calls": tokens["tools"],
        }

        self._write_event(event)

    def log_external_delegation(
        self,
        delegate_to: str,
        task: str,
        estimated_tokens_saved: int,
    ):
        """外部AI委任を記録.

        Args:
            delegate_to: 委任先
            task: タスク名
            estimated_tokens_saved: 節約トークン数（推定）
        """
        if self.current_session_id is None:
            raise RuntimeError("No active session")

        event = {
            "timestamp": _now_iso(),
            "event": "external_delegation",
            "delegate_to": delegate_to,
            "task": task,
            "estimated_tokens_saved": estimated_tokens_saved,
        }

        self._write_event(event)

    def end_session(self):
        """セッションを終了."""
        if self.current_session_id is None:
            raise RuntimeError("No active session")

        now = datetime.now(timezone.utc)
        duration = 0
        if self.session_start_time:
            duration = int((now - self.session_start_time).total_seconds())

        event = {
            "timestamp": _now_iso(),
            "event": "session_end",
            "total_input": self.cumulative_input,
            "total_output": self.cumulative_output,
            "total_tools": self.tool_count,
            "duration_sec": duration,
        }

        self._write_event(event)

        # セッションをクリア
        self.current_session_id = None
        self.current_log_file = None

    def _write_event(self, event: Dict[str, Any]):
        """イベントをJSONL形式で書き込み.

        Args:
            event: イベントデータ
        """
        if self.current_log_file is None:
            raise RuntimeError("No active log file")

        with open(self.current_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
