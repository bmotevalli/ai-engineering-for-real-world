from framework_agent import (
    initial_state,
    route_after_model,
    search_activities,
    tool_node,
)


def test_router_sends_pending_call_to_tool():
    state = initial_state("demo")
    state["pending_call"] = {
        "call_id": "call-1",
        "name": "search_activities",
        "arguments": '{"city":"Melbourne","family_friendly":true}',
    }
    assert route_after_model(state) == "tool"


def test_router_ends_when_completed():
    state = initial_state("demo")
    state["status"] = "completed"
    assert route_after_model(state) == "end"


def test_search_activities_is_deterministic():
    result = search_activities("Melbourne", True)
    assert result["city"] == "Melbourne"
    assert len(result["activities"]) == 3


def test_tool_node_appends_observation():
    state = initial_state("demo")
    state["pending_call"] = {
        "call_id": "call-1",
        "name": "search_activities",
        "arguments": '{"city":"Melbourne","family_friendly":true}',
    }

    update = tool_node(state)

    assert update["tool_calls"] == 1
    assert update["pending_call"] is None
    assert update["observations"][0]["tool"] == "search_activities"
