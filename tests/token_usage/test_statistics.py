"""Tests for token usage statistics."""

import json
from pathlib import Path

import pytest

from src.token_usage.statistics import TokenStatistics


class TestTokenStatistics:
    """Test TokenStatistics functionality."""

    @pytest.fixture
    def temp_log_dir(self, tmp_path):
        """Temporary log directory."""
        return tmp_path / ".token-usage"

    @pytest.fixture
    def stats(self, temp_log_dir):
        """TokenStatistics instance with temporary directory."""
        temp_log_dir.mkdir(parents=True, exist_ok=True)
        return TokenStatistics(base_dir=str(temp_log_dir))

    @pytest.fixture
    def sample_session_log(self, temp_log_dir):
        """サンプルセッションログを作成."""
        sessions_dir = temp_log_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        log_file = sessions_dir / "2026-01-29_143022.jsonl"

        events = [
            {"timestamp": "2026-01-29T14:30:22Z", "event": "session_start", "session_id": "sess_abc123", "issue": "123"},
            {"timestamp": "2026-01-29T14:30:30Z", "event": "skill_start", "skill": "tdd-cycle", "issue": "123"},
            {"timestamp": "2026-01-29T14:30:35Z", "event": "tool_call", "tool": "Read", "params": {}, "input_tokens": 1000, "output_tokens": 500, "model": "sonnet-4.5", "cumulative_input": 1000, "cumulative_output": 500, "context": {"skill": "tdd-cycle", "phase": "RED"}},
            {"timestamp": "2026-01-29T14:30:40Z", "event": "tool_call", "tool": "Edit", "params": {}, "input_tokens": 2000, "output_tokens": 800, "model": "sonnet-4.5", "cumulative_input": 3000, "cumulative_output": 1300, "context": {"skill": "tdd-cycle", "phase": "GREEN"}},
            {"timestamp": "2026-01-29T14:31:00Z", "event": "skill_end", "skill": "tdd-cycle", "duration_sec": 30, "total_input": 3000, "total_output": 1300, "tool_calls": 2},
            {"timestamp": "2026-01-29T14:32:00Z", "event": "session_end", "total_input": 3000, "total_output": 1300, "total_tools": 2, "duration_sec": 98}
        ]

        with open(log_file, "w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        return log_file

    def test_init_creates_summary_file(self, temp_log_dir, stats):
        """初期化時にsummary.jsonが作成される."""
        summary_file = temp_log_dir / "summary.json"
        assert summary_file.exists()

        with open(summary_file) as f:
            summary = json.load(f)

        assert summary["total_sessions"] == 0
        assert summary["total_tokens"]["input"] == 0
        assert summary["total_tokens"]["output"] == 0

    def test_update_from_session_aggregates_data(self, temp_log_dir, stats, sample_session_log):
        """セッションログから統計が集計される."""
        stats.update_from_session(str(sample_session_log))

        summary_file = temp_log_dir / "summary.json"
        with open(summary_file) as f:
            summary = json.load(f)

        assert summary["total_sessions"] == 1
        assert summary["total_tokens"]["input"] == 3000
        assert summary["total_tokens"]["output"] == 1300

    def test_skill_statistics(self, temp_log_dir, stats, sample_session_log):
        """スキル別統計が集計される."""
        stats.update_from_session(str(sample_session_log))

        summary_file = temp_log_dir / "summary.json"
        with open(summary_file) as f:
            summary = json.load(f)

        assert "tdd-cycle" in summary["by_skill"]
        skill_stats = summary["by_skill"]["tdd-cycle"]
        assert skill_stats["sessions"] == 1
        assert skill_stats["avg_input"] == 3000
        assert skill_stats["avg_output"] == 1300

    def test_tool_statistics(self, temp_log_dir, stats, sample_session_log):
        """ツール別統計が集計される."""
        stats.update_from_session(str(sample_session_log))

        summary_file = temp_log_dir / "summary.json"
        with open(summary_file) as f:
            summary = json.load(f)

        assert "Read" in summary["by_tool"]
        assert "Edit" in summary["by_tool"]

        read_stats = summary["by_tool"]["Read"]
        assert read_stats["calls"] == 1
        assert read_stats["avg_input"] == 1000
        assert read_stats["avg_output"] == 500

    def test_top_consumers_ranking(self, temp_log_dir, stats, sample_session_log):
        """トップコンシューマーがランキングされる."""
        stats.update_from_session(str(sample_session_log))

        summary_file = temp_log_dir / "summary.json"
        with open(summary_file) as f:
            summary = json.load(f)

        assert "top_token_consumers" in summary
        assert len(summary["top_token_consumers"]) > 0
        top = summary["top_token_consumers"][0]
        assert top["context"] == "tdd-cycle"
        assert top["avg_total"] == 4300  # 3000 + 1300

    def test_multiple_sessions_accumulate(self, temp_log_dir, stats, sample_session_log):
        """複数セッションの統計が累積される."""
        stats.update_from_session(str(sample_session_log))
        stats.update_from_session(str(sample_session_log))  # 同じログを2回処理

        summary_file = temp_log_dir / "summary.json"
        with open(summary_file) as f:
            summary = json.load(f)

        assert summary["total_sessions"] == 2
        assert summary["total_tokens"]["input"] == 6000
        assert summary["total_tokens"]["output"] == 2600

        skill_stats = summary["by_skill"]["tdd-cycle"]
        assert skill_stats["sessions"] == 2
        assert skill_stats["avg_input"] == 3000  # 平均は変わらない

    def test_external_delegation_tracking(self, temp_log_dir, stats):
        """外部AI委任の統計が集計される."""
        sessions_dir = temp_log_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        log_file = sessions_dir / "test.jsonl"

        events = [
            {"timestamp": "2026-01-29T14:30:22Z", "event": "session_start", "session_id": "sess_abc123"},
            {"timestamp": "2026-01-29T14:35:30Z", "event": "external_delegation", "delegate_to": "codex-cli", "task": "code-review", "estimated_tokens_saved": 3000},
            {"timestamp": "2026-01-29T14:40:00Z", "event": "session_end", "total_input": 0, "total_output": 0, "total_tools": 0, "duration_sec": 578}
        ]

        with open(log_file, "w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        stats.update_from_session(str(log_file))

        summary_file = temp_log_dir / "summary.json"
        with open(summary_file) as f:
            summary = json.load(f)

        assert "external_delegations" in summary
        assert "codex-cli" in summary["external_delegations"]
        codex_stats = summary["external_delegations"]["codex-cli"]
        assert codex_stats["count"] == 1
        assert codex_stats["estimated_tokens_saved"] == 3000

    def test_corrupted_summary_fallback(self, temp_log_dir, stats):
        """破損したsummary.jsonの読み込み時にフォールバックする."""
        summary_file = temp_log_dir / "summary.json"
        with open(summary_file, "w") as f:
            f.write("invalid json{{{")

        # 新しいインスタンスを作成（破損したファイルを読み込む）
        stats_new = TokenStatistics(base_dir=str(temp_log_dir))

        # デフォルト値で初期化されている
        with open(summary_file) as f:
            summary = json.load(f)

        assert summary["total_sessions"] == 0
        assert summary["total_tokens"]["input"] == 0
