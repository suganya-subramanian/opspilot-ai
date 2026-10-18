"""Runnable example of the OpsPilot AI tool-selection pattern."""

import json

from app.decision import select_diagnostic_tool


def main() -> None:
    problem = (
        "The payments API pod is in CrashLoopBackOff, has restarted six times, "
        "and exited with code 1. Determine the most useful diagnostic action "
        "to investigate the cause."
    )

    result = select_diagnostic_tool(problem)

    print(
        json.dumps(
            {
                "pattern": "tool-selection",
                "problem": problem,
                "decision": result,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
