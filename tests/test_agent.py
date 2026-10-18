from app import agent


def fake_decision(tool_name):
    return {
        "selected_tool": tool_name,
        "probabilities": {tool_name: 1.0},
        "confidence": 1.0,
        "decider_calls": 1,
        "latency_ms": 10,
    }


def test_troubleshoot_runs_selected_diagnostic(monkeypatch):
    monkeypatch.setattr(
        agent,
        "select_diagnostic_tool",
        lambda problem: fake_decision("container_logs"),
    )

    result = agent.troubleshoot(
        problem="demo-app is in CrashLoopBackOff",
        explain=False,
    )

    assert result["diagnostic_tool"] == "container_logs"
    assert "DATABASE_URL is missing" in result["diagnostic_evidence"]
    assert result["explanation"] is None


def test_troubleshoot_rejects_unknown_tool(monkeypatch):
    monkeypatch.setattr(
        agent,
        "select_diagnostic_tool",
        lambda problem: fake_decision("delete_pod"),
    )

    try:
        agent.troubleshoot(
            problem="demo-app is failing",
            explain=False,
        )
    except ValueError as exc:
        assert "unsupported diagnostic tool" in str(exc)
    else:
        raise AssertionError("Expected an unsupported-tool error")


def test_troubleshoot_calls_explainer_when_enabled(monkeypatch):
    monkeypatch.setattr(
        agent,
        "select_diagnostic_tool",
        lambda problem: fake_decision("pod_status"),
    )

    monkeypatch.setattr(
        agent,
        "generate_explanation",
        lambda problem, diagnostic_evidence: {
            "explanation": "Investigate the container's startup configuration."
        },
    )

    result = agent.troubleshoot(
        problem="demo-app is in CrashLoopBackOff",
        explain=True,
    )

    assert result["diagnostic_tool"] == "pod_status"
    assert "CrashLoopBackOff" in result["diagnostic_evidence"]
    assert "explanation" in result["explanation"]
def test_troubleshoot_rejects_empty_problem():
    try:
        agent.troubleshoot(problem="", explain=False)
    except ValueError as exc:
        assert "must not be empty" in str(exc)
    else:
        raise AssertionError("Expected an error for an empty problem")


def test_troubleshoot_rejects_whitespace_problem():
    try:
        agent.troubleshoot(problem="   ", explain=False)
    except ValueError as exc:
        assert "must not be empty" in str(exc)
    else:
        raise AssertionError("Expected an error for a whitespace-only problem")
def test_select_diagnostic_tool_rejects_missing_answer(monkeypatch):
    from app import decision

    class FakeDecider:
        calls = 1
        last_latency_ms = 10

        @staticmethod
        def choice(**kwargs):
            return {"type": "choice"}

        def ask(self, state, questions):
            return {}

    monkeypatch.setattr(decision, "Decider", FakeDecider)

    try:
        decision.select_diagnostic_tool("Pod is crashing")
    except ValueError as exc:
        assert "missing a valid diagnostic_tool answer" in str(exc)
    else:
        raise AssertionError("Expected an error for a missing Decider answer")


def test_select_diagnostic_tool_rejects_unsupported_choice(monkeypatch):
    from app import decision

    class FakeDecider:
        calls = 1
        last_latency_ms = 10

        @staticmethod
        def choice(**kwargs):
            return {"type": "choice"}

        def ask(self, state, questions):
            return {
                "diagnostic_tool": {
                    "choice": "delete_pod",
                    "probabilities": {},
                    "confidence": 1.0,
                }
            }

    monkeypatch.setattr(decision, "Decider", FakeDecider)

    try:
        decision.select_diagnostic_tool("Pod is crashing")
    except ValueError as exc:
        assert "unsupported diagnostic tool" in str(exc)
    else:
        raise AssertionError("Expected an error for an unsupported choice")
