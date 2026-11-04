from __future__ import annotations

from types import SimpleNamespace

import pytest

from agent import (
    ActionProposal,
    AgentResult,
    AgentState,
    RunBudget,
    RunStatus,
    StopReason,
    action_fingerprint,
    resume_after_approval,
    search_activities,
    validate_arguments,
    TOOLS,
)


def test_action_fingerprint_is_stable_for_argument_order():
    left = action_fingerprint("tool", {"a": 1, "b": 2})
    right = action_fingerprint("tool", {"b": 2, "a": 1})
    assert left == right


def test_search_activities_is_deterministic():
    result = search_activities("Melbourne", family_friendly=True)
    assert result["city"] == "Melbourne"
    assert len(result["activities"]) == 3


def test_validate_arguments_rejects_unknown_keys():
    with pytest.raises(ValueError, match="Unexpected"):
        validate_arguments(
            TOOLS["search_activities"],
            {"city": "Melbourne", "family_friendly": True, "extra": 1},
        )


def test_resume_rejects_changed_approval_fingerprint():
    proposal = ActionProposal(
        call_id="call-1",
        tool="reserve_activity",
        arguments={"activity_id": "river-cruise", "party_size": 2},
        fingerprint="not-the-real-fingerprint",
    )
    waiting = AgentResult(
        status=RunStatus.WAITING_FOR_APPROVAL,
        stop_reason=StopReason.WAITING_FOR_APPROVAL,
        state=AgentState(goal="demo"),
        approval=proposal,
    )
    with pytest.raises(PermissionError, match="changed"):
        resume_after_approval(waiting, approved=True)


def test_budget_defaults_are_bounded():
    budget = RunBudget()
    assert budget.max_steps > 0
    assert budget.max_tool_calls > 0
    assert budget.retry_attempts > 0
