"""Orchestrate safe Kubernetes diagnostics for OpsPilot AI."""

from app import diagnostics
from app.decision import select_diagnostic_tool
from app.explainer import generate_explanation


DIAGNOSTIC_FUNCTIONS = {
    "pod_status": diagnostics.get_pod_status,
    "container_logs": diagnostics.get_container_logs,
    "pod_events": diagnostics.get_pod_events,
}


def troubleshoot(
    problem: str,
    pod_name: str = "demo-app",
    namespace: str = "default",
    explain: bool = True,
) -> dict:
    """Select and run a simulated diagnostic, then optionally explain findings."""

    if not problem or not problem.strip():
        raise ValueError("Problem description must not be empty.")

    # Step 1: Ask Strands Decider to select the diagnostic.
    decision = select_diagnostic_tool(problem)

    selected_tool = decision.get("selected_tool")

    # Never execute an arbitrary tool name returned by the decision service.
    if selected_tool not in DIAGNOSTIC_FUNCTIONS:
        raise ValueError(
            f"Decider returned an unsupported diagnostic tool: {selected_tool!r}"
        )

    # Step 2: Run the selected simulated diagnostic.
    diagnostic_function = DIAGNOSTIC_FUNCTIONS[selected_tool]
    evidence = diagnostic_function(
        pod_name=pod_name,
        namespace=namespace,
    )

    result = {
        "problem": problem,
        "pod_name": pod_name,
        "namespace": namespace,
        "decision": decision,
        "diagnostic_tool": selected_tool,
        "diagnostic_evidence": evidence,
        "explanation": None,
    }

    # Step 3: Call Bedrock only when explicitly enabled by the caller.
    if explain:
        result["explanation"] = generate_explanation(
            problem=problem,
            diagnostic_evidence=evidence,
        )

    return result
