from __future__ import annotations

import os
import stat
import sys
import textwrap
import time
from pathlib import Path

import pytest

from yasinai.runtime.local_llm import (
    LocalLLMRuntime,
    LocalLLMRuntimeConfig,
    LocalLLMRuntimeError,
)


FAKE_SERVER = textwrap.dedent(
    '''
    import argparse
    from http.server import BaseHTTPRequestHandler, HTTPServer

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--host', default='127.0.0.1')
    args, _ = parser.parse_known_args()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ('/health', '/v1/models'):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *_args):
            pass

    HTTPServer((args.host, args.port), Handler).serve_forever()
    '''
).strip() + "\n"


def make_runtime(tmp_path: Path, *, port: int = 18765) -> LocalLLMRuntime:
    executable = tmp_path / "llama-server"
    executable.write_text(f"#!{sys.executable}\n{FAKE_SERVER}", encoding="utf-8")
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    model = tmp_path / "model.gguf"
    model.write_bytes(b"test-model")
    return LocalLLMRuntime(
        LocalLLMRuntimeConfig(
            executable=str(executable),
            model=str(model),
            port=port,
            startup_timeout=8,
            poll_interval=0.05,
            state_file=tmp_path / "runtime.json",
        )
    )


def test_start_health_status_and_stop(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)

    started = runtime.start()
    assert started.state == runtime.READY
    assert started.pid is not None
    assert runtime.health()
    assert runtime.status().pid == started.pid

    stopped = runtime.stop()
    assert stopped.state == runtime.STOPPED
    assert stopped.pid is None
    assert runtime.status().state == runtime.STOPPED


def test_start_is_idempotent_for_owned_ready_process(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    first = runtime.start()
    second = runtime.start()
    try:
        assert second.pid == first.pid
        assert second.state == runtime.READY
    finally:
        runtime.stop()


def test_restart_rotates_process(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    first = runtime.start()
    try:
        second = runtime.restart()
        assert second.state == runtime.READY
        assert second.pid is not None
        assert second.pid != first.pid
    finally:
        runtime.stop()


def test_missing_model_fails_without_starting_process(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    runtime.config.resolved_state_file.unlink(missing_ok=True)
    missing = tmp_path / "missing.gguf"
    runtime = LocalLLMRuntime(
        LocalLLMRuntimeConfig(
            executable=runtime.config.executable,
            model=str(missing),
            port=18766,
            state_file=tmp_path / "missing-state.json",
        )
    )
    with pytest.raises(LocalLLMRuntimeError, match="model does not exist"):
        runtime.start()
    assert runtime.status().pid is None


def test_occupied_port_is_reported_without_killing_other_process(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path, port=18767)
    other = __import__("socket").socket()
    other.bind(("127.0.0.1", 18767))
    try:
        other.listen(1)
        with pytest.raises(LocalLLMRuntimeError, match="already occupied"):
            runtime.start()
        assert other.fileno() >= 0
    finally:
        other.close()


def test_stale_state_does_not_kill_reused_unrelated_process(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path, port=18768)
    runtime.config.resolved_state_file.parent.mkdir(parents=True, exist_ok=True)
    runtime.config.resolved_state_file.write_text(
        '{"pid": 999999, "starttime": "1", "port": 18768, "host": "127.0.0.1", '
        f'"executable": "{runtime.config.executable}", "model": "{runtime.config.model}"}}\n',
        encoding="utf-8",
    )
    assert runtime.status().state == runtime.STOPPED
    assert not runtime.config.resolved_state_file.exists()
