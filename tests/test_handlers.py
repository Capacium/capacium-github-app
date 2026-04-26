"""Tests for GitHub App webhook handlers."""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.handlers import handle_push, handle_release, handle_installation, detect_capability_yaml


def test_detect_capability_yaml():
    files = {"added": ["capability.yaml"], "modified": [], "removed": []}
    assert detect_capability_yaml(files) is True

    files = {"added": ["README.md"], "modified": ["src/main.py"], "removed": []}
    assert detect_capability_yaml(files) is False

    files = None
    assert detect_capability_yaml(files) is False


def test_handle_push_with_capability():
    payload = {
        "repository": {"full_name": "test-owner/test-repo"},
        "ref": "refs/heads/main",
        "commits": [{"added": ["capability.yaml"], "modified": [], "removed": []}],
    }
    result = handle_push(payload)
    assert result["status"] == "capability_detected"
    assert result["repo"] == "test-owner/test-repo"


def test_handle_push_without_capability():
    payload = {
        "repository": {"full_name": "test-owner/test-repo"},
        "ref": "refs/heads/main",
        "commits": [{"added": ["README.md"], "modified": [], "removed": []}],
    }
    result = handle_push(payload)
    assert result["status"] == "no_capability"


def test_handle_release_published():
    payload = {
        "repository": {"full_name": "test-owner/test-repo"},
        "release": {"tag_name": "v1.0.0"},
        "action": "published",
    }
    result = handle_release(payload)
    assert result["status"] == "release_detected"
    assert result["action"] == "sync_to_exchange"


def test_handle_release_not_published():
    payload = {
        "repository": {"full_name": "test-owner/test-repo"},
        "release": {"tag_name": "v1.0.0"},
        "action": "draft",
    }
    result = handle_release(payload)
    assert result["status"] == "ignored"


def test_handle_installation():
    payload = {
        "installation": {"id": 12345},
        "sender": {"login": "test-user"},
        "repositories": [{"full_name": "test-owner/test-repo"}],
    }
    result = handle_installation(payload, "installation")
    assert result["status"] == "registered"
    assert result["installation_id"] == 12345
    assert "test-owner/test-repo" in result["repositories"]


if __name__ == "__main__":
    test_detect_capability_yaml()
    test_handle_push_with_capability()
    test_handle_push_without_capability()
    test_handle_release_published()
    test_handle_release_not_published()
    test_handle_installation()
    print("All tests passed!")
