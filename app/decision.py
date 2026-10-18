"""Use Strands Decider 2B to select a Kubernetes diagnostic tool."""

from app.decider_client import Decider

DIAGNOSTIC_CHOICES = {
    "pod_status": (
        "Inspect pod status, restart count, and last termination reason."
    ),
    "container_logs": (
        "Inspect recent container logs for application errors."
    ),
    "pod_events": (
        "Inspect Kubernetes events for scheduling, image, or restart problems."
    ),
}


def select_diagnostic_tool(problem: str) -> dict:
    """Ask Strands Decider to choose the most relevant diagnostic tool."""

    decider = Decider()

    question = Decider.choice(
        instructions=(
            "Choose the single most useful next diagnostic tool for investigating "
            "the Kubernetes problem. Select the option best supported by the "
            "provided evidence. If evidence is limited, prefer pod_status."
        ),
        criteria=DIAGNOSTIC_CHOICES,
    )

    answers = decider.ask(
        state=f"Kubernetes problem and available evidence:\n{problem}",
        questions={"diagnostic_tool": question},
    )

    answer = answers.get("diagnostic_tool")

    if not isinstance(answer, dict):
        raise ValueError("Decider response is missing a valid diagnostic_tool answer.")

    selected_tool = answer.get("choice")

    if selected_tool not in DIAGNOSTIC_CHOICES:
        raise ValueError(
            f"Decider selected an unsupported diagnostic tool: {selected_tool!r}"
        )

    return {
        "selected_tool": selected_tool,
        "probabilities": answer.get("probabilities", {}),
        "confidence": answer.get("confidence"),
        "decider_calls": decider.calls,
        "latency_ms": decider.last_latency_ms,
    }
