# OpsPilot AI — Intelligent Kubernetes Troubleshooting Agent

OpsPilot AI is a demonstration agent that uses **Strands Decider 2B** to select a diagnostic action for a Kubernetes troubleshooting scenario and can use **Amazon Bedrock** to generate a natural-language explanation of the returned evidence.

The project demonstrates a decision-driven agent workflow: receive a problem description, choose a diagnostic action, validate the choice, collect evidence, and optionally explain that evidence.

> **Project status:** Strands Decider 2B has been run successfully with the OpsPilot application. The Kubernetes diagnostic functions use simulated data; the application does not query a live cluster. A real Amazon Bedrock inference was successfully invoked during development, but its initial response was truncated at the 100-token output limit. The limit was later increased to 250 tokens; a response using the increased limit has not yet been verified.

## Features

- **Decision-driven tool selection:** Uses Strands Decider 2B to select a diagnostic action.
- **Three diagnostic options:** Pod status, container logs, and Kubernetes events.
- **Decision validation:** Validates the selected action before executing it.
- **Simulated diagnostic evidence:** Returns predefined evidence for demonstration and testing.
- **Optional Bedrock explanation:** Supports natural-language explanations through Amazon Bedrock.
- **Safety-conscious scope:** Does not connect to or modify a real Kubernetes cluster.
- **Automated tests:** Includes tests for the agent, diagnostic functions, and explanation component.
- **Reusable decision pattern:** Documents a tool-selection pattern and provides a runnable example.

## Architecture

The workflow is:

1. **Problem input:** The user describes a Kubernetes application problem.
2. **Decision:** Strands Decider 2B selects the most useful next diagnostic action.
3. **Validation:** OpsPilot checks that the selected action is one of the supported diagnostic tools.
4. **Diagnostic execution:** The selected function returns simulated evidence.
5. **Optional explanation:** Amazon Bedrock can generate a natural-language explanation when enabled.
6. **Result:** The application presents the selected action, probabilities, evidence, and optional explanation.

### Architecture flow

```text
                 User Problem
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
             | Validate Selected|
             | Diagnostic Tool  |
             +------------------+
                      |
                      v
             +------------------+
             | Diagnostic Tools |
             +------------------+
               /       |       \
              v        v        v
          Pod Status  Container  Kubernetes
                       Logs       Events
              \        |        /
               \       |       /
                      v
             +------------------+
             | Diagnostic       |
             | Evidence         |
             +------------------+
                      |
                      v
             +------------------+
             | Amazon Bedrock   |
             |    Optional      |
             |   Explanation    |
             +------------------+
                      |
                      v
                 Final Result
```

**Important:** Diagnostic evidence is simulated. This architecture demonstrates the workflow without requiring access to a live Kubernetes cluster.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application implementation |
| Strands Decider 2B | Diagnostic action selection |
| Strands Agents SDK | Agent framework integration |
| Amazon Bedrock | Optional natural-language explanations |
| Boto3 | AWS SDK for Python |
| Pytest | Automated testing |
| Linux | Development and execution environment |
| Git and GitHub | Version control and source hosting |

## Project Structure

```text
opspilot-ai/
├── app/
│   ├── __init__.py
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

The Strands Decider source checkout and Python virtual environment are local development resources and are intentionally excluded from this repository.

## Reusable Decision Pattern

OpsPilot includes a reusable **tool-selection** pattern for choosing the next diagnostic action. The pattern demonstrates how to define a decision question and supported options, obtain a decision from Strands Decider, validate the selected option, and connect the result to the agent's execution path.

- [Read the pattern documentation](decision-patterns/kubernetes-diagnostic-tool-selection/README.md)
- [Run the example](decision-patterns/kubernetes-diagnostic-tool-selection/example.py)

The example calls the configured Decider service. It does not require a live Kubernetes cluster because the diagnostic data used by the application is simulated.

## Requirements and Limitations

Before running the application, ensure you have:

- Python 3.11 or a compatible version.
- Git.
- The application dependencies listed in `requirements.txt`.
- A separately installed and running Strands Decider server.
- The supported Strands Decider 2B model checkpoint configured for that server.
- AWS credentials and appropriate IAM permissions if you want to use the optional Bedrock explanation.

For the latest Decider installation and model setup instructions, refer to the [official Strands Decider repository](https://github.com/strands-labs/strands-decider).

### Dependency reproducibility

The current `requirements.txt` lists `strands-agents` and `boto3` without pinned versions. The application has been tested in its existing development environment, but a complete installation from a fresh environment has not yet been verified. Installation reproducibility across environments is therefore not guaranteed.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/suganya-subramanian/opspilot-ai.git
cd opspilot-ai
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install application dependencies and test tools

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pytest
```

These commands install the dependencies declared by the project and the test runner. They do **not** install the separate Strands Decider server or download its model checkpoint.

### 4. Install and configure Strands Decider

Follow the installation instructions in the [official Strands Decider repository](https://github.com/strands-labs/strands-decider). Install the supported model checkpoint and configure the server according to the upstream documentation.

The development environment used for this project runs the server at:

```text
http://127.0.0.1:8099
```

The application can use a different compatible endpoint through the `STRANDS_DECIDER_URL` environment variable.

### 5. Start the Decider server

Start the server in a separate terminal, following the official installation instructions. In the development environment used for this project, the command was:

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

This command assumes the Decider executable and model checkpoint are already installed in that environment. The model identifier and command may need to be adjusted to match the upstream installation instructions and your machine.

Check the server health:

```bash
curl -sS http://127.0.0.1:8099/health
```

The server should return JSON indicating its health and loaded model.

**Resource note:** Running a 2B model on a CPU requires sufficient memory. Resource usage and inference latency depend on the machine and runtime configuration.

## Running OpsPilot AI

Run commands from the repository root with the virtual environment activated and the Decider server available.

### Run without Amazon Bedrock

Use `--skip-explanation` to execute the decision and diagnostic workflow without making a Bedrock inference call:

```bash
python -m app.main \
  --problem "The Kubernetes pod is in CrashLoopBackOff, has restarted six times, and exited with code 1. Determine the most useful diagnostic action to investigate the cause." \
  --pod payments-api-demo \
  --namespace production \
  --skip-explanation
```

The output includes information such as:

- Problem description.
- Pod name and namespace.
- Selected diagnostic action.
- Decision probabilities and reported confidence.
- Decision latency.
- Diagnostic evidence.
- An empty or null explanation when explanation generation is skipped.

The selected action and probabilities may vary between runs because model decisions can be stochastic.

### Example output

The following is a recorded example from a successful run using Strands Decider 2B. It is also stored in `artifacts/decider-demo-output.json`.

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

This example shows that the Decider selected `container_logs`, after which the diagnostic function returned simulated evidence indicating that the `DATABASE_URL` environment variable was missing.

**Interpreting the decision:** The selected tool's reported probability was approximately 66.29%, and the reported confidence was 0.4944. Neither value guarantees that the selected action is correct. The recorded latency of 4599.57 milliseconds is from one run and is not a performance guarantee.

## Available Diagnostic Tools

OpsPilot currently supports three simulated diagnostic actions.

### 1. Pod status

Returns example information about pod state, restart count, and last exit code.

Example evidence:

```text
Pod status: CrashLoopBackOff
Restart count: 6
Last exit code: 1
```

### 2. Container logs

Returns example application log output.

Example evidence:

```text
ERROR: Required environment variable DATABASE_URL is missing.
Application startup failed.
```

This simulated evidence suggests that the application may be failing during startup because a required environment variable is absent. It is not evidence collected from a real container.

### 3. Kubernetes events

Returns simulated event information associated with the pod.

Example evidence:

```text
Warning BackOff
Container restart back-off observed.
```

These functions do not retrieve live pod status, container logs, or Kubernetes events.

## Amazon Bedrock Integration

OpsPilot includes an optional explanation component that uses Amazon Bedrock to generate natural-language troubleshooting guidance from diagnostic evidence.

### Configuration

The current defaults are:

| Setting | Default |
|---|---|
| AWS region | `ap-south-1` |
| Bedrock inference profile | `apac.amazon.nova-micro-v1:0` |

You can override the defaults using environment variables:

```bash
export AWS_REGION="ap-south-1"
export BEDROCK_MODEL_ID="apac.amazon.nova-micro-v1:0"
```

Ensure that the inference profile is available to your AWS account and that the execution identity has the required Bedrock permissions.

Inspect the configured AWS identity:

```bash
aws sts get-caller-identity
```

Check inference-profile metadata:

```bash
aws bedrock get-inference-profile \
  --inference-profile-identifier apac.amazon.nova-micro-v1:0 \
  --region ap-south-1
```

Permission to inspect inference-profile metadata does not guarantee permission to invoke the model.

### Cost and permissions

A real Bedrock invocation may incur charges. Before enabling explanations:

- Verify model and inference-profile availability.
- Verify the required IAM permissions.
- Review applicable AWS pricing.
- Use appropriate AWS budget and cost controls.

**Bedrock status:** A real Amazon Bedrock inference was successfully invoked during development. The initial response was truncated at the 100-token output limit. The output limit was subsequently increased to 250 tokens, but a response using the increased limit has not yet been verified.

To avoid additional Bedrock inference calls and potential charges, use `--skip-explanation` when running the CLI.

## Testing

Run the tests from the project root with the virtual environment activated:

```bash
python -m pytest -q tests/
```

### Recorded test result

```text
11 passed
```

The 11 project tests passed in the existing development environment. This recorded result describes that test run; it is not a guarantee that tests will pass in every environment.

Passing these tests does not establish live Kubernetes integration, a verified complete Bedrock explanation, or a successful installation from a fresh environment.

## Evidence and Artifacts

The `artifacts/` directory contains example outputs generated during development.

| File | Description |
|---|---|
| `decider-demo-output.json` | Example decision and diagnostic output |
| `decider-health.json` | Recorded Decider server health information |
| `test-results.txt` | Recorded automated test result |

These artifacts support the demonstration and help reviewers understand the application's behavior. They are records from a development environment, not a guarantee that every future run will produce the same result.

## Safety and Limitations

OpsPilot is a demonstration project with explicit limitations:

- **Simulated diagnostics:** Diagnostic functions return predefined example evidence rather than querying a live Kubernetes cluster.
- **No cluster modifications:** The application does not create, update, or delete Kubernetes resources.
- **Decision validation:** The application validates the selected diagnostic action before executing it.
- **Model uncertainty:** A selected action and its reported probability do not guarantee a correct diagnosis.
- **Optional Bedrock inference:** Real explanations require suitable AWS configuration and may incur charges.
- **No production-readiness claim:** Live Kubernetes access, authentication, authorization, operational monitoring, and production security controls have not been established by this demonstration.

Do not use simulated diagnostic results as evidence about a real production workload.

## Future Improvements

Potential future enhancements include:

- Integrating read-only Kubernetes API diagnostics.
- Collecting real pod status, container logs, and events.
- Adding further validation and error-handling tests.
- Verifying the quality and completeness of Bedrock explanations with the current output limit.
- Adding structured incident summaries and recommended next steps.
- Improving observability, latency measurement, and failure reporting.
- Adding production-grade authentication, authorization, and audit logging before real cluster integration.

These are proposed enhancements, not completed features.

## Third-Party Attribution

OpsPilot uses Strands Decider 2B and adapts the upstream example client implementation.

**Upstream repository:** [strands-labs/strands-decider](https://github.com/strands-labs/strands-decider)

The upstream project is licensed under the Apache License 2.0. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and [`licenses/Apache-2.0.txt`](licenses/Apache-2.0.txt) for the included attribution and license information.

## License

OpsPilot AI's original project code is distributed under the MIT License. See [`LICENSE`](LICENSE).

Third-party material remains subject to its applicable license and attribution requirements.
