"""Deterministic, tamper-evident decision snapshots for audit and replay.

This module is intentionally storage-agnostic: callers can persist the returned
record in a database later. It performs no network, database, or trading actions.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def build_decision_audit(
    decision: Mapping[str, Any],
    *,
    evidence_sources: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Return a stable audit snapshot with provenance and a SHA-256 content ID.

    Each evidence source should identify at least a provider/source and a locator
    or reference. Optional fields such as retrieved_at, query, and data_fingerprint
    let a future persisted record explain what information supported the decision.
    The hash covers the full decision snapshot and evidence list.
    """
    required = {"domain", "recommendation", "inputs", "financials", "policy", "reasons"}
    missing = required.difference(decision)
    if missing:
        raise ValueError(f"decision is missing required fields: {', '.join(sorted(missing))}")

    normalized_sources: list[dict[str, Any]] = []
    for index, source in enumerate(evidence_sources):
        item = dict(source)
        provider = item.get("provider")
        locator = item.get("locator") or item.get("reference")
        if not isinstance(provider, str) or not provider.strip():
            raise ValueError(f"evidence source {index} must include a non-empty provider")
        if not isinstance(locator, str) or not locator.strip():
            raise ValueError(f"evidence source {index} must include a locator or reference")
        normalized_sources.append(item)

    payload = {
        "schema_version": 1,
        "domain": str(decision["domain"]).strip().lower().rstrip("."),
        "recommendation": decision["recommendation"],
        "currency": decision.get("currency", "EUR"),
        "paper_trading_only": True,
        "purchase_executed": False,
        "inputs": dict(decision["inputs"]),
        "financials": dict(decision["financials"]),
        "policy": dict(decision["policy"]),
        "reasons": list(decision["reasons"]),
        "evidence_sources": normalized_sources,
    }
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return {**payload, "audit_id": digest, "hash_algorithm": "sha256"}
