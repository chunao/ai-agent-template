"""
AIレビュー結果コメントに実行情報（使用モデル）が記載されているかを検証するテスト

テスト対象:
- .claude/commands/review.md
- .claude/skills/tdd-cycle/SKILL.md
- .claude/agents/plan-reviewer.md
"""

import re
from pathlib import Path

import pytest


class TestReviewExecutionInfo:
    """AIレビュー実行情報の記載を検証"""

    @pytest.fixture
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリを取得"""
        # テストファイルから2階層上がプロジェクトルート
        return Path(__file__).parent.parent

    @pytest.fixture
    def review_md(self, project_root: Path) -> str:
        """review.mdの内容を取得"""
        file_path = project_root / ".claude" / "commands" / "review.md"
        return file_path.read_text(encoding="utf-8")

    @pytest.fixture
    def tdd_cycle_skill(self, project_root: Path) -> str:
        """tdd-cycle/SKILL.mdの内容を取得"""
        file_path = project_root / ".claude" / "skills" / "tdd-cycle" / "SKILL.md"
        return file_path.read_text(encoding="utf-8")

    @pytest.fixture
    def plan_reviewer(self, project_root: Path) -> str:
        """plan-reviewer.mdの内容を取得"""
        file_path = project_root / ".claude" / "agents" / "plan-reviewer.md"
        return file_path.read_text(encoding="utf-8")

    # TC01: review.mdに「実行情報」セクションが存在する
    def test_review_md_has_execution_info_section(self, review_md: str):
        """review.mdに「実行情報」セクションが存在することを確認"""
        assert "### 実行情報" in review_md, "review.mdに「実行情報」セクションが存在しません"

    # TC02: tdd-cycle/SKILL.mdに「実行情報」セクションが存在する
    def test_tdd_cycle_has_execution_info_section(self, tdd_cycle_skill: str):
        """tdd-cycle/SKILL.mdに「実行情報」セクションが存在することを確認"""
        assert (
            "### 実行情報" in tdd_cycle_skill
        ), "tdd-cycle/SKILL.mdに「実行情報」セクションが存在しません"

    # TC03: plan-reviewer.mdに「実行情報」セクションが存在する
    def test_plan_reviewer_has_execution_info_section(self, plan_reviewer: str):
        """plan-reviewer.mdに「実行情報」セクションが存在することを確認"""
        assert (
            "### 実行情報" in plan_reviewer
        ), "plan-reviewer.mdに「実行情報」セクションが存在しません"

    # TC08: Claude Code直接実行時のモデル表示（review.md）
    def test_review_md_has_model_field(self, review_md: str):
        """review.mdに「使用モデル」フィールドが存在することを確認"""
        assert (
            "- **使用モデル**:" in review_md
        ), "review.mdに「使用モデル」フィールドが存在しません"

    # TC08: Claude Code直接実行時のモデル表示（tdd-cycle）
    def test_tdd_cycle_has_model_field(self, tdd_cycle_skill: str):
        """tdd-cycle/SKILL.mdに「使用モデル」フィールドが存在することを確認"""
        assert (
            "- **使用モデル**:" in tdd_cycle_skill
        ), "tdd-cycle/SKILL.mdに「使用モデル」フィールドが存在しません"

    # TC08: Claude Code直接実行時のモデル表示（plan-reviewer）
    def test_plan_reviewer_has_model_field(self, plan_reviewer: str):
        """plan-reviewer.mdに「使用モデル」フィールドが存在することを確認"""
        assert (
            "- **使用モデル**:" in plan_reviewer
        ), "plan-reviewer.mdに「使用モデル」フィールドが存在しません"

    # TC09: 実行日時フィールドの存在（review.md）
    def test_review_md_has_datetime_field(self, review_md: str):
        """review.mdに「実行日時」フィールドが存在することを確認"""
        assert (
            "- **実行日時**:" in review_md
        ), "review.mdに「実行日時」フィールドが存在しません"

    # TC09: 実行日時フィールドの存在（tdd-cycle）
    def test_tdd_cycle_has_datetime_field(self, tdd_cycle_skill: str):
        """tdd-cycle/SKILL.mdに「実行日時」フィールドが存在することを確認"""
        assert (
            "- **実行日時**:" in tdd_cycle_skill
        ), "tdd-cycle/SKILL.mdに「実行日時」フィールドが存在しません"

    # TC09: 実行日時フィールドの存在（plan-reviewer）
    def test_plan_reviewer_has_datetime_field(self, plan_reviewer: str):
        """plan-reviewer.mdに「実行日時」フィールドが存在することを確認"""
        assert (
            "- **実行日時**:" in plan_reviewer
        ), "plan-reviewer.mdに「実行日時」フィールドが存在しません"

    # TC06: Markdown構文の整合性（見出しレベル）
    def test_execution_info_section_heading_level(self, review_md: str):
        """「実行情報」セクションの見出しレベルが正しいことを確認（###）"""
        # 「実行情報」セクションの見出しレベルを確認
        pattern = r"^### 実行情報$"
        assert re.search(
            pattern, review_md, re.MULTILINE
        ), "review.mdの「実行情報」見出しレベルが正しくありません（### が必要）"

    # TC10: 全レビュータスクで構造が統一（フィールド順序）
    def test_execution_info_fields_order_consistency(
        self, review_md: str, tdd_cycle_skill: str, plan_reviewer: str
    ):
        """全ファイルで「実行情報」セクションのフィールド順序が統一されていることを確認"""
        # 期待されるフィールド順序
        expected_order = ["実行者", "使用モデル", "実行日時"]

        for file_content, file_name in [
            (review_md, "review.md"),
            (tdd_cycle_skill, "tdd-cycle/SKILL.md"),
            (plan_reviewer, "plan-reviewer.md"),
        ]:
            # 「実行情報」セクションを抽出
            match = re.search(
                r"### 実行情報\n((?:- \*\*.*?\*\*:.*?\n)+)",
                file_content,
                re.MULTILINE,
            )
            assert match, f"{file_name}に「実行情報」セクションが見つかりません"

            section_content = match.group(1)

            # フィールドの順序を確認
            fields = re.findall(r"- \*\*(.*?)\*\*:", section_content)
            assert (
                fields == expected_order
            ), f"{file_name}のフィールド順序が期待と異なります。期待: {expected_order}, 実際: {fields}"

    # TC04: 実行日時取得のクロスプラットフォーム対応（フォールバック）
    def test_datetime_fallback_syntax_in_review_md(self, review_md: str):
        """review.mdに日時取得のフォールバック構文が含まれることを確認"""
        # date コマンドまたは powershell の Get-Date を使用している
        has_date_command = "date" in review_md.lower()
        has_powershell = "powershell" in review_md.lower() or "get-date" in review_md.lower()

        # どちらかが存在すればOK（実装パターンによる）
        assert (
            has_date_command or has_powershell
        ), "review.mdに日時取得処理が見つかりません"

    # TC07: 既存テンプレート構造との整合性（「実行情報」が「レビュー結果」の前）
    def test_execution_info_before_review_result(self, review_md: str):
        """review.mdで「実行情報」セクションが「レビュー結果」の前に配置されていることを確認"""
        # 「実行情報」と「レビュー結果」の位置を取得
        exec_info_pos = review_md.find("### 実行情報")
        review_result_pos = review_md.find("### レビュー結果")

        assert exec_info_pos != -1, "「実行情報」セクションが見つかりません"
        assert review_result_pos != -1, "「レビュー結果」セクションが見つかりません"
        assert (
            exec_info_pos < review_result_pos
        ), "「実行情報」は「レビュー結果」の前に配置する必要があります"
