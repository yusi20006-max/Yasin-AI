"""Minimal OpenAI-compatible HTTP transport for the Yasin-AI service boundary."""
from __future__ import annotations

import json
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from yasinai.contracts.base import ContractViolationError
from yasinai.contracts.generation import GenerationRequest, GenerationResult
from yasinai.providers.base import ProviderCapability
from yasinai.services.generation_service import GenerationService
from yasinai.gateway.token_validation import TokenValidationBridge
from yasinai.gateway.token_import import TokenImportBridge
from yasinai.services.credential_registry import CredentialRegistry

logger = logging.getLogger(__name__)
MAX_BODY_BYTES = 1_048_576


class YasinAIGateway:
    """HTTP adapter that delegates generation to ``GenerationService``."""

    def __init__(self, generation_service: GenerationService | None = None) -> None:
        self.generation_service = generation_service or GenerationService()

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "service": "yasin-ai"}

    def models(self) -> dict[str, Any]:
        data: list[dict[str, Any]] = []
        for provider in self.generation_service.registry.available_for_capability(ProviderCapability.GENERATION):
            for model in provider.info.model_ids:
                data.append({"id": model, "object": "model", "owned_by": provider.info.name})
        return {"object": "list", "data": data}

    def chat_completions(self, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        messages = payload.get("messages")
        if not isinstance(messages, list) or not messages:
            return 400, {"error": {"message": "messages must be a non-empty list", "type": "invalid_request_error"}}
        prompt_parts: list[str] = []
        system_prompt: str | None = None
        for message in messages:
            if not isinstance(message, dict) or message.get("role") not in {"system", "user", "assistant"}:
                return 400, {"error": {"message": "invalid message", "type": "invalid_request_error"}}
            content = message.get("content", "")
            if not isinstance(content, str):
                return 400, {"error": {"message": "message content must be a string", "type": "invalid_request_error"}}
            if message["role"] == "system":
                system_prompt = content
            else:
                prompt_parts.append(content)
        prompt = "\n".join(prompt_parts).strip()
        if not prompt:
            return 400, {"error": {"message": "at least one non-system message is required", "type": "invalid_request_error"}}
        try:
            request = GenerationRequest(
                prompt=prompt,
                model=payload.get("model"),
                max_tokens=payload.get("max_tokens", 1024),
                temperature=payload.get("temperature", 0.7),
                system_prompt=system_prompt,
                stop_sequences=payload.get("stop", []) or [],
                provider=payload.get("provider"),
            )
        except (TypeError, ValueError, ContractViolationError) as exc:
            return 400, {"error": {"message": str(exc), "type": "invalid_request_error"}}
        result = self.generation_service.generate(request)
        if not result.success:
            return 503, {"error": {"message": result.error or "generation failed", "type": "provider_error"}}
        return 200, self._result_payload(result)

    @staticmethod
    def _result_payload(result: GenerationResult) -> dict[str, Any]:
        return {
            "id": "yasinai-chat-completion",
            "object": "chat.completion",
            "model": result.model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": result.text}, "finish_reason": result.finish_reason or "stop"}],
            "usage": {"prompt_tokens": result.input_tokens, "completion_tokens": result.output_tokens, "total_tokens": result.input_tokens + result.output_tokens},
        }


def create_server(gateway: YasinAIGateway | None = None, *, host: str | None = None, port: int | None = None, token_bridge: TokenValidationBridge | None = None) -> ThreadingHTTPServer:
    gateway = gateway or YasinAIGateway()
    if token_bridge is None and os.environ.get("YASINAI_BRIDGE_TOKEN"):
        token_bridge = TokenValidationBridge()
    import_bridge = TokenImportBridge(validation_bridge=token_bridge, registry=CredentialRegistry()) if token_bridge else None
    bind_host = host or os.environ.get("YASINAI_GATEWAY_HOST", "127.0.0.1")
    bind_port = port if port is not None else int(os.environ.get("YASINAI_GATEWAY_PORT", "8000"))

    class Handler(BaseHTTPRequestHandler):
        server_version = "YasinAI/1"

        def _write(self, status: int, payload: dict[str, Any]) -> None:
            data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self._cors()
            self.end_headers()
            self.wfile.write(data)

        def _cors(self) -> None:
            origin = self.headers.get("Origin")
            if token_bridge and origin == token_bridge.allowed_origin:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, X-YasinAI-Bridge-Token")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

        def do_OPTIONS(self) -> None:
            if not token_bridge or self.headers.get("Origin") != token_bridge.allowed_origin:
                self._write(403, {"error": {"message": "origin not allowed", "type": "forbidden"}})
                return
            self.send_response(204); self._cors(); self.end_headers()

        def do_GET(self) -> None:
            if self.path == "/v1/token/credentials":
                if not import_bridge or not token_bridge or not token_bridge.authorize(dict(self.headers), self.headers.get("Origin")):
                    self._write(403, {"error": {"message": "bridge authorization failed", "type": "forbidden"}}); return
                self._write(200, {"credentials": import_bridge.registry.list_public()})
            elif self.path == "/health":
                self._write(200, gateway.health())
            elif self.path == "/v1/models":
                self._write(200, gateway.models())
            else:
                self._write(404, {"error": {"message": "not found", "type": "not_found"}})

        def do_POST(self) -> None:
            if self.path == "/v1/token/import":
                if not import_bridge or not token_bridge or not token_bridge.authorize(dict(self.headers), self.headers.get("Origin")):
                    self._write(403, {"error": {"message": "bridge authorization failed", "type": "forbidden"}}); return
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if length <= 0 or length > MAX_BODY_BYTES:
                        self._write(413, {"error": {"message": "request body too large or empty", "type": "invalid_request_error"}}); return
                    payload = json.loads(self.rfile.read(length))
                    status, response = import_bridge.import_credential(payload) if isinstance(payload, dict) else (400, {"error": {"message": "JSON body must be an object", "type": "invalid_request_error"}})
                except (ValueError, TypeError, OSError, json.JSONDecodeError):
                    status, response = 400, {"error": {"message": "invalid import request", "type": "invalid_request_error"}}
                self._write(status, response); return
            if self.path == "/v1/token/validate":
                if not token_bridge or not token_bridge.authorize(dict(self.headers), self.headers.get("Origin")):
                    self._write(403, {"error": {"message": "bridge authorization failed", "type": "forbidden"}}); return
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    if length <= 0 or length > MAX_BODY_BYTES:
                        self._write(413, {"error": {"message": "request body too large or empty", "type": "invalid_request_error"}}); return
                    payload = json.loads(self.rfile.read(length))
                    status,response=(200, token_bridge.validate(payload)) if isinstance(payload, dict) else (400, {"error":{"message":"JSON body must be an object","type":"invalid_request_error"}})
                except Exception:
                    status,response=400,{"error":{"message":"invalid validation request","type":"invalid_request_error"}}
                self._write(status,response); return
            if self.path != "/v1/chat/completions":
                self._write(404, {"error": {"message": "not found", "type": "not_found"}})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._write(400, {"error": {"message": "invalid content length", "type": "invalid_request_error"}})
                return
            if length <= 0 or length > MAX_BODY_BYTES:
                self._write(413, {"error": {"message": "request body too large or empty", "type": "invalid_request_error"}})
                return
            try:
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("JSON body must be an object")
                status, response = gateway.chat_completions(payload)
            except (json.JSONDecodeError, ValueError):
                status, response = 400, {"error": {"message": "invalid JSON body", "type": "invalid_request_error"}}
            except Exception:
                logger.exception("HTTP gateway request failed")
                status, response = 500, {"error": {"message": "internal server error", "type": "internal_error"}}
            self._write(status, response)

        def log_message(self, fmt: str, *args: Any) -> None:
            logger.info("HTTP %s", fmt % args)

    return ThreadingHTTPServer((bind_host, bind_port), Handler)


def serve() -> None:
    server = create_server()
    logger.info("Yasin-AI gateway listening on %s:%s", *server.server_address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    serve()
