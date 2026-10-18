# OpsPilot AI — Intelligent Kubernetes Troubleshooting Agent

OpsPilot AI is an intelligent Kubernetes troubleshooting agent that uses **Strands Decider 2B** to select diagnostic actions and **Amazon Bedrock** to generate natural-language troubleshooting explanations.

The project demonstrates how an AI agent can select a diagnostic tool, collect evidence, and explain potential causes of Kubernetes application failures.

> **Project status:** Strands Decider 2B has been tested with the OpsPilot application. Kubernetes diagnostic functions currently use simulated data. A successful real Amazon Bedrock inference has not yet been verified.

## Features

- **Intelligent decision-making:** Uses Strands Decider 2B to select a diagnostic action.
- **Diagnostic tool selection:** Chooses among pod-status, container-log, and Kubernetes-event diagnostics.
- **Decision validation:** Validates the selected diagnostic action before execution.
- **Diagnostic evidence:** Returns evidence from simulated Kubernetes diagnostic functions.
- **AI-powered explanations:** Supports optional troubleshooting explanations using Amazon Bedrock.
- **Safety-focused design:** Does not connect to or modify a real Kubernetes cluster.
- **Automated testing:** Includes tests for the agent, diagnostic tools, and explanation functionality.
- **Demonstration artifacts:** Stores example decision output, server health information, and test results.

## Architecture

The OpsPilot workflow consists of the following steps:

1. **Problem input:** The user describes a Kubernetes application problem.
2. **Decision-making:** Strands Decider 2B selects a diagnostic action.
3. **Decision validation:** OpsPilot validates the selected action against the supported diagnostic tools.
4. **Diagnostic execution:** The selected diagnostic function returns evidence.
5. **Explanation:** Amazon Bedrock can generate a natural-language explanation when enabled.
6. **Result:** The application presents the selected action, decision probabilities, diagnostic evidence, and optional explanation.

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
             | Optional         |
             | Explanation      |
             +------------------+
                      |
                      v
                 Final Result
```

**Note:** The diagnostic functions return simulated evidence. The architecture demonstrates the troubleshooting workflow without requiring a live Kubernetes cluster.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application implementation |
| Strands Decider 2B | Diagnostic action selection |
| Strands Agents SDK | Agent tools and integration |
| Amazon Bedrock | Optional natural-language explanations |
| Boto3 | AWS SDK for Python |
| Pytest | Automated testing |
| Linux | Application execution environment |
| Git | Version control |

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

The Strands Decider source checkout and Python virtual environment are local development resources and are intentionally excluded from the OpsPilot repository.

## Requirements

Before running OpsPilot, ensure that you have:

- Python 3.11 or a compatible version.
- Git.
- The Strands Agents SDK.
- A working Strands Decider server.
- The supported Strands Decider 2B model checkpoint.
- AWS credentials and appropriate IAM permissions if using Amazon Bedrock explanations.

For the latest Decider installation and model setup instructions, refer to the [official Strands Decider repository](https://github.com/strands-labs/strands-decider).

### Dependency reproducibility

The current `requirements.txt` lists `strands-agents` and `boto3` without pinned versions.

The application has been tested in its existing development environment, but a complete installation from a fresh environment has not yet been verified. Consequently, installation reproducibility across different environments is not guaranteed.

## Installation

### 1. Clone the repository

After publishing this project, replace the placeholder with your actual GitHub repository URL.

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd opspilot-ai
```

### 2. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install application dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pytest
```

These commands install the application dependencies declared in `requirements.txt` and the test runner.

**Important:** They do not install the separate Strands Decider server or download its model checkpoint.

### 4. Install and configure Strands Decider

Follow the official installation instructions:

https://github.com/strands-labs/strands-decider

Install the supported model checkpoint and configure the Decider server according to the upstream documentation.

The development environment used for this project runs the server at:

```text
http://127.0.0.1:8099
```

The application can be configured to use another endpoint through the `STRANDS_DECIDER_URL` environment variable, provided that the endpoint is compatible with the client.

### 5. Start the Decider server

Start the server in a separate terminal, following the official installation instructions.

In the development environment used for this project, the server was started with:

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

This command assumes that the Decider executable and model checkpoint have already been installed in the environment.

Check server health:

```bash
curl -sS http://127.0.0.1:8099/health
```

The server should return a JSON response indicating its health and loaded model.

**Resource note:** Running a 2B model on a CPU requires sufficient memory. Actual resource usage and inference latency depend on the machine and runtime configuration.

## Running OpsPilot AI

### Run without Amazon Bedrock

The following command executes the decision and diagnostic workflow without making a Bedrock inference call:

```bash
python -m app.main \
  --problem "The Kubernetes pod is in CrashLoopBackOff, has restarted six times, and exited with code 1. Determine the most useful diagnostic action to investigate the cause." \
  --pod payments-api-demo \
  --namespace production \
  --skip-explanation
```

The application returns information such as:

- Original problem description.
- Pod name and namespace.
- Selected diagnostic action.
- Decision probabilities.
- Decision confidence.
- Decision latency.
- Diagnostic evidence.
- Optional explanation field.

The selected action and probabilities may vary between runs because model decisions can be stochastic.

### Example output

The following is a recorded example from a successful run using Strands Decider 2B. It matches the example stored in `artifacts/decider-demo-output.json`.

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

This example demonstrates that the Decider selected `container_logs` and the diagnostic function returned simulated evidence indicating that the `DATABASE_URL` environment variable was missing.

**Interpreting the decision:** The selected tool had a probability of approximately 66.29%. The recorded confidence value was 0.4944. Neither value guarantees that the selected action is correct.

The recorded latency of 4599.57 milliseconds is from one run and is not a performance guarantee.

## Available Diagnostic Tools

OpsPilot currently supports three simulated diagnostic actions.

### 1. Pod Status

The pod-status diagnostic returns example information about the pod state, restart count, and last exit code.

Example evidence:

```text
Pod status: CrashLoopBackOff
Restart count: 6
Last exit code: 1
```

### 2. Container Logs

The container-log diagnostic returns example application log output.

Example evidence:

```text
ERROR: Required environment variable DATABASE_URL is missing.
Application startup failed.
```

This evidence suggests that the application may be failing during startup because a required environment variable is absent.

### 3. Kubernetes Events

The Kubernetes-event diagnostic returns simulated event information associated with the pod.

Example evidence:

```text
Warning BackOff
Container restart back-off observed.
```

These functions are demonstrations. They do not retrieve live pod status, container logs, or Kubernetes events.

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

Ensure that the selected inference profile is available to your AWS account and that the execution identity has the required Bedrock permissions.

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

- Verify the model and inference-profile availability.
- Verify the required IAM permissions.
- Review the applicable AWS pricing.
- Use appropriate AWS budget and cost controls.

**Bedrock status:** The explanation component is implemented, but a successful real Bedrock inference has not yet been verified as part of the demonstrated project run.

To avoid a Bedrock inference call, use the `--skip-explanation` option when running the CLI.

## Testing

OpsPilot includes automated tests for the agent, diagnostic functions, and explanation component.

Run the tests from the project root:

```bash
source .venv/bin/activate
python -m pytest -q tests/
```

### Recorded test result

```text
11 passed
```

The project tests passed in the existing development environment.

Passing these tests does not establish that live Kubernetes integration, real Amazon Bedrock inference, or a fresh-environment installation has been verified.

## Evidence and Artifacts

The `artifacts/` directory contains example outputs generated during development.

| File | Description |
|---|---|
| `decider-demo-output.json` | Example decision and diagnostic output |
| `decider-health.json` | Recorded Decider server health information |
| `test-results.txt` | Recorded automated test result |

These artifacts support the demonstration and help reviewers understand the behavior of the application.

They are records from a development environment, not a guarantee that every future run will produce the same result.

## Safety and Limitations

OpsPilot is a demonstration project with explicit limitations.

- **Simulated diagnostics:** Diagnostic tools return predefined example evidence rather than querying a live Kubernetes cluster.
- **No cluster modifications:** The application does not create, update, or delete Kubernetes resources.
- **Decision validation:** The application validates the selected diagnostic action before executing it.
- **Model uncertainty:** A selected action and its probability do not guarantee a correct diagnosis.
- **Optional Bedrock inference:** Real explanations require suitable AWS configuration and may incur charges.
- **No production-readiness claim:** Live Kubernetes access, authentication, authorization, operational monitoring, and production security controls have not been established by this demonstration.

Do not use simulated diagnostic results as evidence about a real production workload.

## Future Improvements

Potential future enhancements include:

- Integrating read-only Kubernetes API diagnostics.
- Collecting real pod status, container logs, and events.
- Adding further validation and error-handling tests.
- Verifying real Amazon Bedrock explanations.
- Adding structured incident summaries and recommended next steps.
- Improving observability, latency measurement, and failure reporting.
- Adding production-grade authentication, authorization, and audit logging before real cluster integration.

These are proposed enhancements, not completed features.

## Third-Party Attribution

OpsPilot uses Strands Decider 2B and adapts the upstream example client implementation.

**Upstream repository:**
https://github.com/strands-labs/strands-decider

The upstream project is licensed under Apache License 2.0. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and [`licenses/Apache-2.0.txt`](licenses/Apache-2.0.txt) for the included attribution and license information.

## License

OpsPilot AI's original project code is distributed under the MIT License. See [`LICENSE`](LICENSE).

Third-party material remains subject to its applicable license and attribution requirements.
