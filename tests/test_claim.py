"""Tests for claim signal derivation."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.claim import (
    derive_claim_from_installation,
    enrich_claim_with_org_domain,
    enrich_claim_with_attestations,
)


def test_user_installation():
    payload = {
        "installation": {"id": 100, "account": {"login": "alice", "type": "User"}},
        "sender": {"login": "alice"},
        "repositories": [{"full_name": "alice/my-repo"}],
    }
    claim = derive_claim_from_installation(payload, "installation")
    assert claim["installation_id"] == 100
    assert claim["installer"] == "alice"
    assert claim["account_type"] == "User"
    assert claim["repositories"] == ["alice/my-repo"]
    signals = {s["type"] for s in claim["claim_signals"]}
    assert "installation_ownership" in signals
    # User installation: moderate strength
    install_signal = [s for s in claim["claim_signals"] if s["type"] == "installation_ownership"][0]
    assert install_signal["strength"] == "moderate"


def test_org_installation():
    payload = {
        "installation": {"id": 200, "account": {"login": "MyOrg", "type": "Organization"}},
        "sender": {"login": "bob"},
        "repositories": [
            {"full_name": "MyOrg/repo-one"},
            {"full_name": "MyOrg/repo-two"},
        ],
    }
    claim = derive_claim_from_installation(payload, "installation")
    assert claim["account_type"] == "Organization"
    assert len(claim["repositories"]) == 2
    signals = {s["type"] for s in claim["claim_signals"]}
    assert "org_installation" in signals
    indicators = {i["type"] for i in claim["trust_indicators"]}
    assert "org_ownership" in indicators
    assert claim["claim_signals"][0]["strength"] == "strong"


def test_installation_repositories_event():
    payload = {
        "installation": {"id": 300, "account": {"login": "carol-corp", "type": "Organization"}},
        "sender": {"login": "carol"},
        "repositories_added": [{"full_name": "carol-corp/new-project"}],
    }
    claim = derive_claim_from_installation(payload, "installation_repositories")
    assert claim["repositories"] == ["carol-corp/new-project"]


def test_enrich_with_org_domain():
    claim = {
        "installation_id": 1,
        "claim_signals": [],
        "trust_indicators": [],
        "evidence": [],
    }
    result = enrich_claim_with_org_domain(claim, "example.com")
    indicators = {i["type"] for i in result["trust_indicators"]}
    assert "verified_domain" in indicators
    assert result["evidence"][0]["domain"] == "example.com"


def test_enrich_with_org_domain_none():
    claim = {
        "installation_id": 1,
        "claim_signals": [],
        "trust_indicators": [],
        "evidence": [],
    }
    result = enrich_claim_with_org_domain(claim, None)
    assert len(result["trust_indicators"]) == 0


def test_enrich_with_attestations():
    claim = {
        "installation_id": 1,
        "claim_signals": [],
        "trust_indicators": [],
        "evidence": [],
    }
    attestations = [
        {"id": "att-001", "subject": "capability.yaml", "signer": "MyOrg"},
    ]
    result = enrich_claim_with_attestations(claim, attestations)
    indicators = {i["type"] for i in result["trust_indicators"]}
    assert "artifact_attestations" in indicators
    assert result["evidence"][0]["attestation_id"] == "att-001"


def test_enrich_with_attestations_empty():
    claim = {
        "installation_id": 1,
        "claim_signals": [],
        "trust_indicators": [],
        "evidence": [],
    }
    result = enrich_claim_with_attestations(claim, [])
    assert len(result["trust_indicators"]) == 0


if __name__ == "__main__":
    test_user_installation()
    test_org_installation()
    test_installation_repositories_event()
    test_enrich_with_org_domain()
    test_enrich_with_org_domain_none()
    test_enrich_with_attestations()
    test_enrich_with_attestations_empty()
    print("All claim tests passed!")
