"""Token usage statistics."""

import json
from pathlib import Path
from typing import Dict, Any, List


class TokenStatistics:
    """トークン消費統計を管理."""

    def __init__(self, base_dir: str = "D:/projects/P010/.token-usage"):
        """Initialize statistics.

        Args:
            base_dir: 統計ファイルを保存するベースディレクトリ
        """
        self.base_dir = Path(base_dir)
        self.summary_file = self.base_dir / "summary.json"

        # デフォルト統計
        self.default_summary = {
            "total_sessions": 0,
            "total_tokens": {"input": 0, "output": 0},
            "by_skill": {},
            "by_tool": {},
            "external_delegations": {},
            "top_token_consumers": [],
        }

        # summary.jsonの初期化
        if self.summary_file.exists():
            try:
                with open(self.summary_file, encoding="utf-8") as f:
                    self.summary = json.load(f)
            except (json.JSONDecodeError, IOError):
                # 破損している場合はデフォルトで上書き
                self.summary = self.default_summary.copy()
                self._save_summary()
        else:
            self.summary = self.default_summary.copy()
            self._save_summary()

    def update_from_session(self, log_file_path: str):
        """セッションログから統計を更新.

        Args:
            log_file_path: セッションログファイルのパス
        """
        log_file = Path(log_file_path)
        if not log_file.exists():
            return

        # ログファイルを読み込み
        events = []
        with open(log_file, encoding="utf-8") as f:
            for line in f:
                events.append(json.loads(line))

        # セッション統計を抽出
        session_input = 0
        session_output = 0
        skill_stats: Dict[str, Dict[str, int]] = {}
        tool_stats: Dict[str, List[Dict[str, int]]] = {}
        external_delegations: Dict[str, Dict[str, int]] = {}

        for event in events:
            event_type = event.get("event")

            if event_type == "session_end":
                session_input = event.get("total_input", 0)
                session_output = event.get("total_output", 0)

            elif event_type == "skill_end":
                skill = event.get("skill")
                if skill:
                    skill_stats[skill] = {
                        "input": event.get("total_input", 0),
                        "output": event.get("total_output", 0),
                    }

            elif event_type == "tool_call":
                tool = event.get("tool")
                if tool:
                    if tool not in tool_stats:
                        tool_stats[tool] = []
                    tool_stats[tool].append({
                        "input": event.get("input_tokens", 0),
                        "output": event.get("output_tokens", 0),
                    })

            elif event_type == "external_delegation":
                delegate_to = event.get("delegate_to")
                if delegate_to:
                    if delegate_to not in external_delegations:
                        external_delegations[delegate_to] = {"count": 0, "tokens_saved": 0}
                    external_delegations[delegate_to]["count"] += 1
                    external_delegations[delegate_to]["tokens_saved"] += event.get("estimated_tokens_saved", 0)

        # 累積統計を更新
        self.summary["total_sessions"] += 1
        self.summary["total_tokens"]["input"] += session_input
        self.summary["total_tokens"]["output"] += session_output

        # スキル別統計を更新
        for skill, tokens in skill_stats.items():
            if skill not in self.summary["by_skill"]:
                self.summary["by_skill"][skill] = {
                    "sessions": 0,
                    "total_input": 0,
                    "total_output": 0,
                    "avg_input": 0,
                    "avg_output": 0,
                }

            stats = self.summary["by_skill"][skill]
            stats["sessions"] += 1
            stats["total_input"] += tokens["input"]
            stats["total_output"] += tokens["output"]
            stats["avg_input"] = stats["total_input"] // stats["sessions"]
            stats["avg_output"] = stats["total_output"] // stats["sessions"]

        # ツール別統計を更新
        for tool, calls in tool_stats.items():
            if tool not in self.summary["by_tool"]:
                self.summary["by_tool"][tool] = {
                    "calls": 0,
                    "total_input": 0,
                    "total_output": 0,
                    "avg_input": 0,
                    "avg_output": 0,
                }

            stats = self.summary["by_tool"][tool]
            for call in calls:
                stats["calls"] += 1
                stats["total_input"] += call["input"]
                stats["total_output"] += call["output"]

            stats["avg_input"] = stats["total_input"] // stats["calls"]
            stats["avg_output"] = stats["total_output"] // stats["calls"]

        # 外部AI委任統計を更新
        for delegate_to, data in external_delegations.items():
            if delegate_to not in self.summary["external_delegations"]:
                self.summary["external_delegations"][delegate_to] = {
                    "count": 0,
                    "estimated_tokens_saved": 0,
                }

            self.summary["external_delegations"][delegate_to]["count"] += data["count"]
            self.summary["external_delegations"][delegate_to]["estimated_tokens_saved"] += data["tokens_saved"]

        # トップコンシューマーを更新
        self._update_top_consumers()

        # 保存
        self._save_summary()

    def _update_top_consumers(self):
        """トップトークンコンシューマーを更新."""
        consumers = []

        for skill, stats in self.summary["by_skill"].items():
            avg_total = stats["avg_input"] + stats["avg_output"]
            consumers.append({"context": skill, "avg_total": avg_total})

        # 降順ソート
        consumers.sort(key=lambda x: x["avg_total"], reverse=True)
        self.summary["top_token_consumers"] = consumers

    def _save_summary(self):
        """統計をファイルに保存."""
        with open(self.summary_file, "w", encoding="utf-8") as f:
            json.dump(self.summary, f, indent=2, ensure_ascii=False)
