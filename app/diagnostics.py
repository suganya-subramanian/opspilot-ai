"""Safe diagnostic tools for OpsPilot AI.

Initial version uses simulated Kubernetes data.
No real cluster is accessed or modified.
"""

from strands import tool


@tool
def get_pod_status(pod_name: str, namespace: str = "default") -> str:
    """Get the status and restart count of a Kubernetes pod.

    Args:
        pod_name: Name of the Kubernetes pod.
        namespace: Kubernetes namespace.
    """
    return (
        f"Pod: {pod_name}\n"
        f"Namespace: {namespace}\n"
        "Status: CrashLoopBackOff\n"
        "Container state: Waiting\n"
        "Restart count: 6\n"
        "Last termination reason: Error\n"
        "Last exit code: 1"
    )


@tool
def get_container_logs(pod_name: str, namespace: str = "default") -> str:
    """Get recent logs from a Kubernetes container.

    Args:
        pod_name: Name of the Kubernetes pod.
        namespace: Kubernetes namespace.
    """
    return (
        f"Pod: {pod_name}\n"
        f"Namespace: {namespace}\n"
        "Simulated container log:\n"
        "ERROR: Required environment variable DATABASE_URL is missing.\n"
        "Application startup failed."
    )


@tool
def get_pod_events(pod_name: str, namespace: str = "default") -> str:
    """Get recent Kubernetes events associated with a pod.

    Args:
        pod_name: Name of the Kubernetes pod.
        namespace: Kubernetes namespace.
    """
    return (
        f"Pod: {pod_name}\n"
        f"Namespace: {namespace}\n"
        "Simulated event:\n"
        "Warning BackOff: Back-off restarting failed container."
    )
