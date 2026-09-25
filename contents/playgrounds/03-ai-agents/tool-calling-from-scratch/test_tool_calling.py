"""Offline tests for the deterministic host-side tool boundary."""

import unittest
from types import SimpleNamespace

from tool_calling import ToolInputError, answer_once, execute_tool_call, parse_arguments


class FakeResponses:
    def __init__(self, *responses: SimpleNamespace) -> None:
        self.pending = list(responses)
        self.requests: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> SimpleNamespace:
        self.requests.append(kwargs)
        return self.pending.pop(0)


class FakeClient:
    def __init__(self, *responses: SimpleNamespace) -> None:
        self.responses = FakeResponses(*responses)


class ParseArgumentsTests(unittest.TestCase):
    def test_parses_object(self) -> None:
        self.assertEqual(parse_arguments('{"service":"checkout"}'), {"service": "checkout"})

    def test_rejects_invalid_json(self) -> None:
        with self.assertRaisesRegex(ToolInputError, "not valid JSON"):
            parse_arguments("not-json")

    def test_rejects_non_object_json(self) -> None:
        with self.assertRaisesRegex(ToolInputError, "JSON object"):
            parse_arguments('["checkout"]')


class ExecuteToolCallTests(unittest.TestCase):
    def test_dispatches_allowlisted_tool(self) -> None:
        result = execute_tool_call(
            "lookup_service_health",
            '{"service":"checkout","environment":"production"}',
        )
        self.assertEqual(result["status"], "degraded")
        self.assertEqual(result["active_incident"], "INC-2041")

    def test_rejects_unknown_tool(self) -> None:
        with self.assertRaisesRegex(ToolInputError, "Unknown tool"):
            execute_tool_call("run_shell", "{}")

    def test_rejects_extra_arguments(self) -> None:
        with self.assertRaisesRegex(ToolInputError, "requires exactly"):
            execute_tool_call(
                "lookup_service_health",
                '{"service":"checkout","environment":"production","force":true}',
            )

    def test_rejects_value_outside_allowlist(self) -> None:
        with self.assertRaisesRegex(ToolInputError, "service must be"):
            execute_tool_call(
                "lookup_service_health",
                '{"service":"payments","environment":"production"}',
            )


class AnswerOnceTests(unittest.TestCase):
    def test_returns_direct_answer_when_no_tool_is_requested(self) -> None:
        client = FakeClient(SimpleNamespace(output=[], output_text="Direct answer"))

        answer = answer_once(client, "test-model", "What is a readiness probe?")

        self.assertEqual(answer, "Direct answer")
        self.assertEqual(len(client.responses.requests), 1)

    def test_correlates_tool_output_with_call_id(self) -> None:
        call = SimpleNamespace(
            type="function_call",
            name="lookup_service_health",
            arguments='{"service":"checkout","environment":"production"}',
            call_id="call-123",
        )
        client = FakeClient(
            SimpleNamespace(output=[call], output_text=""),
            SimpleNamespace(output=[], output_text="Checkout is degraded."),
        )

        answer = answer_once(client, "test-model", "Is checkout healthy?")

        self.assertEqual(answer, "Checkout is degraded.")
        final_input = client.responses.requests[1]["input"]
        self.assertEqual(final_input[-1]["type"], "function_call_output")
        self.assertEqual(final_input[-1]["call_id"], "call-123")
        self.assertIn('"status": "degraded"', final_input[-1]["output"])

    def test_rejects_a_second_tool_use_turn(self) -> None:
        call = SimpleNamespace(
            type="function_call",
            name="lookup_service_health",
            arguments='{"service":"catalog","environment":"production"}',
            call_id="call-1",
        )
        repeated_call = SimpleNamespace(type="function_call")
        client = FakeClient(
            SimpleNamespace(output=[call], output_text=""),
            SimpleNamespace(output=[repeated_call], output_text=""),
        )

        with self.assertRaisesRegex(RuntimeError, "permits one tool-use turn"):
            answer_once(client, "test-model", "Inspect catalog")


if __name__ == "__main__":
    unittest.main()
