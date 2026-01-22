"""GitHub Actions ワークフロー設定のテスト

Issue #11: PR作成前のテスト実行を確実にする仕組みを導入する
Issue #26: pathsフィルターでスキップ時にステータスが報告されない問題を修正
"""

from pathlib import Path

import pytest
import yaml


class TestGitHubActionsWorkflow:
    """GitHub Actions test.yml ワークフローのテスト"""

    @pytest.fixture
    def workflow_path(self) -> Path:
        """ワークフローファイルのパスを返す"""
        return Path(__file__).parent.parent / ".github" / "workflows" / "test.yml"

    @pytest.fixture
    def workflow_config(self, workflow_path: Path) -> dict:
        """ワークフロー設定を読み込む"""
        if not workflow_path.exists():
            pytest.skip(f"Workflow file not found: {workflow_path}")
        with open(workflow_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_workflow_file_exists(self, workflow_path: Path):
        """ワークフローファイルが存在すること"""
        assert workflow_path.exists(), f"Workflow file should exist at {workflow_path}"

    def test_workflow_has_name(self, workflow_config: dict):
        """ワークフローに名前が設定されていること"""
        assert "name" in workflow_config, "Workflow should have a name"

    def _get_triggers(self, workflow_config: dict) -> dict:
        """トリガー設定を取得する（YAMLの'on'はPythonでTrueになる）"""
        return workflow_config.get("on") or workflow_config.get(True, {})

    def test_workflow_triggers_on_pull_request(self, workflow_config: dict):
        """PRイベントでトリガーされること"""
        triggers = self._get_triggers(workflow_config)
        assert triggers, "Workflow should have triggers"
        assert "pull_request" in triggers, "Workflow should trigger on pull_request"

    def test_workflow_targets_main_branch(self, workflow_config: dict):
        """mainブランチへのPRがターゲットであること"""
        triggers = self._get_triggers(workflow_config)
        pr_config = triggers.get("pull_request", {})
        branches = pr_config.get("branches", [])
        assert "main" in branches, "Workflow should target main branch"

    def test_workflow_has_check_changes_job(self, workflow_config: dict):
        """check-changesジョブが存在すること（Issue #26: dorny/paths-filter方式）"""
        jobs = workflow_config.get("jobs", {})
        assert "check-changes" in jobs, "Workflow should have 'check-changes' job"

    def test_check_changes_job_uses_paths_filter(self, workflow_config: dict):
        """check-changesジョブがdorny/paths-filterを使用すること"""
        check_changes_job = workflow_config.get("jobs", {}).get("check-changes", {})
        steps = check_changes_job.get("steps", [])
        uses_paths_filter = any(
            "dorny/paths-filter" in step.get("uses", "") for step in steps
        )
        assert uses_paths_filter, "check-changes job should use dorny/paths-filter"

    def test_check_changes_job_detects_python_files(self, workflow_config: dict):
        """check-changesジョブがPythonファイルを検出対象にしていること"""
        check_changes_job = workflow_config.get("jobs", {}).get("check-changes", {})
        steps = check_changes_job.get("steps", [])
        for step in steps:
            if "dorny/paths-filter" in step.get("uses", ""):
                filters_config = step.get("with", {}).get("filters", "")
                assert "*.py" in filters_config, "Paths filter should detect Python files"
                return
        pytest.fail("dorny/paths-filter step not found")

    def test_workflow_has_skip_test_job(self, workflow_config: dict):
        """skip-testジョブが存在すること（Issue #26: テスト不要時用）"""
        jobs = workflow_config.get("jobs", {})
        assert "skip-test" in jobs, "Workflow should have 'skip-test' job"

    def test_test_job_depends_on_check_changes(self, workflow_config: dict):
        """testジョブがcheck-changesに依存すること"""
        test_job = workflow_config.get("jobs", {}).get("test", {})
        needs = test_job.get("needs", [])
        if isinstance(needs, str):
            needs = [needs]
        assert "check-changes" in needs, "test job should depend on check-changes"

    def test_skip_test_job_depends_on_check_changes(self, workflow_config: dict):
        """skip-testジョブがcheck-changesに依存すること"""
        skip_test_job = workflow_config.get("jobs", {}).get("skip-test", {})
        needs = skip_test_job.get("needs", [])
        if isinstance(needs, str):
            needs = [needs]
        assert "check-changes" in needs, "skip-test job should depend on check-changes"

    def test_workflow_has_jobs(self, workflow_config: dict):
        """ジョブが定義されていること"""
        assert "jobs" in workflow_config, "Workflow should have jobs"
        assert len(workflow_config["jobs"]) > 0, "Workflow should have at least one job"

    def test_workflow_has_test_job(self, workflow_config: dict):
        """testジョブが存在すること"""
        jobs = workflow_config.get("jobs", {})
        assert "test" in jobs, "Workflow should have a 'test' job"

    def test_test_job_runs_on_ubuntu(self, workflow_config: dict):
        """testジョブがubuntuで実行されること"""
        test_job = workflow_config.get("jobs", {}).get("test", {})
        runs_on = test_job.get("runs-on", "")
        assert "ubuntu" in runs_on, "Test job should run on Ubuntu"

    def test_test_job_has_steps(self, workflow_config: dict):
        """testジョブにステップがあること"""
        test_job = workflow_config.get("jobs", {}).get("test", {})
        steps = test_job.get("steps", [])
        assert len(steps) > 0, "Test job should have steps"

    def test_test_job_uses_uv(self, workflow_config: dict):
        """testジョブがuvを使用すること"""
        test_job = workflow_config.get("jobs", {}).get("test", {})
        steps = test_job.get("steps", [])
        step_names = [s.get("name", "") for s in steps]
        step_uses = [s.get("uses", "") for s in steps]

        has_uv = any("uv" in name.lower() for name in step_names) or \
                 any("uv" in uses.lower() for uses in step_uses)
        assert has_uv, "Test job should use uv for dependency management"

    def test_test_job_runs_pytest(self, workflow_config: dict):
        """testジョブがpytestを実行すること"""
        test_job = workflow_config.get("jobs", {}).get("test", {})
        steps = test_job.get("steps", [])

        has_pytest = False
        for step in steps:
            run_cmd = step.get("run", "")
            if "pytest" in run_cmd:
                has_pytest = True
                break

        assert has_pytest, "Test job should run pytest"
