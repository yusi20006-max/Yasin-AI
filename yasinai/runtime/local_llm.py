"""Managed local llama-server lifecycle for GGUF inference runtimes.

The runtime manager owns only the external process lifecycle. Provider
implementations remain responsible for inference requests.
"""
from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


class LocalLLMRuntimeError(RuntimeError):
    """Raised for safe, operator-facing local runtime failures."""


@dataclass(frozen=True)
class LocalLLMRuntimeConfig:
    executable: str = "llama-server"
    model: str = ""
    host: str = "127.0.0.1"
    port: int = 18765
    context_size: int = 8192
    threads: int = 4
    startup_timeout: float = 30.0
    poll_interval: float = 0.25
    state_file: Path = Path("~/.config/yasinai/local-llm-runtime.json")
    extra_args: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError("model must be configured")
        if not (1 <= self.port <= 65535):
            raise ValueError("port must be between 1 and 65535")
        if self.context_size < 1 or self.threads < 1:
            raise ValueError("context_size and threads must be positive")
        if self.startup_timeout <= 0 or self.poll_interval <= 0:
            raise ValueError("startup_timeout and poll_interval must be positive")

    @property
    def resolved_state_file(self) -> Path:
        return self.state_file.expanduser()

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


@dataclass(frozen=True)
class LocalLLMRuntimeStatus:
    state: str
    pid: int | None
    port: int
    endpoint: str
    detail: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "state": self.state,
            "pid": self.pid,
            "port": self.port,
            "endpoint": self.endpoint,
            "detail": self.detail,
        }


class LocalLLMRuntime:
    """Safely start and manage one owned llama-server instance."""

    STOPPED = "STOPPED"
    STARTING = "STARTING"
    READY = "READY"
    FAILED = "FAILED"

    def __init__(self, config: LocalLLMRuntimeConfig) -> None:
        self.config = config
        self._process: subprocess.Popen[bytes] | None = None

    def _read_state(self) -> dict[str, object] | None:
        path = self.config.resolved_state_file
        if not path.exists():
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return value if isinstance(value, dict) else None

    def _write_state(self, pid: int, starttime: str) -> None:
        path = self.config.resolved_state_file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "pid": pid,
                    "starttime": starttime,
                    "port": self.config.port,
                    "host": self.config.host,
                    "executable": self.config.executable,
                    "model": self.config.model,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass

    def _clear_state(self) -> None:
        try:
            self.config.resolved_state_file.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            pass

    @staticmethod
    def _proc_starttime(pid: int) -> str | None:
        try:
            fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()
            return fields[21]
        except (OSError, IndexError, ValueError):
            return None

    @staticmethod
    def _proc_cmdline(pid: int) -> list[str] | None:
        try:
            raw = Path(f"/proc/{pid}/cmdline").read_bytes()
        except OSError:
            return None
        return [part.decode(errors="replace") for part in raw.split(b"\0") if part]

    def _owned_pid(self) -> int | None:
        state = self._read_state()
        if not state:
            return None
        try:
            pid = int(state["pid"])
        except (KeyError, TypeError, ValueError):
            self._clear_state()
            return None
        starttime = self._proc_starttime(pid)
        cmdline = self._proc_cmdline(pid)
        if starttime is None or cmdline is None:
            self._clear_state()
            return None
        if str(state.get("starttime")) != starttime:
            self._clear_state()
            return None
        executable_name = Path(self.config.executable).name
        if not any(Path(arg).name == executable_name for arg in cmdline):
            return None
        if "--port" not in cmdline:
            return None
        try:
            port_index = cmdline.index("--port")
            if int(cmdline[port_index + 1]) != self.config.port:
                return None
        except (ValueError, IndexError):
            return None
        return pid

    def _port_free(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((self.config.host, self.config.port))
            except OSError:
                return False
        return True

    def _health_url(self, path: str = "/health") -> str:
        return f"{self.config.base_url}{path}"

    def health(self) -> bool:
        """Return True only when llama-server reports a healthy endpoint."""
        for path in ("/health", "/v1/models"):
            try:
                with urllib.request.urlopen(self._health_url(path), timeout=2) as response:
                    if 200 <= response.status < 300:
                        return True
            except (urllib.error.URLError, TimeoutError, OSError):
                continue
        return False

    def status(self) -> LocalLLMRuntimeStatus:
        pid = self._owned_pid()
        if pid is None:
            return LocalLLMRuntimeStatus(self.STOPPED, None, self.config.port, self.config.base_url)
        if self.health():
            return LocalLLMRuntimeStatus(self.READY, pid, self.config.port, self.config.base_url)
        return LocalLLMRuntimeStatus(self.STARTING, pid, self.config.port, self.config.base_url)

    def start(self) -> LocalLLMRuntimeStatus:
        current = self.status()
        if current.state == self.READY:
            return current
        if current.pid is not None:
            raise LocalLLMRuntimeError("A managed llama-server process exists but is not ready")
        if not self._port_free():
            raise LocalLLMRuntimeError(f"Port {self.config.port} is already occupied by another process")
        if not Path(self.config.model).expanduser().is_file():
            raise LocalLLMRuntimeError("Configured GGUF model does not exist")

        command: list[str] = [
            self.config.executable,
            "-m",
            str(Path(self.config.model).expanduser()),
            "-t",
            str(self.config.threads),
            "-c",
            str(self.config.context_size),
            "--host",
            self.config.host,
            "--port",
            str(self.config.port),
            *self.config.extra_args,
        ]
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except (OSError, ValueError) as exc:
            raise LocalLLMRuntimeError("Unable to start llama-server") from exc

        self._process = process
        starttime = self._proc_starttime(process.pid) or "unknown"
        self._write_state(process.pid, starttime)
        deadline = time.monotonic() + self.config.startup_timeout
        while time.monotonic() < deadline:
            if process.poll() is not None:
                self._clear_state()
                raise LocalLLMRuntimeError("llama-server exited before becoming ready")
            if self.health():
                return LocalLLMRuntimeStatus(self.READY, process.pid, self.config.port, self.config.base_url)
            time.sleep(self.config.poll_interval)

        self._terminate_process(process)
        self._clear_state()
        raise LocalLLMRuntimeError("llama-server did not become ready before timeout")

    def stop(self) -> LocalLLMRuntimeStatus:
        pid = self._owned_pid()
        if pid is None:
            self._clear_state()
            self._process = None
            return LocalLLMRuntimeStatus(self.STOPPED, None, self.config.port, self.config.base_url)
        process = self._process if self._process is not None and self._process.pid == pid else None
        if process is None:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                self._clear_state()
                return LocalLLMRuntimeStatus(self.STOPPED, None, self.config.port, self.config.base_url)
            self._wait_pid_exit(pid)
        else:
            self._terminate_process(process)
        self._clear_state()
        self._process = None
        return LocalLLMRuntimeStatus(self.STOPPED, None, self.config.port, self.config.base_url)

    def restart(self) -> LocalLLMRuntimeStatus:
        self.stop()
        return self.start()

    def _wait_pid_exit(self, pid: int, timeout: float = 5.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._proc_starttime(pid) is None:
                return
            time.sleep(self.config.poll_interval)
        if self._proc_starttime(pid) is not None:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    @staticmethod
    def _terminate_process(process: subprocess.Popen[bytes]) -> None:
        if process.poll() is not None:
            return
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
