"""Generate Kubernetes troubleshooting explanations with Amazon Bedrock."""

import json
import os

import boto3


AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "apac.amazon.nova-micro-v1:0",
)


def generate_explanation(problem: str, diagnostic_evidence: str) -> dict:
    """Explain a Kubernetes problem using diagnostic evidence.

    This function calls Bedrock only when explicitly invoked.
    """

    prompt = f"""
You are OpsPilot AI, a Kubernetes troubleshooting assistant.

Analyze the Kubernetes problem using only the evidence provided.

KUBERNETES PROBLEM:
{problem}

DIAGNOSTIC EVIDENCE:
{diagnostic_evidence}

Provide:
1. Likely root cause.
2. Evidence supporting the diagnosis.
3. Recommended recovery steps.
4. Verification steps after recovery.
5. Any uncertainty or missing information.

Safety requirements:
- Do not claim that a suggested fix has been executed.
- Do not invent diagnostic evidence.
- Do not recommend deleting production resources as a first response.
- Prefer safe, reversible recovery steps.
- Clearly identify commands that require human approval.

Return a concise, practical troubleshooting report.
"""

    client = boto3.client(
        "bedrock-runtime",
        region_name=AWS_REGION,
    )

    response = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(
            {
                "schemaVersion": "messages-v1",
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}],
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 250,
                    "temperature": 0.2,
                },
            }
        ),
        contentType="application/json",
        accept="application/json",
    )

    result = json.loads(response["body"].read())
    explanation = result["output"]["message"]["content"][0]["text"]

    return {
        "model_id": BEDROCK_MODEL_ID,
        "region": AWS_REGION,
        "explanation": explanation,
    }
