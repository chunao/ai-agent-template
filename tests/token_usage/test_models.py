"""Tests for token usage data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from src.token_usage.models import (
    SessionStartEvent,
    SkillStartEvent,
    ToolCallEvent,
    ExternalDelegationEvent,
)


class TestSessionStartEvent:
    """SessionStartEventのテスト."""

    def test_valid_event(self):
        """正常系: 有効なイベントを作成できること."""
        event = SessionStartEvent(
            session_id="sess_20260130_143022_123456",
            issue="94",
            worktree="/worktrees/issue-94"
        )

        assert event.event == "session_start"
        assert event.session_id == "sess_20260130_143022_123456"
        assert event.issue == "94"
        assert isinstance(event.timestamp, str)

    def test_minimal_event(self):
        """正常系: 最小限の必須フィールドで作成できること."""
        event = SessionStartEvent(session_id="sess_test")

        assert event.session_id == "sess_test"
        assert event.issue is None
        assert event.worktree is None

    def test_invalid_session_id(self):
        """異常系: 空のセッションIDはエラー."""
        with pytest.raises(ValidationError):
            SessionStartEvent(session_id="")


class TestSkillStartEvent:
    """SkillStartEventのテスト."""

    def test_valid_event(self):
        """正常系: 有効なイベントを作成できること."""
        event = SkillStartEvent(
            skill="tdd-cycle",
            issue="94"
        )

        assert event.event == "skill_start"
        assert event.skill == "tdd-cycle"
        assert event.issue == "94"

    def test_minimal_event(self):
        """正常系: issue無しでも作成できること."""
        event = SkillStartEvent(skill="tdd-cycle")

        assert event.skill == "tdd-cycle"
        assert event.issue is None

    def test_invalid_skill_name(self):
        """異常系: 空のスキル名はエラー."""
        with pytest.raises(ValidationError):
            SkillStartEvent(skill="")


class TestToolCallEvent:
    """ToolCallEventのテスト."""

    def test_valid_event(self):
        """正常系: 有効なイベントを作成できること."""
        event = ToolCallEvent(
            tool="Read",
            params={"file_path": "test.py"},
            input_tokens=1234,
            output_tokens=567,
            model="sonnet-4.5",
            cumulative_input=1234,
            cumulative_output=567,
            context={"skill": "tdd-cycle", "phase": "RED"}
        )

        assert event.event == "tool_call"
        assert event.tool == "Read"
        assert event.input_tokens == 1234
        assert event.output_tokens == 567

    def test_zero_tokens(self):
        """境界値: トークン数0も許容."""
        event = ToolCallEvent(
            tool="Read",
            params={},
            input_tokens=0,
            output_tokens=0,
            model="sonnet-4.5",
            cumulative_input=0,
            cumulative_output=0
        )

        assert event.input_tokens == 0
        assert event.output_tokens == 0

    def test_negative_tokens(self):
        """異常系: 負のトークン数はエラー."""
        with pytest.raises(ValidationError):
            ToolCallEvent(
                tool="Read",
                params={},
                input_tokens=-1,
                output_tokens=0,
                model="sonnet-4.5",
                cumulative_input=0,
                cumulative_output=0
            )


class TestExternalDelegationEvent:
    """ExternalDelegationEventのテスト."""

    def test_valid_event(self):
        """正常系: 有効なイベントを作成できること."""
        event = ExternalDelegationEvent(
            delegate_to="codex-cli",
            task="code-review",
            estimated_tokens_saved=3000
        )

        assert event.event == "external_delegation"
        assert event.delegate_to == "codex-cli"
        assert event.estimated_tokens_saved == 3000

    def test_zero_tokens_saved(self):
        """境界値: 節約トークン数0も許容."""
        event = ExternalDelegationEvent(
            delegate_to="codex-cli",
            task="test",
            estimated_tokens_saved=0
        )

        assert event.estimated_tokens_saved == 0

    def test_negative_tokens_saved(self):
        """異常系: 負の節約トークン数はエラー."""
        with pytest.raises(ValidationError):
            ExternalDelegationEvent(
                delegate_to="codex-cli",
                task="test",
                estimated_tokens_saved=-100
            )
