import pytest

from app.services.decision_audit import build_decision_audit
from app.services.investment_policy import evaluate_candidate


def sample_decision():
    return evaluate_candidate(
        domain="Audit.Example.",
        estimated_resale_value=500,
        sale_probability=0.8,
        acquisition_cost=50,
        additional_fees=5,
        annual_renewal_cost=15,
        holding_years=1,
        evidence_confidence=0.9,
        trademark_risk="low",
    )


def test_decision_audit_is_stable_and_normalizes_domain():
    decision = sample_decision()
    evidence = [
        {
            "provider": "manual-comparable-sales",
            "locator": "spreadsheet:row-12",
            "retrieved_at": "2026-10-09T08:00:00Z",
            "data_fingerprint": "sample-sha256:abc123",
        }
    ]

    first = build_decision_audit(decision, evidence_sources=evidence)
    second = build_decision_audit(decision, evidence_sources=evidence)

    assert first == second
    assert first["domain"] == "audit.example"
    assert first["paper_trading_only"] is True
    assert first["purchase_executed"] is False
    assert len(first["audit_id"]) == 64
    assert first["hash_algorithm"] == "sha256"
    assert first["evidence_sources"] == evidence


def test_decision_audit_hash_changes_when_evidence_changes():
    decision = sample_decision()
    first = build_decision_audit(
        decision,
        evidence_sources=[{"provider": "source-a", "locator": "record-1"}],
    )
    second = build_decision_audit(
        decision,
        evidence_sources=[{"provider": "source-a", "locator": "record-2"}],
    )

    assert first["audit_id"] != second["audit_id"]


def test_decision_audit_requires_decision_fields_and_evidence_provenance():
    with pytest.raises(ValueError, match="missing required fields"):
        build_decision_audit({"domain": "example.com"})

    with pytest.raises(ValueError, match="provider"):
        build_decision_audit(sample_decision(), evidence_sources=[{"locator": "record-1"}])

    with pytest.raises(ValueError, match="locator or reference"):
        build_decision_audit(sample_decision(), evidence_sources=[{"provider": "source-a"}])
