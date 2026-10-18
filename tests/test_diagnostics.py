from app.diagnostics import (
    get_pod_status,
    get_container_logs,
    get_pod_events,
)


def test_pod_status_reports_crash_loop():
    result = get_pod_status("demo-app", "default")

    assert "CrashLoopBackOff" in result
    assert "Restart count: 6" in result
    assert "Last exit code: 1" in result


def test_container_logs_report_missing_database_url():
    result = get_container_logs("demo-app", "default")

    assert "DATABASE_URL is missing" in result
    assert "Application startup failed" in result


def test_pod_events_report_backoff():
    result = get_pod_events("demo-app", "default")

    assert "Warning BackOff" in result
    assert "demo-app" in result
