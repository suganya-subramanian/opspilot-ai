import io
import json

from app import explainer


class FakeBedrockClient:
    def invoke_model(self, **kwargs):
        assert kwargs["modelId"] == explainer.BEDROCK_MODEL_ID
        assert kwargs["contentType"] == "application/json"

        request = json.loads(kwargs["body"])
        prompt = request["messages"][0]["content"][0]["text"]

        assert "CrashLoopBackOff" in prompt
        assert "DATABASE_URL" in prompt

        return {
            "body": io.BytesIO(
                json.dumps(
                    {
                        "output": {
                            "message": {
                                "content": [
                                    {
                                        "text": (
                                            "Root cause: DATABASE_URL is missing."
                                        )
                                    }
                                ]
                            }
                        }
                    }
                ).encode()
            )
        }


def test_generate_explanation_uses_bedrock_response(monkeypatch):
    monkeypatch.setattr(
        explainer.boto3,
        "client",
        lambda *args, **kwargs: FakeBedrockClient(),
    )

    result = explainer.generate_explanation(
        problem="demo-app is in CrashLoopBackOff",
        diagnostic_evidence=(
            "Container log: DATABASE_URL is missing."
        ),
    )

    assert result["explanation"] == (
        "Root cause: DATABASE_URL is missing."
    )
    assert result["region"] == "ap-south-1"
    assert result["model_id"] == "apac.amazon.nova-micro-v1:0"
