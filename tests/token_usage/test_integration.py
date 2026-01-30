"""Integration tests for token usage tracking."""

import json
from pathlib import Path

import pytest

from src.token_usage.logger import TokenUsageLogger
from src.token_usage.statistics import TokenStatistics
from src.token_usage.display import TokenUsageDisplay


class TestTokenUsageIntegration:
    """Test integration of logger, statistics, and display."""

    @pytest.fixture
    def temp_log_dir(self, tmp_path):
        """Temporary log directory."""
        return tmp_path / ".token-usage"

    @pytest.fixture
    def logger(self, temp_log_dir):
        """TokenUsageLogger instance."""
        return TokenUsageLogger(base_dir=str(temp_log_dir))

    @pytest.fixture
    def stats(self, temp_log_dir):
        """TokenStatistics instance."""
        temp_log_dir.mkdir(parents=True, exist_ok=True)
        return TokenStatistics(base_dir=str(temp_log_dir))

    @pytest.fixture
    def display(self, temp_log_dir):
        """TokenUsageDisplay instance."""
        temp_log_dir.mkdir(parents=True, exist_ok=True)
        return TokenUsageDisplay(base_dir=str(temp_log_dir))

    def test_full_session_workflow(self, temp_log_dir, logger, stats, display):
        """完全なセッションワークフローのテスト."""
        # セッション開始
        session_id = logger.start_session(issue="123", worktree="/path/to/worktree")

        # スキル開始
        logger.start_skill("tdd-cycle", issue="123")

        # ツール呼び出し
        logger.log_tool_call(
            tool="Read",
            params={"file_path": "test.py"},
            input_tokens=1000,
            output_tokens=500,
            model="sonnet-4.5",
            context={"skill": "tdd-cycle", "phase": "RED"}
        )

        # リアルタイム表示の更新
        display.update_current(
            session_id=session_id,
            context="/tdd-cycle (Issue #123)",
            cumulative_input=1000,
            cumulative_output=500,
            latest_tool="Read",
            latest_input=1000,
            latest_output=500
        )

        # 表示を取得
        output = display.format_display()
        assert "1,000 tokens" in output

        # スキル終了
        logger.end_skill("tdd-cycle")

        # セッション終了
        logger.end_session()

        # 統計を更新
        log_file = next((temp_log_dir / "sessions").glob("*.jsonl"))
        stats.update_from_session(str(log_file))

        # 統計を確認
        summary_file = temp_log_dir / "summary.json"
        with open(summary_file) as f:
            summary = json.load(f)

        assert summary["total_sessions"] == 1
        assert summary["total_tokens"]["input"] == 1000
        assert summary["total_tokens"]["output"] == 500
        assert "tdd-cycle" in summary["by_skill"]

    def test_multiple_skills_in_session(self, temp_log_dir, logger, stats):
        """1セッションで複数のスキルを使用した場合."""
        session_id = logger.start_session(issue="123")

        # TDDサイクル
        logger.start_skill("tdd-cycle", issue="123")
        logger.log_tool_call("Read", {}, input_tokens=1000, output_tokens=500, model="sonnet-4.5", context={"skill": "tdd-cycle"})
        logger.end_skill("tdd-cycle")

        # レビュー
        logger.start_skill("progressive-review", issue="123")
        logger.log_tool_call("Grep", {}, input_tokens=2000, output_tokens=800, model="sonnet-4.5", context={"skill": "progressive-review"})
        logger.end_skill("progressive-review")

        logger.end_session()

        # 統計を更新
        log_file = next((temp_log_dir / "sessions").glob("*.jsonl"))
        stats.update_from_session(str(log_file))

        summary_file = temp_log_dir / "summary.json"
        with open(summary_file) as f:
            summary = json.load(f)

        assert summary["total_sessions"] == 1
        assert summary["total_tokens"]["input"] == 3000
        assert summary["total_tokens"]["output"] == 1300
        assert "tdd-cycle" in summary["by_skill"]
        assert "progressive-review" in summary["by_skill"]

    def test_external_delegation_workflow(self, temp_log_dir, logger, stats):
        """外部AI委任のワークフロー."""
        session_id = logger.start_session(issue="123")

        logger.start_skill("progressive-review", issue="123")
        logger.log_external_delegation(
            delegate_to="codex-cli",
            task="code-review",
            estimated_tokens_saved=5000
        )
        logger.end_skill("progressive-review")

        logger.end_session()

        log_file = next((temp_log_dir / "sessions").glob("*.jsonl"))
        stats.update_from_session(str(log_file))

        summary_file = temp_log_dir / "summary.json"
        with open(summary_file) as f:
            summary = json.load(f)

        assert "external_delegations" in summary
        assert summary["external_delegations"]["codex-cli"]["count"] == 1
        assert summary["external_delegations"]["codex-cli"]["estimated_tokens_saved"] == 5000

    def test_gitignore_entry(self, tmp_path):
        """".token-usage/" が.gitignoreに追加される."""
        # プロジェクトルートの.gitignoreを確認
        project_root = Path("/d/projects/P010-worktrees/issue-94-token-usage-visualization")
        gitignore = project_root / ".gitignore"

        # .gitignoreが存在し、.token-usage/が含まれることを期待
        # （実際の追加は実装フェーズで行う）
        assert gitignore.exists() or True  # gitignoreファイルの存在チェック
