"""worktree-workflow ルールと関連コマンドの整合性テスト

Issue #46: 1 Issue 1 Worktree ワークフローを徹底する
"""

from pathlib import Path

import pytest


class TestWorktreeWorkflowRule:
    """1 Issue 1 Worktree ルールファイルのテスト"""

    @pytest.fixture
    def rule_path(self) -> Path:
        """ルールファイルのパスを返す"""
        return Path(__file__).parent.parent / ".claude" / "rules" / "worktree-workflow.md"

    @pytest.fixture
    def rule_content(self, rule_path: Path) -> str:
        """ルールファイルの内容を読み込む"""
        if not rule_path.exists():
            pytest.skip(f"Rule file not found: {rule_path}")
        return rule_path.read_text(encoding="utf-8")

    def test_rule_file_exists(self, rule_path: Path):
        """ルールファイルが存在すること"""
        assert rule_path.exists(), f"Rule file should exist at {rule_path}"

    def test_rule_has_title(self, rule_content: str):
        """ルールファイルにタイトルがあること"""
        assert "# " in rule_content, "Rule file should have a title"

    def test_rule_defines_one_issue_one_worktree_principle(self, rule_content: str):
        """1 Issue 1 Worktree の原則が定義されていること"""
        principle_keywords = ["1 Issue", "1 Worktree"]
        has_principle = all(
            keyword in rule_content for keyword in principle_keywords
        )
        assert has_principle, "Rule should define the 1 Issue 1 Worktree principle"

    def test_rule_defines_standard_flow(self, rule_content: str):
        """標準フローが定義されていること（worktree-start → start-issue の順序）"""
        assert "/worktree-start" in rule_content, "Rule should mention /worktree-start"
        assert "/start-issue" in rule_content, "Rule should mention /start-issue"

        # worktree-start が start-issue より前に言及されている（フロー順序）
        worktree_start_pos = rule_content.find("/worktree-start")
        start_issue_pos = rule_content.find("/start-issue")
        assert worktree_start_pos < start_issue_pos, (
            "Standard flow should show /worktree-start before /start-issue"
        )

    def test_rule_defines_exception_cases(self, rule_content: str):
        """例外ケース（Worktreeを使わない場合）が定義されていること"""
        exception_keywords = ["例外", "使わない", "不要", "スキップ"]
        has_exception = any(
            keyword in rule_content for keyword in exception_keywords
        )
        assert has_exception, "Rule should define exception cases for when worktree is not needed"

    def test_rule_covers_full_workflow(self, rule_content: str):
        """ルールが完全なワークフロー（tdd, review, pr-create, pr-merge）をカバーすること"""
        required_commands = ["/tdd", "/review", "/pr-create", "/pr-merge"]
        for cmd in required_commands:
            assert cmd in rule_content, f"Rule should mention {cmd} in the workflow"


class TestStartIssueWorktreeGuidance:
    """/start-issue コマンドのWorktree推奨ガイダンスのテスト"""

    @pytest.fixture
    def command_path(self) -> Path:
        """コマンドファイルのパスを返す"""
        return Path(__file__).parent.parent / ".claude" / "commands" / "start-issue.md"

    @pytest.fixture
    def command_content(self, command_path: Path) -> str:
        """コマンドファイルの内容を読み込む"""
        if not command_path.exists():
            pytest.skip(f"Command file not found: {command_path}")
        return command_path.read_text(encoding="utf-8")

    def test_has_worktree_guidance_before_branch_creation(self, command_content: str):
        """ブランチ作成ステップの前にWorktree推奨ガイダンスがあること"""
        # Worktree推奨ガイダンスの存在確認
        worktree_keywords = ["Worktree", "worktree"]
        has_worktree_mention = any(
            keyword in command_content for keyword in worktree_keywords
        )
        assert has_worktree_mention, "Command should mention Worktree"

        # 「推奨」の文言があること
        recommend_keywords = ["推奨", "おすすめ", "recommended"]
        has_recommendation = any(
            keyword in command_content for keyword in recommend_keywords
        )
        assert has_recommendation, "Command should recommend using Worktree"

        # Worktreeガイダンスがブランチ作成の前にあること
        # ブランチ作成は「### 3. ブランチの作成」で始まる
        branch_creation_markers = ["ブランチの作成", "git checkout -b"]
        first_branch_marker = min(
            (command_content.find(m) for m in branch_creation_markers if command_content.find(m) >= 0),
            default=-1,
        )

        # Worktree推奨の位置を確認
        worktree_recommend_pos = -1
        for keyword in ["Worktree推奨", "Worktree使用", "worktree-start"]:
            pos = command_content.find(keyword)
            if pos >= 0 and (worktree_recommend_pos < 0 or pos < worktree_recommend_pos):
                worktree_recommend_pos = pos

        assert worktree_recommend_pos >= 0, "Command should have Worktree guidance"
        assert first_branch_marker >= 0, "Command should have branch creation section"
        assert worktree_recommend_pos < first_branch_marker, (
            "Worktree guidance should appear before branch creation step"
        )

    def test_no_duplicate_parallel_work_section(self, command_content: str):
        """末尾の「並列作業について」セクションが統合されていること（重複がないこと）"""
        # 「並列作業について」が独立セクションとして残っていないこと
        parallel_section_count = command_content.count("## 並列作業について")
        assert parallel_section_count == 0, (
            "The '並列作業について' section should be integrated into the Worktree guidance, "
            "not remain as a separate section"
        )

    def test_non_worktree_flow_preserved(self, command_content: str):
        """通常フロー（非Worktree）が維持されていること"""
        # ブランチ作成のステップが残っていること
        assert "git checkout -b" in command_content, (
            "Non-worktree flow (branch creation) should be preserved"
        )


class TestWorktreeStartCommandIntegration:
    """/worktree-start コマンドのstart-issue連携テスト"""

    @pytest.fixture
    def command_path(self) -> Path:
        """コマンドファイルのパスを返す"""
        return Path(__file__).parent.parent / ".claude" / "commands" / "worktree-start.md"

    @pytest.fixture
    def command_content(self, command_path: Path) -> str:
        """コマンドファイルの内容を読み込む"""
        if not command_path.exists():
            pytest.skip(f"Command file not found: {command_path}")
        return command_path.read_text(encoding="utf-8")

    def test_has_responsibility_description(self, command_content: str):
        """コマンドの責務（環境準備）が明記されていること"""
        responsibility_keywords = ["環境準備", "作業ディレクトリ", "分離"]
        has_responsibility = any(
            keyword in command_content for keyword in responsibility_keywords
        )
        assert has_responsibility, "Command should describe its responsibility (environment preparation)"

    def test_references_start_issue_as_next_step(self, command_content: str):
        """/start-issue が次のステップとして案内されていること"""
        assert "/start-issue" in command_content, (
            "Command should reference /start-issue as the next step"
        )

    def test_clarifies_planning_is_start_issue_responsibility(self, command_content: str):
        """計画立案は /start-issue の責務であることが明記されていること"""
        planning_delegation_keywords = [
            "計画",
            "実装計画",
            "/start-issue",
        ]
        # 計画立案と/start-issueの関連が記載されていること
        has_planning = any(
            keyword in command_content for keyword in planning_delegation_keywords[:2]
        )
        has_start_issue = "/start-issue" in command_content
        assert has_planning and has_start_issue, (
            "Command should clarify that planning is /start-issue's responsibility"
        )


class TestWorkflowConsistency:
    """ワークフロー全体の整合性テスト"""

    @pytest.fixture
    def commands_dir(self) -> Path:
        """コマンドディレクトリのパスを返す"""
        return Path(__file__).parent.parent / ".claude" / "commands"

    @pytest.fixture
    def rules_dir(self) -> Path:
        """ルールディレクトリのパスを返す"""
        return Path(__file__).parent.parent / ".claude" / "rules"

    def _read_file(self, path: Path) -> str:
        """ファイルを読み込む（存在しない場合はskip）"""
        if not path.exists():
            pytest.skip(f"File not found: {path}")
        return path.read_text(encoding="utf-8")

    def test_pr_merge_handles_worktree(self, commands_dir: Path):
        """pr-merge がWorktree削除を処理すること"""
        content = self._read_file(commands_dir / "pr-merge.md")
        assert "worktree" in content.lower(), (
            "/pr-merge should handle worktree cleanup"
        )

    def test_pr_create_works_from_worktree(self, commands_dir: Path):
        """pr-create がWorktree環境から動作可能であること"""
        content = self._read_file(commands_dir / "pr-create.md")
        # pr-create はブランチからpushするため、worktree環境でも動作する
        assert "git push" in content, (
            "/pr-create should support pushing from any branch (including worktree)"
        )

    def test_no_circular_reference_between_commands(self, commands_dir: Path):
        """start-issue と worktree-start の間に循環参照がないこと"""
        start_issue = self._read_file(commands_dir / "start-issue.md")
        worktree_start = self._read_file(commands_dir / "worktree-start.md")

        # start-issue が worktree-start を「実行せよ」と指示していないこと
        # （推奨案内は OK、実行指示は循環参照になる）
        circular_patterns = [
            "/worktree-start` で実装",
            "/worktree-start` を実行",
            "worktree-startを実行",
        ]
        has_circular = any(
            pattern in start_issue for pattern in circular_patterns
        )
        assert not has_circular, (
            "/start-issue should not instruct to execute /worktree-start "
            "(recommend is OK, but execute instruction creates circular reference)"
        )

    def test_worktree_workflow_rule_referenced_in_start_issue(
        self, commands_dir: Path, rules_dir: Path
    ):
        """start-issue がworktree-workflowルールの方針に従っていること"""
        rule_path = rules_dir / "worktree-workflow.md"
        if not rule_path.exists():
            pytest.skip("worktree-workflow.md not yet created")

        start_issue = self._read_file(commands_dir / "start-issue.md")

        # start-issue が Worktree を推奨していること（ルールの方針に従う）
        worktree_keywords = ["Worktree", "worktree"]
        has_worktree = any(k in start_issue for k in worktree_keywords)
        assert has_worktree, (
            "/start-issue should follow worktree-workflow rule by mentioning Worktree"
        )
