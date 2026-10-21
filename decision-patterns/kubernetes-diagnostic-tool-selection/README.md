# Reusable Decision Pattern: Kubernetes Diagnostic Tool Selection

**Project:** OpsPilot AI  
**Pattern:** Tool Selection  
**Decision Model:** Strands Decider 2B  
**Explanation Model:** Amazon Bedrock Nova Micro  
**Hackathon Tags:** `#strands-decider-2b` `#tool-selection`

## 1. Overview

OpsPilot AI demonstrates how an AI agent can use **Strands Decider 2B** to select the next diagnostic action for a Kubernetes troubleshooting scenario.

Instead of relying on a generative language model to choose a tool, the application sends a typed choice question to Strands Decider 2B. The decision model selects one option from a predefined set of diagnostic actions.

The agent validates the selected option, executes the corresponding diagnostic function, and collects the returned evidence. Amazon Bedrock can then generate a natural-language explanation of the findings.

This pattern separates decision-making, tool execution, and explanation into distinct stages, making the workflow easier to understand, test, and reuse.

## 2. Project Highlights

- **Typed decision-making:** Uses `Decider.choice()` to define a structured decision question and its available options.
- **Context-aware selection:** Supplies the Kubernetes problem description and available evidence to the decision process.
- **Three diagnostic options:** Pod status, container logs, and Kubernetes events.
- **Validated tool execution:** Rejects unsupported selections before executing diagnostic functions.
- **Agent integration:** Connects the selected option directly to the corresponding function in the agent workflow.
- **Decision transparency:** Exposes decision probabilities, reported confidence, and latency.
- **Optional AI explanation:** Uses Amazon Bedrock to generate natural-language troubleshooting guidance.
- **Reusable implementation:** Includes a documented pattern and runnable example for developers to adapt.

## 3. Problem Statement

When a Kubernetes application fails, an engineer may need to inspect several types of diagnostic information:

- Pod status, restart count, and termination details.
- Container logs containing application errors.
- Kubernetes events describing scheduling, image, or restart problems.

The agent must decide which diagnostic action to perform first based on the problem description and the evidence available to it.

OpsPilot AI uses Strands Decider 2B to make this tool-selection decision.

### Example scenario

The payments API pod is in `CrashLoopBackOff`, has restarted six times, and exited with code 1.

The agent must choose the most useful next diagnostic action from the supported options.

## 4. Decision Pattern Design

**Pattern type:** Tool selection

**Decision objective:** Select one diagnostic tool based on the Kubernetes problem description and any evidence supplied to the decision process.

### Available options

| Option | Description |
|---|---|
| `pod_status` | Inspect pod status, restart count, and last termination reason. |
| `container_logs` | Inspect recent container logs for application errors. |
| `pod_events` | Inspect Kubernetes events for scheduling, image, or restart problems. |

These options are defined in the `DIAGNOSTIC_CHOICES` dictionary in `app/decision.py`.

### Typed choice question

The pattern uses the Strands Decider `choice` question type.

The decision instructions are:

> Choose the single most useful next diagnostic tool for investigating the Kubernetes problem. Select the option best supported by the provided evidence. If evidence is limited, prefer pod_status.

The question defines the decision objective, while the options describe the actions available to the model.

### Decision state

The state contains the Kubernetes problem description and any evidence already available to the decision process.

Example:

```text
Kubernetes problem and available evidence:
The payments API pod is in CrashLoopBackOff, has restarted six times,
and exited with code 1.
```

## 5. Implementation

The primary implementation is in `app/decision.py`.

### Step 1: Define the diagnostic options

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

This dictionary defines the allowed decision options and gives the model a description of each action.

### Step 2: Create the typed question

The `Decider.choice()` method defines the decision instructions and available options.

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

Using a predefined set of choices makes the decision space explicit and helps the application map the answer to a supported diagnostic function.

### Step 3: Send the state and question

The problem description and typed question are passed to the Decider client.

```python
answers = decider.ask(
    state=f"Kubernetes problem and available evidence:\n{problem}",
    questions={"diagnostic_tool": question},
)
```

The returned answer identifies the selected diagnostic option.

### Step 4: Validate the selection

The implementation checks that the response contains a valid answer and that the selected option belongs to `DIAGNOSTIC_CHOICES`.

Unsupported selections are rejected rather than executed.

The complete implementation is available in `app/decision.py`.

## 6. Integrating the Decision into the Agent

The agent orchestration is implemented in `app/agent.py`.

The workflow is:

1. Receive the Kubernetes problem description.
2. Ask Strands Decider 2B to select a diagnostic tool.
3. Validate the returned selection.
4. Map the selected option to a supported diagnostic function.
5. Execute the selected function.
6. Collect the diagnostic evidence.
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

Separating the decision and execution stages makes the pattern easier to inspect, test, and extend.

## 7. Architecture

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

**Diagnostic scope:** The current implementation uses simulated diagnostic evidence. It demonstrates the complete decision-selection and evidence-processing workflow without querying a live Kubernetes cluster.

## 8. Running the Example Application

### Prerequisites

You need:

- Python 3.11 or a compatible version.
- The OpsPilot AI repository and its Python dependencies.
- A separately installed and running Strands Decider server with the supported model checkpoint.
- AWS credentials and appropriate IAM permissions if using the optional Bedrock explanation.

Follow the official Strands Decider documentation for installation and configuration:

https://github.com/strands-labs/strands-decider

### Start the Decider service

Activate the Python virtual environment from the repository root:

```bash
source .venv/bin/activate
```

Check the Decider server:

```bash
curl -sS http://127.0.0.1:8099/health
```

The server should return JSON describing its health and loaded model.

### Run the troubleshooting workflow

Run the application without invoking Amazon Bedrock:

```bash
python -m app.main \
  --problem "The Kubernetes pod is in CrashLoopBackOff, has restarted six times, and exited with code 1. Determine the most useful diagnostic action to investigate the cause." \
  --pod payments-api-demo \
  --namespace production \
  --skip-explanation
```

The output includes:

- The original problem description.
- The selected diagnostic tool.
- Decision probabilities and reported confidence.
- Decision latency.
- Diagnostic evidence.
- An optional explanation field.

The selected tool and probabilities may vary between runs.

## 9. Example Decision Result

A recorded successful run selected `container_logs` for the troubleshooting scenario.

```json
{
  "selected_tool": "container_logs",
  "probabilities": {
    "pod_status": 0.0886,
    "container_logs": 0.6629,
    "pod_events": 0.2485
  },
  "confidence": 0.4944,
  "decider_calls": 1,
  "latency_ms": 4599.57
}
```

The corresponding diagnostic function returned the following scenario evidence:

```text
Pod: payments-api-demo
Namespace: production
Simulated container log:
ERROR: Required environment variable DATABASE_URL is missing.
Application startup failed.
```

This example demonstrates how the selected tool determines which diagnostic function runs and what evidence is returned.

The reported probability for `container_logs` was approximately 66.29%. The recorded latency was approximately 4.6 seconds for this run. These values are illustrative results from one execution, not guarantees of diagnostic correctness or performance.

## 10. How to Reuse This Pattern

This pattern can be adapted to other applications that must select one action from a predefined set of tools.

### Step 1: Define the available options

Create a dictionary of supported option names and clear descriptions.

For example, a cloud-support agent might choose between:

- `inspect_metrics`
- `inspect_logs`
- `inspect_recent_deployments`

### Step 2: Write the decision instructions

Describe the decision objective and explain what the model should consider when selecting an option.

### Step 3: Create a typed choice question

Use the Strands Decider client to create a `choice` question with the supported options.

### Step 4: Supply the application state

Provide the problem description and relevant evidence available at decision time.

### Step 5: Validate the answer

Check that the returned option is supported by the application. Reject missing or unsupported selections.

### Step 6: Map options to functions

Create an allowlist mapping valid option names to application functions. Execute only functions explicitly registered in that mapping.

### Step 7: Evaluate the pattern

Test representative scenarios and inspect selected options, probabilities, confidence values, and latency. Evaluate decision quality instead of assuming that a valid response is necessarily the correct decision.

## 11. Decision Confidence and Safety

Strands Decider 2B returns decision information that can include option probabilities and a confidence value.

These values help developers inspect model behavior, but they do not guarantee that the selected diagnostic action is correct.

The current implementation:

- Validates the selected option.
- Rejects unsupported diagnostic tool names.
- Uses a predefined mapping of supported diagnostic functions.
- Does not implement an explicit confidence threshold.
- Does not implement automatic retries or a separate low-confidence fallback policy.
- Does not modify Kubernetes resources.

The instruction to prefer `pod_status` when evidence is limited is part of the decision question. It is not a separately enforced fallback mechanism.

For production-oriented extensions, developers should consider explicit uncertainty handling, additional validation, authentication, authorization, audit logging, and appropriate operational safeguards.

## 12. Strands Decider 2B and Amazon Bedrock

The components have distinct responsibilities in this pattern.

### Strands Decider 2B — Decision selection

Selects the diagnostic tool from the predefined options based on the supplied problem state.

### Diagnostic function — Evidence collection

Executes the selected application function and returns the corresponding diagnostic evidence.

### Amazon Bedrock — Natural-language explanation

Optionally generates a natural-language troubleshooting explanation from the problem description and diagnostic evidence.

The Bedrock explanation component is implemented separately in `app/explainer.py`.

A Bedrock invocation may incur AWS charges. The `--skip-explanation` option allows the decision and diagnostic workflow to run without invoking Bedrock.

## 13. Project Source Files

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

## 14. Future Enhancements

Potential extensions to this pattern include:

- Integrating read-only Kubernetes API diagnostics.
- Evaluating decision quality across representative failure scenarios.
- Implementing explicit low-confidence handling.
- Recording structured evaluation results.
- Measuring decision latency across repeated runs.
- Adding appropriate security controls before connecting to real clusters.

These are potential extensions to the current implementation.

## 15. References

- [Strands Decider repository](https://github.com/strands-labs/strands-decider)
- [Introducing Strands Decider](https://strandsagents.com/blog/introducing-strands-decider/)

## License

This pattern is part of OpsPilot AI and is distributed under the repository's MIT License.

Third-party components remain subject to their respective licenses and attribution requirements. See `THIRD_PARTY_NOTICES.md` for further information.
