"""
レビューアサインメントの適切性を検証するテスト。

Issue #43: 各実装フェーズにおけるレビュアーロール・モデルの適切性を検証する
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_file(relative_path: str) -> str:
    """指定パスのファイル内容を読み込む。"""
    path = os.path.join(BASE_DIR, relative_path)
    with open(path, encoding="utf-8") as f:
        return f.read()


class TestModelRecommendation:
    """各レビューファイルに推奨モデルセクションが存在することを検証する。"""

    def test_plan_reviewer_has_model_recommendation(self):
        content = read_file(".claude/agents/plan-reviewer.md")
        assert "## Model Recommendation" in content
        assert "sonnet" in content.lower() or "Sonnet" in content

    def test_reviewer_has_model_recommendation(self):
        content = read_file(".claude/agents/reviewer.md")
        assert "## Model Recommendation" in content
        assert "sonnet" in content.lower() or "Sonnet" in content

    def test_tdd_cycle_has_model_recommendation(self):
        content = read_file(".claude/skills/tdd-cycle/SKILL.md")
        assert "## Model Recommendation" in content or "### Model Recommendation" in content
        assert "haiku" in content.lower() or "Haiku" in content

    def test_progressive_review_has_model_recommendation(self):
        content = read_file(".claude/skills/progressive-review/SKILL.md")
        assert "## Model Recommendation" in content
        assert "sonnet" in content.lower() or "Sonnet" in content

    def test_model_recommendation_includes_rationale(self):
        """推奨モデルに根拠が含まれていることを確認する。"""
        files = [
            ".claude/agents/plan-reviewer.md",
            ".claude/agents/reviewer.md",
            ".claude/skills/tdd-cycle/SKILL.md",
            ".claude/skills/progressive-review/SKILL.md",
        ]
        for file_path in files:
            content = read_file(file_path)
            model_section_match = re.search(
                r"##[#]? Model Recommendation[^\n]*\n(.*?)(?=\n##[^#]|\Z)",
                content,
                re.DOTALL,
            )
            assert model_section_match is not None, f"{file_path} にModel Recommendationセクションがない"
            section_content = model_section_match.group(1)
            assert len(section_content.strip()) > 50, (
                f"{file_path} のModel Recommendationセクションに十分な根拠がない"
            )


class TestThreeWayRelationship:
    """reviewer.md / progressive-review / review.md の3者関係が明確に定義されていることを検証する。"""

    def test_reviewer_has_role_clarification(self):
        """reviewer.mdにprogressive-reviewとの使い分けが記述されている。"""
        content = read_file(".claude/agents/reviewer.md")
        assert "progressive-review" in content.lower() or "Progressive Review" in content

    def test_progressive_review_has_role_clarification(self):
        """progressive-review にreviewer.mdとの使い分けが記述されている。"""
        content = read_file(".claude/skills/progressive-review/SKILL.md")
        assert "reviewer.md" in content or "reviewer" in content.lower()

    def test_review_command_has_relationship_description(self):
        """review.md にprogressive-reviewとの関係が記述されている。"""
        content = read_file(".claude/commands/review.md")
        assert "progressive-review" in content.lower() or "Progressive Review" in content


class TestReviewAssignmentGuide:
    """レビューアサインメントガイドラインが存在し、必要な内容を含んでいることを検証する。"""

    def test_guide_file_exists(self):
        path = os.path.join(BASE_DIR, ".claude/rules/review-assignment-guide.md")
        assert os.path.exists(path), "review-assignment-guide.md が存在しない"

    def test_guide_has_decision_flow(self):
        """判断フローが含まれている。"""
        content = read_file(".claude/rules/review-assignment-guide.md")
        assert "判断" in content or "フロー" in content or "decision" in content.lower()

    def test_guide_has_model_selection_criteria(self):
        """モデル選択基準が含まれている。"""
        content = read_file(".claude/rules/review-assignment-guide.md")
        assert "モデル" in content or "model" in content.lower()
        assert "基準" in content or "criteria" in content.lower() or "選択" in content

    def test_guide_has_role_template(self):
        """ロール定義テンプレートが含まれている。"""
        content = read_file(".claude/rules/review-assignment-guide.md")
        assert "テンプレート" in content or "template" in content.lower()

    def test_guide_has_codex_delegation_section(self):
        """Issue #45 Codex委任に関するセクションが含まれている。"""
        content = read_file(".claude/rules/review-assignment-guide.md")
        assert "Codex" in content or "委任" in content or "delegation" in content.lower()

    def test_guide_has_complexity_assessment(self):
        """タスク複雑度の評価軸が含まれている。"""
        content = read_file(".claude/rules/review-assignment-guide.md")
        assert "複雑度" in content or "complexity" in content.lower() or "コンテキスト" in content


class TestTddReviewPolicy:
    """TDD REVIEWの実行方式方針が記述されていることを検証する。"""

    def test_tdd_cycle_has_execution_policy(self):
        """tdd-cycle SKILL.mdに実行方式の方針が記述されている。"""
        content = read_file(".claude/skills/tdd-cycle/SKILL.md")
        assert "メインエージェント" in content or "実行方式" in content or "execution" in content.lower()

    def test_tdd_command_consistent_with_skill(self):
        """tdd.mdとtdd-cycle/SKILL.mdで推奨モデル情報が整合している。"""
        tdd_cmd = read_file(".claude/commands/tdd.md")
        tdd_skill = read_file(".claude/skills/tdd-cycle/SKILL.md")
        # 両方にREVIEWフェーズへの言及がある
        assert "REVIEW" in tdd_cmd
        assert "REVIEW" in tdd_skill


class TestIssue45Preparation:
    """Issue #45（Codex委任）への準備が各ファイルに注記されていることを検証する。"""

    def test_guide_mentions_issue_45(self):
        """ガイドラインにIssue #45への言及がある。"""
        content = read_file(".claude/rules/review-assignment-guide.md")
        assert "#45" in content or "Issue 45" in content or "Codex" in content
