"""ci-fixer エージェント定義のテスト

Issue #13: PR作成後のCI結果自動確認機能を追加する
"""

from pathlib import Path

import pytest


class TestCiFixerAgent:
    """ci-fixer エージェント定義のテスト"""

    @pytest.fixture
    def agent_path(self) -> Path:
        """エージェントファイルのパスを返す"""
        return Path(__file__).parent.parent / ".claude" / "agents" / "ci-fixer.md"

    @pytest.fixture
    def agent_content(self, agent_path: Path) -> str:
        """エージェントファイルの内容を読み込む"""
        if not agent_path.exists():
            pytest.skip(f"Agent file not found: {agent_path}")
        return agent_path.read_text(encoding="utf-8")

    def test_agent_file_exists(self, agent_path: Path):
        """エージェントファイルが存在すること"""
        assert agent_path.exists(), f"Agent file should exist at {agent_path}"

    def test_agent_has_title(self, agent_content: str):
        """タイトルがあること"""
        assert "# CI Fixer" in agent_content or "# ci-fixer" in agent_content.lower(), \
            "Agent should have a title"

    def test_agent_has_role_section(self, agent_content: str):
        """Roleセクションがあること"""
        assert "Role" in agent_content or "役割" in agent_content, \
            "Agent should have Role section"

    def test_agent_has_capabilities(self, agent_content: str):
        """Capabilitiesセクションがあること"""
        assert "Capabilities" in agent_content or "機能" in agent_content or "能力" in agent_content, \
            "Agent should have Capabilities section"

    def test_agent_analyzes_ci_logs(self, agent_content: str):
        """CIログを解析すること"""
        content_lower = agent_content.lower()
        has_ci = "ci" in content_lower or "github actions" in content_lower
        has_log = "ログ" in agent_content or "log" in content_lower
        assert has_ci and has_log, "Agent should analyze CI logs"

    def test_agent_identifies_failures(self, agent_content: str):
        """失敗を識別すること"""
        content_lower = agent_content.lower()
        has_failure = "失敗" in agent_content or "fail" in content_lower or "error" in content_lower
        has_identify = "特定" in agent_content or "識別" in agent_content or "identify" in content_lower or "detect" in content_lower
        assert has_failure and has_identify, "Agent should identify failures"

    def test_agent_proposes_fixes(self, agent_content: str):
        """修正を提案すること"""
        content_lower = agent_content.lower()
        has_fix = "修正" in agent_content or "fix" in content_lower or "repair" in content_lower
        has_propose = "提案" in agent_content or "推奨" in agent_content or "propos" in content_lower or "suggest" in content_lower or "recommend" in content_lower
        assert has_fix and has_propose, "Agent should propose fixes"

    def test_agent_locates_source_files(self, agent_content: str):
        """ソースファイルを特定すること"""
        content_lower = agent_content.lower()
        has_source = "ソース" in agent_content or "source" in content_lower or "ファイル" in agent_content or "file" in content_lower
        has_locate = "特定" in agent_content or "locat" in content_lower or "find" in content_lower or "関連" in agent_content
        assert has_source and has_locate, "Agent should locate source files"

    def test_agent_has_workflow(self, agent_content: str):
        """ワークフローが定義されていること"""
        content_lower = agent_content.lower()
        has_workflow = "workflow" in content_lower or "process" in content_lower or \
                       "手順" in agent_content or "ステップ" in agent_content or "step" in content_lower
        assert has_workflow, "Agent should have defined workflow"

    def test_agent_provides_code_suggestions(self, agent_content: str):
        """コード修正案を提供すること"""
        content_lower = agent_content.lower()
        has_code = "コード" in agent_content or "code" in content_lower
        has_suggestion = "提案" in agent_content or "修正案" in agent_content or "suggest" in content_lower or "example" in content_lower
        assert has_code and has_suggestion, "Agent should provide code suggestions"
