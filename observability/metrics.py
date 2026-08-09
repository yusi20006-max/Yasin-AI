"""Dependency-free metrics primitives for YasinAI services."""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import wraps
from threading import Lock
from time import monotonic
from typing import Any, Callable, Dict


@dataclass
class Counter:
    name: str
    value: int = 0
    _lock: Lock = field(default_factory=Lock, repr=False)

    def inc(self, amount: int = 1) -> int:
        if amount < 0:
            raise ValueError("counter increment must be non-negative")
        with self._lock:
            self.value += amount
            return self.value


@dataclass
class Timer:
    name: str
    count: int = 0
    total_seconds: float = 0.0
    _lock: Lock = field(default_factory=Lock, repr=False)

    def observe(self, seconds: float) -> float:
        if seconds < 0:
            raise ValueError("duration must be non-negative")
        with self._lock:
            self.count += 1
            self.total_seconds += seconds
            return seconds

    @property
    def average_seconds(self) -> float:
        with self._lock:
            return self.total_seconds / self.count if self.count else 0.0


class MetricsRegistry:
    """Thread-safe in-process registry suitable for service adapters."""

    def __init__(self) -> None:
        self._counters: Dict[str, Counter] = {}
        self._timers: Dict[str, Timer] = {}
        self._lock = Lock()

    def counter(self, name: str) -> Counter:
        with self._lock:
            return self._counters.setdefault(name, Counter(name))

    def timer(self, name: str) -> Timer:
        with self._lock:
            return self._timers.setdefault(name, Timer(name))

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            counters = {k: v.value for k, v in self._counters.items()}
            timers = {
                k: {"count": v.count, "total_seconds": v.total_seconds, "average_seconds": v.average_seconds}
                for k, v in self._timers.items()
            }
        return {"counters": counters, "timers": timers}


def timed(registry: MetricsRegistry, name: str) -> Callable:
    """Record execution duration while preserving the wrapped callable metadata."""
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            started = monotonic()
            try:
                return fn(*args, **kwargs)
            finally:
                registry.timer(name).observe(monotonic() - started)
        return wrapped
    return decorator
