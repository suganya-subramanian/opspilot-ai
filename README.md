# OpsPilot AI — Intelligent Kubernetes Troubleshooting Agent

OpsPilot AI is a decision-driven troubleshooting agent built using **Strands Decider 2B** and **Amazon Bedrock**. It selects a diagnostic action for a Kubernetes troubleshooting scenario, validates the decision, collects diagnostic evidence, and can generate a natural-language explanation of the findings.

The project demonstrates how decision-making can be integrated into an AI agent workflow to make diagnostic tool selection more structured and transparent.

## Project Highlights

- **Intelligent tool selection:** Uses Strands Decider 2B to select the next diagnostic action.
- **Three diagnostic options:** Pod status, container logs, and Kubernetes events.
- **Decision transparency:** Displays the selected tool, decision probabilities, reported confidence, Decider call count, and latency.
- **Validated execution:** Checks the selected diagnostic action before invoking the corresponding function.
- **Amazon Bedrock integration:** Adds an optional natural-language troubleshooting explanation component.
- **Reusable decision pattern:** Includes a documented and runnable tool-selection example for reuse in other agent projects.
- **Automated testing:** Includes tests for agent behavior, diagnostic functions, and the explanation component.
- **Open-source repository:** Includes source code, test artifacts, third-party attribution, and license information.

## Project Links

- **GitHub Repository:** https://github.com/suganya-subramanian/opspilot-ai
- **Demo Video:** https://youtu.be/VyUEszeYRyU

## Architecture and Workflow

OpsPilot follows a decision-driven workflow:

1. **Problem input:** Receive a Kubernetes troubleshooting scenario.
2. **Decision selection:** Strands Decider 2B chooses the most relevant diagnostic action from the available options.
3. **Decision validation:** Verify that the selected action is supported.
4. **Diagnostic execution:** Execute the corresponding diagnostic function.
5. **Evidence collection:** Return the diagnostic information for the scenario.
6. **AI explanation:** Optionally send the evidence to Amazon Bedrock for a natural-language explanation.
7. **Final result:** Present the selected action, decision metrics, diagnostic evidence, and optional explanation.

### Architecture Diagram

```text
              Kubernetes Problem
                      |
                      v
              +------------------+
              |   OpsPilot AI    |
              |      Agent       |
              +------------------+
                      |
                      v
              +------------------+
              | Strands Decider  |
              |       2B         |
              +------------------+
                      |
                      v
              +------------------+
              | Validate Decision|
              +------------------+
                      |
                      v
              +------------------+
              | Diagnostic Tools |
              +------------------+
                /       |       \
               v        v        v
           Pod Status  Container  Pod Events
                        Logs
                \       |       /
                 \      |      /
                      v
              +------------------+
              | Diagnostic       |
              | Evidence         |
              +------------------+
                      |
                      v
              +------------------+
              | Amazon Bedrock   |
              |   Explanation    |
              |    (Optional)    |
              +------------------+
                      |
                      v
                 Final Result
```

**Diagnostic scope:** The current demonstration uses simulated Kubernetes evidence and does not query or modify a live cluster. This allows the decision-making and explanation workflow to be demonstrated without requiring access to a running Kubernetes environment.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Strands Decider 2B | Diagnostic action selection |
| Strands Agents SDK | Agent framework integration |
| Amazon Bedrock | Natural-language explanation |
| Boto3 | AWS SDK for Python |
| Pytest | Automated testing |
| Linux | Development and execution |
| Git and GitHub | Version control and source hosting |

## Project Structure

```text
opspilot-ai/
├── app/
│   ├── agent.py
│   ├── decider_client.py
│   ├── decision.py
│   ├── diagnostics.py
│   ├── explainer.py
│   └── main.py
├── artifacts/
│   ├── decider-demo-output.json
│   ├── decider-health.json
│   └── test-results.txt
├── decision-patterns/
│   └── kubernetes-diagnostic-tool-selection/
│       ├── README.md
│       └── example.py
├── licenses/
│   └── Apache-2.0.txt
├── tests/
│   ├── test_agent.py
│   ├── test_diagnostics.py
│   └── test_explainer.py
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── THIRD_PARTY_NOTICES.md
```

The Strands Decider source checkout and Python virtual environment are separate development resources and are not included in the repository.

## Reusable Decision Pattern

OpsPilot includes a reusable **tool-selection decision pattern** demonstrating how to:

1. Define a decision question and supported options.
2. Request a decision from Strands Decider.
3. Validate the selected option.
4. Connect the decision to the agent's execution path.

Explore the implementation:

- [Decision pattern documentation](decision-patterns/kubernetes-diagnostic-tool-selection/README.md)
- [Runnable example](decision-patterns/kubernetes-diagnostic-tool-selection/example.py)

This pattern can serve as a starting point for agents that need to choose among multiple tools or diagnostic actions.

## Requirements

- Python 3.11 or a compatible version
- Git
- Application dependencies listed in `requirements.txt`
- A separately installed and running Strands Decider server with a supported model checkpoint
- AWS credentials and appropriate IAM permissions for the optional Bedrock explanation

For the latest Decider installation instructions, refer to the [official Strands Decider repository](https://github.com/strands-labs/strands-decider).

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/suganya-subramanian/opspilot-ai.git
cd opspilot-ai
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pytest
```

### 4. Install and start Strands Decider

Install Strands Decider and its supported model checkpoint by following the upstream documentation.

In the development environment used for this project, the server ran at `http://127.0.0.1:8099`.

Check the server health:

```bash
curl -sS http://127.0.0.1:8099/health
```

The following is the command used in that environment, assuming the executable and model checkpoint are already installed:

```bash
cd ~/opspilot-ai
source .venv/bin/activate

nohup .venv/bin/strands-decider serve \
  StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 \
  --device cpu \
  --host 127.0.0.1 \
  --port 8099 \
  > ~/opspilot-decider.log 2>&1 < /dev/null &
```

If your Decider service uses another compatible endpoint, configure `STRANDS_DECIDER_URL` accordingly. Running the 2B model on CPU requires sufficient memory, and inference latency depends on the environment.

## Running OpsPilot AI

Run the following commands from the repository root with the virtual environment activated and the Decider service running.

### Run without the Bedrock explanation

```bash
python -m app.main \
  --problem "The Kubernetes pod is in CrashLoopBackOff, has restarted six times, and exited with code 1. Determine the most useful diagnostic action to investigate the cause." \
  --pod payments-api-demo \
  --namespace production \
  --skip-explanation
```

The application returns the problem details, selected diagnostic tool, decision metrics, and diagnostic evidence. The `--skip-explanation` option skips the Bedrock inference call.

## Example Decision Output

The following is a recorded successful run using Strands Decider 2B, also available in `artifacts/decider-demo-output.json`.

```json
{
  "problem": "The Kubernetes pod is in CrashLoopBackOff, has restarted six times, and exited with code 1. Determine the most useful diagnostic action to investigate the cause.",
  "pod_name": "payments-api-demo",
  "namespace": "production",
  "decision": {
    "selected_tool": "container_logs",
    "probabilities": {
      "pod_status": 0.0886,
      "container_logs": 0.6629,
      "pod_events": 0.2485
    },
    "confidence": 0.4944,
    "decider_calls": 1,
    "latency_ms": 4599.57
  },
  "diagnostic_tool": "container_logs",
  "diagnostic_evidence": "Pod: payments-api-demo\nNamespace: production\nSimulated container log:\nERROR: Required environment variable DATABASE_URL is missing.\nApplication startup failed.",
  "explanation": null
}
```

### Understanding the result

- **Selected tool:** `container_logs`
- **Reported probability:** Approximately 66.29% for the selected tool.
- **Reported confidence:** `0.4944`
- **Decider calls:** `1`
- **Recorded latency:** Approximately 4.6 seconds in this run.
- **Diagnostic finding:** The scenario evidence indicates that the required `DATABASE_URL` environment variable is missing.

The decision probabilities and latency are example values from a recorded run. Results may vary between runs, and model-reported confidence does not guarantee diagnostic correctness.

## Diagnostic Tools

### 1. Pod Status

Returns scenario information about pod state, restart count, and last exit code.

```text
Pod status: CrashLoopBackOff
Restart count: 6
Last exit code: 1
```

### 2. Container Logs

Returns example application log output.

```text
ERROR: Required environment variable DATABASE_URL is missing.
Application startup failed.
```

This scenario illustrates how missing application configuration can cause startup failure.

### 3. Kubernetes Events

Returns example event information associated with the pod.

```text
Warning BackOff
Container restart back-off observed.
```

## Amazon Bedrock Integration

OpsPilot includes an optional explanation component that uses Amazon Bedrock to turn diagnostic evidence into natural-language troubleshooting guidance.

### Configuration

| Setting | Default |
|---|---|
| AWS Region | `ap-south-1` |
| Bedrock inference profile | `apac.amazon.nova-micro-v1:0` |

Configure the values using environment variables if needed:

```bash
export AWS_REGION="ap-south-1"
export BEDROCK_MODEL_ID="apac.amazon.nova-micro-v1:0"
```

Verify the active AWS identity:

```bash
aws sts get-caller-identity
```

Inspect the inference profile:

```bash
aws bedrock get-inference-profile \
  --inference-profile-identifier apac.amazon.nova-micro-v1:0 \
  --region ap-south-1
```

The AWS account must have access to the inference profile and the IAM permissions required to invoke it.

A real Amazon Bedrock inference was successfully invoked during development. The response output limit was increased after an initial response was truncated; review the returned explanation and configured token limit when adapting the application.

**Cost consideration:** Bedrock inference may incur charges. Review applicable AWS pricing and configure appropriate cost controls. Use `--skip-explanation` to run the workflow without a Bedrock call.

## Testing and Verification

Run the automated test suite:

```bash
python -m pytest -q tests/
```

**Recorded result: `11 passed`.**

The tests cover the agent, diagnostic functions, and explanation component in the development environment.

The `artifacts/` directory contains supporting records:

| File | Purpose |
|---|---|
| `decider-demo-output.json` | Example decision and diagnostic output |
| `decider-health.json` | Recorded Decider server health |
| `test-results.txt` | Recorded test result |

## Safety and Intended Use

OpsPilot is a demonstration and learning project. Its diagnostic functions return predefined scenario evidence; the application does not retrieve live pod status, logs, or events, and does not create, update, or delete Kubernetes resources.

Before connecting this workflow to a real cluster, implement and validate appropriate read-only Kubernetes access, authentication and authorization, operational monitoring, audit logging, error handling, and production security controls.

## Future Enhancements

Potential next steps include:

- Integrating read-only Kubernetes API diagnostics.
- Collecting real pod status, container logs, and events.
- Expanding validation and error-handling tests.
- Evaluating explanation quality across more troubleshooting scenarios.
- Adding structured incident summaries and recommended next steps.
- Improving observability, latency measurement, and failure reporting.
- Establishing production-grade authentication, authorization, and audit logging before live cluster integration.

These items are proposed enhancements, not completed features.

## Third-Party Attribution

OpsPilot uses Strands Decider 2B and adapts the upstream example client implementation.

- **Upstream repository:** [strands-labs/strands-decider](https://github.com/strands-labs/strands-decider)
- **Upstream license:** Apache License 2.0

See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and [`licenses/Apache-2.0.txt`](licenses/Apache-2.0.txt) for attribution and license details.

## License

OpsPilot AI's original project code is distributed under the MIT License. See [`LICENSE`](LICENSE).

Third-party material remains subject to its applicable license and attribution requirements.
