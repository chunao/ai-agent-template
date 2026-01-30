"""Token usage display."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _now_iso() -> str:
    """現在時刻をISO形式で取得."""
    return datetime.now(timezone.utc).isoformat()


class TokenUsageDisplay:
    """トークン消費状況の表示."""

    def __init__(self, base_dir: str = "D:/projects/P010/.token-usage"):
        """Initialize display.

        Args:
            base_dir: current.jsonを保存するベースディレクトリ
        """
        self.base_dir = Path(base_dir)
        self.current_file = self.base_dir / "current.json"

    def update_current(
        self,
        session_id: str,
        context: str,
        cumulative_input: int,
        cumulative_output: int,
        latest_tool: str,
        latest_input: int,
        latest_output: int,
        latest_file: Optional[str] = None,
    ):
        """current.jsonを更新.

        Args:
            session_id: セッションID
            context: 現在のコンテキスト
            cumulative_input: 累積入力トークン
            cumulative_output: 累積出力トークン
            latest_tool: 最新のツール名
            latest_input: 最新の入力トークン
            latest_output: 最新の出力トークン
            latest_file: 最新のファイル名
        """
        data = {
            "session_id": session_id,
            "timestamp": _now_iso(),
            "current_context": context,
            "cumulative": {
                "input": cumulative_input,
                "output": cumulative_output,
                "total": cumulative_input + cumulative_output,
            },
            "latest": {
                "timestamp": _now_iso(),
                "tool": latest_tool,
                "input": latest_input,
                "output": latest_output,
            },
        }

        if latest_file:
            data["latest"]["file"] = latest_file

        with open(self.current_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def format_display(self) -> str:
        """表示フォーマットを生成.

        Returns:
            フォーマット済み表示文字列
        """
        if not self.current_file.exists():
            return ""

        try:
            with open(self.current_file, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return ""

        session_id = data.get("session_id", "unknown")
        context = data.get("current_context", "")
        cumulative = data.get("cumulative", {})
        latest = data.get("latest", {})

        lines = [
            "━" * 40,
            f"📊 Token Usage (Session: {session_id})",
            "━" * 40,
            f"Current Context: {context}",
            "",
            "Cumulative:",
            f"  Input:  {self._format_number(cumulative.get('input', 0))} tokens",
            f"  Output:  {self._format_number(cumulative.get('output', 0))} tokens",
            f"  Total:  {self._format_number(cumulative.get('total', 0))} tokens",
            "",
            f"Latest ({latest.get('timestamp', '')}):",
            f"  Tool: {latest.get('tool', 'unknown')}"
            + (f" ({latest.get('file', '')})" if latest.get('file') else ""),
            f"  Input:  {self._format_number(latest.get('input', 0))} tokens",
            f"  Output:  {self._format_number(latest.get('output', 0))} tokens",
            "━" * 40,
        ]

        return "\n".join(lines)

    def _format_number(self, num: int) -> str:
        """数値をカンマ区切りフォーマット.

        Args:
            num: フォーマット対象の数値

        Returns:
            カンマ区切りの文字列
        """
        return f"{num:,}"

    def clear_current(self):
        """current.jsonをクリア."""
        if self.current_file.exists():
            self.current_file.unlink()
