"""Batch token health checking with secret-free aggregate reporting."""
from __future__ import annotations
from collections import Counter
from typing import Any
from yasinai.services.token_health import TokenHealthEngine

class BatchHealthService:
    def __init__(self, validator_factory):
        self.validator_factory=validator_factory

    def check(self, tokens: list[dict[str, Any]]) -> dict[str, Any]:
        results=[]
        for item in tokens:
            provider=str(item.get("provider") or "").strip().lower()
            credential=item.get("credential")
            if not provider or not isinstance(credential,str) or not credential:
                results.append({"provider":provider or "unknown","state":"UNKNOWN","error_code":"INVALID_CREDENTIAL"})
                continue
            engine=TokenHealthEngine(self.validator_factory(provider).validate_credential)
            record=engine.check(credential)
            results.append({"provider":provider,"state":record.state.value,"error_code":record.validation.error_code})
        states=Counter(r["state"] for r in results)
        providers=Counter(r["provider"] for r in results)
        return {"total":len(results),"states":dict(states),"providers":dict(providers),"results":results}
