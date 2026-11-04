from __future__ import annotations

import json
import os
from typing import Any, Literal, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from openai import OpenAI

load_dotenv()


class GraphState(TypedDict):
    goal: str
    input_items: list[Any]
    observations: list[dict[str, Any]]
    pending_call: dict[str, Any] | None
    answer: str | None
    steps: int
    tool_calls: int
    status: str


ACTIVITIES = [
    {
        "id": "botanic-gardens",
        "name": "Royal Botanic Gardens walk",
        "family_friendly": True,
        "reservation_required": False,
    },
    {
        "id": "river-cruise",
        "name": "Yarra River sightseeing cruise",
        "family_friendly": True,
        "reservation_required": True,
    },
    {
        "id": "museum",
        "name": "Melbourne Museum visit",
        "family_friendly": True,
        "reservation_required": False,
    },
]


def search_activities(city: str, family_friendly: bool) -> dict[str, Any]:
    if city.strip().lower() != "melbourne":
        return {"city": city, "activities": []}

    matches = [
        item for item in ACTIVITIES
        if not family_friendly or item["family_friendly"]
    ]
    return {"city": "Melbourne", "activities": matches}


TOOLS = [
    {
        "type": "function",
        "name": "search_activities",
        "description": "List demo activities available in Melbourne.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "family_friendly": {"type": "boolean"},
            },
            "required": ["city", "family_friendly"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]


def initial_state(goal: str) -> GraphState:
    return {
        "goal": goal,
        "input_items": [{"role": "user", "content": goal}],
        "observations": [],
        "pending_call": None,
        "answer": None,
        "steps": 0,
        "tool_calls": 0,
        "status": "running",
    }


def make_model_node(client: OpenAI, model: str, *, max_steps: int = 5):
    def model_node(state: GraphState) -> dict[str, Any]:
        if state["steps"] >= max_steps:
            return {
                "status": "stopped_step_budget",
                "pending_call": None,
            }

        response = client.responses.create(
            model=model,
            instructions=(
                "You are a concise travel assistant. "
                "Use search_activities when useful. "
                "Do not invent activity data. "
                "Return a final answer when you have enough information."
            ),
            tools=TOOLS,
            parallel_tool_calls=False,
            input=state["input_items"],
        )

        new_items = list(state["input_items"])
        new_items.extend(response.output)

        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            return {
                "input_items": new_items,
                "pending_call": None,
                "answer": response.output_text,
                "steps": state["steps"] + 1,
                "status": "completed",
            }

        if len(calls) != 1:
            raise RuntimeError("Lesson 11 supports one tool call per graph step")

        call = calls[0]
        return {
            "input_items": new_items,
            "pending_call": {
                "call_id": call.call_id,
                "name": call.name,
                "arguments": call.arguments,
            },
            "steps": state["steps"] + 1,
        }

    return model_node


def tool_node(state: GraphState) -> dict[str, Any]:
    call = state["pending_call"]
    if call is None:
        raise RuntimeError("tool_node called without a pending tool call")

    if call["name"] != "search_activities":
        observation = {
            "ok": False,
            "error": f"Unsupported tool: {call['name']}",
        }
    else:
        arguments = json.loads(call["arguments"])
        if set(arguments) != {"city", "family_friendly"}:
            observation = {
                "ok": False,
                "error": "Unexpected tool arguments",
            }
        else:
            observation = {
                "ok": True,
                "data": search_activities(
                    city=arguments["city"],
                    family_friendly=arguments["family_friendly"],
                ),
            }

    new_items = list(state["input_items"])
    new_items.append({
        "type": "function_call_output",
        "call_id": call["call_id"],
        "output": json.dumps(observation),
    })

    observations = list(state["observations"])
    observations.append({
        "tool": call["name"],
        "observation": observation,
    })

    return {
        "input_items": new_items,
        "observations": observations,
        "pending_call": None,
        "tool_calls": state["tool_calls"] + 1,
    }


def route_after_model(state: GraphState) -> Literal["tool", "end"]:
    if state["status"] != "running":
        return "end"
    if state["pending_call"] is not None:
        return "tool"
    return "end"


def build_graph(
    *,
    client: OpenAI | None = None,
    model: str | None = None,
    max_steps: int = 5,
):
    client = client or OpenAI()
    model = model or os.getenv("OPENAI_MODEL", "gpt-5.6")

    builder = StateGraph(GraphState)
    builder.add_node("model", make_model_node(client, model, max_steps=max_steps))
    builder.add_node("tool", tool_node)

    builder.add_edge(START, "model")
    builder.add_conditional_edges(
        "model",
        route_after_model,
        {
            "tool": "tool",
            "end": END,
        },
    )
    builder.add_edge("tool", "model")

    return builder.compile()
