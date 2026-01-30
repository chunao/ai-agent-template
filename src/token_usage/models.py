"""Data models for token usage events."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


def _now_iso() -> str:
    """現在時刻をISO形式で取得."""
    return datetime.now(timezone.utc).isoformat()


class BaseEvent(BaseModel):
    """イベントの基底クラス."""

    timestamp: str = Field(default_factory=_now_iso)
    event: str


class SessionStartEvent(BaseEvent):
    """セッション開始イベント."""

    event: str = "session_start"
    session_id: str = Field(min_length=1)
    issue: Optional[str] = None
    worktree: Optional[str] = None


class SkillStartEvent(BaseEvent):
    """スキル開始イベント."""

    event: str = "skill_start"
    skill: str = Field(min_length=1)
    issue: Optional[str] = None


class ToolCallEvent(BaseEvent):
    """ツール呼び出しイベント."""

    event: str = "tool_call"
    tool: str
    params: Dict[str, Any]
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    model: str
    cumulative_input: int = Field(ge=0)
    cumulative_output: int = Field(ge=0)
    context: Optional[Dict[str, Any]] = None


class ExternalDelegationEvent(BaseEvent):
    """外部AI委任イベント."""

    event: str = "external_delegation"
    delegate_to: str
    task: str
    estimated_tokens_saved: int = Field(ge=0)
