"""Command-line interface for OpsPilot AI."""

import argparse
import json
import sys

from app.agent import troubleshoot
from app.decider_client import ServerUnavailable


def main():
    parser = argparse.ArgumentParser(
        description="OpsPilot AI - Kubernetes Troubleshooting Agent"
    )
    parser.add_argument(
        "--problem",
        required=True,
        help="Describe the Kubernetes problem.",
    )
    parser.add_argument(
        "--pod",
        default="demo-app",
        help="Pod name (default: demo-app).",
    )
    parser.add_argument(
        "--namespace",
        default="default",
        help="Kubernetes namespace (default: default).",
    )
    parser.add_argument(
        "--skip-explanation",
        action="store_true",
        help="Skip the Amazon Bedrock explanation step.",
    )

    args = parser.parse_args()

    try:
        result = troubleshoot(
            problem=args.problem,
            pod_name=args.pod,
            namespace=args.namespace,
            explain=not args.skip_explanation,
        )
        print(json.dumps(result, indent=2, default=str))

    except ServerUnavailable as exc:
        print(f"Strands Decider is unavailable: {exc}", file=sys.stderr)
        sys.exit(1)

    except Exception as exc:
        print(f"Troubleshooting failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
