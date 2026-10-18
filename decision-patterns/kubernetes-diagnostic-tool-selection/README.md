# Reusable Decision Pattern: Kubernetes Diagnostic Tool Selection

**Project:** OpsPilot AI  
**Pattern:** Tool Selection  
**Decision Model:** Strands Decider 2B  
**Generative Model:** Amazon Bedrock Nova Micro  
**Hackathon Tags:** `#strands-decider-2b` `#tool-selection`

---

## 1. Overview

This reusable decision pattern demonstrates how an AI agent can use Strands Decider 2B to select the most appropriate diagnostic tool for investigating a Kubernetes application problem.

Instead of asking a generative language model to choose a tool, the agent sends a typed choice question to Strands Decider 2B. The decision model selects one option from a predefined set.

The agent validates the selection before executing the corresponding diagnostic function. Amazon Bedrock can then generate a natural-language explanation from the problem and diagnostic evidence.

This pattern can be adapted to other agents that must choose one action from a set of available tools.

## 2. Problem Statement

When a Kubernetes application fails, an engineer may need to inspect several types of diagnostic information:

- Pod status and restart information.
- Container logs containing application errors.
- Kubernetes events describing scheduling, image, or restart problems.

The agent must decide which diagnostic action to perform first.

OpsPilot AI uses Strands Decider 2B to make this tool-selection decision.

### Example Problem

The payments API pod is in `CrashLoopBackOff`, has restarted six times, and exited with code 1.

The agent must choose the most useful next diagnostic action.

## 3. Decision Pattern

**Pattern type:** Tool selection

**Decision objective:** Select one diagnostic tool based on the Kubernetes problem description and any evidence included in the decision state.

### Available Options

| Option | Description |
|---|---|
| `pod_status` | Inspect pod status, restart count, and last termination reason. |
| `container_logs` | Inspect recent container logs for application errors. |
| `pod_events` | Inspect Kubernetes events for scheduling, image, or restart problems. |

These options are defined in the `DIAGNOSTIC_CHOICES` dictionary in `app/decision.py`.

### Typed Question

The pattern uses the Strands Decider `choice` question type.

The question instructions are:

> Choose the single most useful next diagnostic tool for investigating the Kubernetes problem. Select the option best supported by the provided evidence. If evidence is limited, prefer pod_status.

The options and their descriptions are supplied to the model at runtime.

### Decision State

The state contains the Kubernetes problem description and any evidence already available to the decision process.

Example:

```text
Kubernetes problem and available evidence:
The payments API pod is in CrashLoopBackOff, has restarted six times,
and exited with code 1.
```

## 4. Implementation

The primary implementation is in `app/decision.py`.

### Define the Options

```python
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
```

### Create the Typed Question

The `Decider.choice()` method defines the decision question and its available options.

```python
question = Decider.choice(
    instructions=(
        "Choose the single most useful next diagnostic tool for investigating "
        "the Kubernetes problem. Select the option best supported by the "
        "provided evidence. If evidence is limited, prefer pod_status."
    ),
    criteria=DIAGNOSTIC_CHOICES,
)
```

### Send the State and Question

The problem description and typed question are sent to the Decider client.

```python
answers = decider.ask(
    state=f"Kubernetes problem and available evidence:\n{problem}",
    questions={"diagnostic_tool": question},
)
```

### Validate the Selection

The implementation checks that the response contains a valid answer and that the selected option belongs to `DIAGNOSTIC_CHOICES`.

Unsupported selections are rejected rather than executed.

The complete implementation is available in `app/decision.py`.

## 5. Wiring the Decision into the Agent

The agent orchestration is implemented in `app/agent.py`.

The workflow is:

1. Receive the Kubernetes problem description.
2. Ask Strands Decider 2B to select a diagnostic tool.
3. Validate the returned selection.
4. Map the selected option to a supported diagnostic function.
5. Execute the diagnostic function.
6. Collect the resulting evidence.
7. Optionally call Amazon Bedrock to generate an explanation.
8. Return the decision and diagnostic results.

The diagnostic-function mapping is:

```python
DIAGNOSTIC_FUNCTIONS = {
    "pod_status": diagnostics.get_pod_status,
    "container_logs": diagnostics.get_container_logs,
    "pod_events": diagnostics.get_pod_events,
}
```

Before executing a diagnostic, the agent checks that the selected option exists in this mapping.

The decision and execution stages are separate, making the pattern easier to inspect, test, and reuse.

## 6. Architecture

```text
             Kubernetes Problem
                      |
                      v
              OpsPilot AI Agent
                      |
                      v
             Strands Decider 2B
                      |
                      v
             Typed Choice Question
                      |
                      v
              Selected Tool Name
                      |
                      v
             Validate the Selection
                      |
                      v
             Execute Diagnostic Tool
                      |
                      v
              Diagnostic Evidence
                      |
                      v
              Amazon Bedrock
                (Optional)
                      |
                      v
                Final Result
```

**Important:** The diagnostic functions in the current OpsPilot AI implementation return simulated evidence. They do not query a live Kubernetes cluster.

## 7. Running the Example Application

### Prerequisites

You need:

- Python 3.11 or a compatible version.
- The OpsPilot AI repository.
- The project's Python dependencies.
- A running Strands Decider server with the supported model checkpoint.

Follow the official Strands Decider documentation to install and configure the server:

https://github.com/strands-labs/strands-decider

### Start the Application

From the repository root, activate the Python virtual environment:

```bash
source .venv/bin/activate
```

Check that the Decider server is responding:

```bash
curl -sS http://127.0.0.1:8099/health
```

Run the troubleshooting workflow without invoking Amazon Bedrock:

```bash
python -m app.main \
  --problem "The Kubernetes pod is in CrashLoopBackOff, has restarted six times, and exited with code 1. Determine the most useful diagnostic action to investigate the cause." \
  --pod payments-api-demo \
  --namespace production \
  --skip-explanation
```

The application returns information including:

- The original problem description.
- The selected diagnostic tool.
- Decision probabilities and confidence information.
- Decision latency.
- Diagnostic evidence.
- An optional explanation field.

The selected tool and probabilities may vary between runs.

## 8. How to Reuse This Pattern

You can adapt this decision pattern to other applications that need to select one action from a predefined set.

### Step 1: Define the Available Options

Create a dictionary containing valid option names and clear descriptions.

For example, a cloud-support agent might choose between:

- `inspect_metrics`
- `inspect_logs`
- `inspect_recent_deployments`

### Step 2: Write the Decision Instructions

Describe the decision objective clearly.

Specify what the model should consider when selecting an option.

### Step 3: Create a Typed Choice Question

Use the Strands Decider client to create a `choice` question with the available options.

### Step 4: Supply the Application State

Provide the problem description and any relevant evidence already available.

### Step 5: Validate the Answer

Check that the returned option is supported by the application.

Reject missing or unsupported selections.

### Step 6: Map Options to Functions

Create an allowlist mapping valid option names to application functions.

Execute only functions explicitly registered in that mapping.

### Step 7: Evaluate the Pattern

Test representative scenarios and inspect the selected options, probabilities, confidence values, and latency.

Measure decision quality rather than assuming that a valid response is necessarily a correct decision.

## 9. Confidence and Safety Considerations

Strands Decider 2B returns decision information that can include option probabilities and a confidence value.

These values can help developers inspect model behavior. They do not guarantee that the selected diagnostic action is correct.

The current implementation:

- Validates the selected option.
- Rejects unsupported diagnostic tool names.
- Uses a predefined mapping of supported diagnostic functions.
- Does not implement an explicit confidence threshold.
- Does not implement automatic retries or a separate low-confidence fallback policy.
- Does not modify Kubernetes resources.

The instruction to prefer `pod_status` when evidence is limited is part of the decision question. It is not a separately enforced fallback mechanism.

For production-oriented extensions, developers should consider explicit uncertainty handling, additional validation, authentication, authorization, audit logging, and appropriate operational safeguards.

## 10. Strands Decider 2B and Amazon Bedrock

The two models have different responsibilities in this pattern.

### Strands Decider 2B

Responsible for selecting the diagnostic tool from the available options.

### Diagnostic Function

Responsible for returning the diagnostic evidence associated with the selected option.

### Amazon Bedrock

Optionally generates a natural-language troubleshooting explanation using the problem description and diagnostic evidence.

The Bedrock explanation component is implemented separately in `app/explainer.py`.

A Bedrock invocation may incur AWS charges. The `--skip-explanation` option allows the decision and diagnostic workflow to run without invoking Bedrock.

## 11. Project Source Files

| File | Responsibility |
|---|---|
| `app/decision.py` | Defines the typed decision and validates the selected option. |
| `app/decider_client.py` | Communicates with the Strands Decider server. |
| `app/agent.py` | Orchestrates decision-making and diagnostic execution. |
| `app/diagnostics.py` | Implements the simulated diagnostic functions. |
| `app/explainer.py` | Provides optional Amazon Bedrock explanations. |
| `tests/test_agent.py` | Tests agent behavior. |
| `tests/test_diagnostics.py` | Tests diagnostic functions. |
| `tests/test_explainer.py` | Tests explanation functionality. |

## 12. Limitations and Future Improvements

This pattern demonstrates decision-driven tool selection, but it is not a production-ready Kubernetes troubleshooting system.

Current limitations include:

- Diagnostic data is simulated.
- Live Kubernetes API integration is not implemented.
- A selected tool is not guaranteed to be the most useful action.
- Confidence-based routing and fallback handling are not implemented.
- Performance and decision quality have not been comprehensively benchmarked.
- Fresh-environment installation reproducibility has not been fully verified.

Potential improvements include:

- Adding read-only Kubernetes API diagnostics.
- Testing decision quality across representative failure scenarios.
- Implementing explicit low-confidence handling.
- Recording structured evaluation results.
- Measuring decision latency across repeated runs.
- Adding appropriate security controls before connecting to real clusters.

## 13. References

- Strands Decider repository: https://github.com/strands-labs/strands-decider
- Strands Decider introduction: https://strandsagents.com/blog/introducing-strands-decider/

## License

This pattern is part of OpsPilot AI and is distributed under the repository's MIT License.

Third-party components remain subject to their respective licenses and attribution requirements. See `THIRD_PARTY_NOTICES.md` for further information.
