"""Claim signal derivation from GitHub installation context.

Derives Exchange claim signals (ownership, trust) from GitHub
webhook payloads and API data.
"""


def derive_claim_from_installation(payload: dict, event: str) -> dict:
    """Derive a structured claim from an installation event payload.

    Returns a dict with claim signals, trust indicators, and evidence.
    """
    installation = payload.get("installation", {})
    install_id = installation.get("id", 0)
    sender = payload.get("sender", {})
    sender_login = sender.get("login", "")
    account = installation.get("account", {})
    account_type = account.get("type", "")  # "Organization" or "User"
    account_login = account.get("login", "")
    repos = []

    if event == "installation":
        for r in payload.get("repositories", []):
            repos.append(r.get("full_name", ""))
    elif event == "installation_repositories":
        for r in payload.get("repositories_added", []):
            repos.append(r.get("full_name", ""))

    is_org = account_type == "Organization"

    claim = {
        "installation_id": install_id,
        "installer": sender_login,
        "account_login": account_login,
        "account_type": account_type,
        "repositories": repos,
        "claim_signals": [],
        "trust_indicators": [],
        "evidence": [],
    }

    # Signal: ownership through installation context
    claim["claim_signals"].append({
        "type": "installation_ownership",
        "strength": "strong" if is_org else "moderate",
        "description": f"Installation by {sender_login} on {account_login} ({account_type})",
    })

    # Signal: org-level installation is stronger than user-level
    if is_org:
        claim["claim_signals"].append({
            "type": "org_installation",
            "strength": "strong",
            "description": f"Organization {account_login} installed the app",
        })
        claim["trust_indicators"].append({
            "type": "org_ownership",
            "confidence": "high",
            "description": f"Org-level installation implies {account_login} controls listed repos",
        })
    else:
        claim["trust_indicators"].append({
            "type": "user_ownership",
            "confidence": "moderate",
            "description": f"User-level installation by {sender_login}",
        })

    # Evidence: sender + account metadata
    claim["evidence"].append({
        "source": "github_installation",
        "install_id": install_id,
        "sender": sender_login,
        "account": account_login,
        "account_type": account_type,
        "repository_count": len(repos),
    })

    return claim


def enrich_claim_with_org_domain(claim: dict, verified_domain: str | None) -> dict:
    """Enrich a claim with verified org domain information.

    A verified domain on the GitHub org account strengthens trust.
    Maps to Exchange TrustState: verified_domain → 'verified'.
    """
    if verified_domain:
        claim["trust_indicators"].append({
            "type": "verified_domain",
            "confidence": "high",
            "description": f"Organization has verified domain: {verified_domain}",
        })
        claim["evidence"].append({
            "source": "github_org_domain",
            "domain": verified_domain,
            "verified": True,
        })
    return claim


def enrich_claim_with_attestations(claim: dict, attestations: list) -> dict:
    """Enrich a claim with artifact attestation information.

    GitHub Artifact Attestations provide cryptographic proof of
    provenance. Maps to Exchange TrustState: attested → 'audited'.
    """
    if attestations:
        claim["trust_indicators"].append({
            "type": "artifact_attestations",
            "confidence": "very_high",
            "description": f"{len(attestations)} artifact attestations detected",
        })
        for att in attestations:
            claim["evidence"].append({
                "source": "artifact_attestation",
                "attestation_id": att.get("id", ""),
                "subject": att.get("subject", ""),
                "signer": att.get("signer", ""),
            })
    return claim
