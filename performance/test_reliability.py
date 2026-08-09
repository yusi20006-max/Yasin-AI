"""Fast regression tests for Phase 14 reliability contracts."""
from __future__ import annotations

import threading

from observability.metrics import MetricsRegistry, timed


def test_metrics_registry_is_thread_safe() -> None:
    registry = MetricsRegistry()
    counter = registry.counter("requests")

    def worker() -> None:
        for _ in range(100):
            counter.inc()

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert counter.value == 800


def test_timed_preserves_callable_metadata_and_records_exception() -> None:
    registry = MetricsRegistry()

    @timed(registry, "operation")
    def operation() -> str:
        """Stable callable contract."""
        return "ok"

    assert operation.__name__ == "operation"
    assert operation.__doc__ == "Stable callable contract."
    assert operation() == "ok"

    snapshot = registry.snapshot()
    assert snapshot["timers"]["operation"]["count"] == 1
    assert snapshot["timers"]["operation"]["total_seconds"] >= 0


def test_timed_records_failed_operation() -> None:
    registry = MetricsRegistry()

    @timed(registry, "failed")
    def failed() -> None:
        raise RuntimeError("boom")

    try:
        failed()
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected RuntimeError")

    assert registry.snapshot()["timers"]["failed"]["count"] == 1
