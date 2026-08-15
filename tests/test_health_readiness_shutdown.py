"""#150 — health/readiness and graceful shutdown."""
from __future__ import annotations

from yasinai.core.runtime import Runtime
from yasinai.deployment.health_check import HealthCheck


def test_runtime_not_ready_before_start():
    rt = Runtime(config_defaults={"modules": []})
    assert rt.is_ready() is False
    snap = rt.readiness()
    assert snap["status"] == "not_ready"


def test_runtime_ready_after_start_and_shutdown_releases():
    rt = Runtime(config_defaults={"modules": []})
    rt.start()
    assert rt.is_ready() is True
    assert rt.readiness()["status"] == "ready"
    assert "runtime" in rt.readiness()["services"]
    rt.shutdown()
    assert rt.is_ready() is False
    assert rt.state == Runtime.STOPPED
    assert rt.services.list_services() == {}
    # idempotent
    rt.shutdown()
    assert rt.state == Runtime.STOPPED


def test_deployment_health_check_runs():
    report = HealthCheck().run_all_checks()
    assert "status" in report
    assert report["status"] in {"HEALTHY", "DEGRADED"}
    assert "platforms" in report
