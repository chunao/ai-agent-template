"""ci-analyzer スキル定義のテスト

Issue #13: PR作成後のCI結果自動確認機能を追加する
"""

from pathlib import Path

import pytest


class TestCiAnalyzerSkill:
    """ci-analyzer スキル定義のテスト"""

    @pytest.fixture
    def skill_path(self) -> Path:
        """スキルファイルのパスを返す"""
        return Path(__file__).parent.parent / ".claude" / "skills" / "ci-analyzer" / "SKILL.md"

    @pytest.fixture
    def skill_content(self, skill_path: Path) -> str:
        """スキルファイルの内容を読み込む"""
        if not skill_path.exists():
            pytest.skip(f"Skill file not found: {skill_path}")
        return skill_path.read_text(encoding="utf-8")

    def test_skill_file_exists(self, skill_path: Path):
        """スキルファイルが存在すること"""
        assert skill_path.exists(), f"Skill file should exist at {skill_path}"

    def test_skill_has_frontmatter(self, skill_content: str):
        """フロントマターがあること"""
        assert skill_content.startswith("---"), "Skill should have YAML frontmatter"
        assert skill_content.count("---") >= 2, "Skill should have complete frontmatter"

    def test_skill_has_name(self, skill_content: str):
        """nameフィールドがあること"""
        assert "name:" in skill_content, "Skill should have name field"
        assert "ci-analyzer" in skill_content, "Skill name should be ci-analyzer"

    def test_skill_has_description(self, skill_content: str):
        """descriptionフィールドがあること"""
        assert "description:" in skill_content, "Skill should have description field"

    def test_skill_analyzes_logs(self, skill_content: str):
        """ログ解析機能があること"""
        content_lower = skill_content.lower()
        has_log = "ログ" in skill_content or "log" in content_lower
        has_analyze = "解析" in skill_content or "分析" in skill_content or "analyz" in content_lower
        assert has_log and has_analyze, "Skill should analyze logs"

    def test_skill_categorizes_errors(self, skill_content: str):
        """エラーをカテゴリ分けすること"""
        content_lower = skill_content.lower()
        has_category = "カテゴリ" in skill_content or "categor" in content_lower or "パターン" in skill_content or "pattern" in content_lower
        has_error = "エラー" in skill_content or "error" in content_lower or "失敗" in skill_content or "fail" in content_lower
        assert has_category and has_error, "Skill should categorize errors"

    def test_skill_identifies_test_failures(self, skill_content: str):
        """テスト失敗を識別できること"""
        content_lower = skill_content.lower()
        has_test = "テスト" in skill_content or "test" in content_lower or "pytest" in content_lower
        has_failure = "失敗" in skill_content or "fail" in content_lower or "error" in content_lower
        assert has_test and has_failure, "Skill should identify test failures"

    def test_skill_identifies_dependency_errors(self, skill_content: str):
        """依存関係エラーを識別できること"""
        content_lower = skill_content.lower()
        has_dep = "依存" in skill_content or "dependen" in content_lower or "module" in content_lower or "import" in content_lower
        assert has_dep, "Skill should identify dependency errors"

    def test_skill_identifies_syntax_errors(self, skill_content: str):
        """構文エラーを識別できること"""
        content_lower = skill_content.lower()
        has_syntax = "構文" in skill_content or "syntax" in content_lower
        assert has_syntax, "Skill should identify syntax errors"

    def test_skill_provides_recommendations(self, skill_content: str):
        """改善提案を提供すること"""
        content_lower = skill_content.lower()
        has_recommend = "推奨" in skill_content or "提案" in skill_content or "recommend" in content_lower or \
                        "suggest" in content_lower or "対処" in skill_content or "修正" in skill_content
        assert has_recommend, "Skill should provide recommendations"

    def test_skill_uses_gh_run_view_log(self, skill_content: str):
        """gh run view --log を使用すること"""
        assert "gh run view" in skill_content and "--log" in skill_content, \
            "Skill should use 'gh run view --log' for log retrieval"
