import pytest

from observability import MetricsRegistry, timed


def test_counter_and_timer_snapshot():
    registry = MetricsRegistry()
    assert registry.counter("requests").inc() == 1
    assert registry.counter("requests").inc(2) == 3
    registry.timer("latency").observe(0.25)
    snapshot = registry.snapshot()
    assert snapshot["counters"]["requests"] == 3
    assert snapshot["timers"]["latency"]["count"] == 1
    assert snapshot["timers"]["latency"]["total_seconds"] == pytest.approx(0.25)


def test_rejects_invalid_observations():
    registry = MetricsRegistry()
    with pytest.raises(ValueError):
        registry.counter("requests").inc(-1)
    with pytest.raises(ValueError):
        registry.timer("latency").observe(-0.1)


def test_timed_records_success_and_failure():
    registry = MetricsRegistry()

    @timed(registry, "work")
    def work(value):
        return value

    assert work(42) == 42
    assert registry.timer("work").count == 1

    @timed(registry, "failure")
    def fail():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        fail()
    assert registry.timer("failure").count == 1
