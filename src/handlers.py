"""Webhook event handlers for Capacium GitHub App."""
import json
import os


def detect_capability_yaml(files):
    """Check if any changed files include capability.yaml."""
    if not files:
        return False
    for f in (files.get("added", []) + files.get("modified", [])):
        if f.endswith(("capability.yaml", "capability.yml")):
            return True
    return False


def handle_push(payload):
    repo = payload.get("repository", {})
    repo_name = repo.get("full_name", "unknown")
    ref = payload.get("ref", "")
    branch = ref.replace("refs/heads/", "")

    commits = payload.get("commits", [])
    changed_files = {"added": [], "modified": [], "removed": []}
    for commit in commits:
        changed_files["added"].extend(commit.get("added", []))
        changed_files["modified"].extend(commit.get("modified", []))
        changed_files["removed"].extend(commit.get("removed", []))

    has_capability = detect_capability_yaml(changed_files)

    if has_capability:
        return {
            "status": "capability_detected",
            "repo": repo_name,
            "branch": branch,
            "fingerprint": None,
        }

    return {"status": "no_capability", "repo": repo_name, "branch": branch}


def handle_release(payload):
    repo = payload.get("repository", {})
    repo_name = repo.get("full_name", "unknown")
    release = payload.get("release", {})
    tag = release.get("tag_name", "")
    action = payload.get("action", "")

    if action != "published":
        return {"status": "ignored", "reason": f"action={action}"}

    return {
        "status": "release_detected",
        "repo": repo_name,
        "tag": tag,
        "action": "sync_to_exchange",
    }


def handle_installation(payload, event):
    installation = payload.get("installation", {})
    install_id = installation.get("id", 0)
    sender = payload.get("sender", {}).get("login", "")

    repos = []
    if event == "installation":
        for r in payload.get("repositories", []):
            repos.append(r.get("full_name", ""))
    elif event == "installation_repositories":
        for r in payload.get("repositories_added", []):
            repos.append(r.get("full_name", ""))

    return {
        "status": "registered",
        "installation_id": install_id,
        "sender": sender,
        "repositories": repos,
        "event": event,
    }
