"""Repository discovery for Capacium GitHub App."""
import json
import urllib.request
import urllib.error


class RepoDiscovery:
    def __init__(self, exchange_api_url: str):
        self.exchange_api_url = exchange_api_url.rstrip("/")

    def scan_repo(self, repo_full_name: str, default_branch: str) -> dict:
        url = f"https://api.github.com/repos/{repo_full_name}/contents/capability.yaml?ref={default_branch}"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3.raw"})
        try:
            with urllib.request.urlopen(req) as resp:
                content = resp.read().decode()
                return {"has_capability": True, "content_preview": content[:200]}
        except urllib.error.HTTPError:
            return {"has_capability": False}

    def list_capability_repos(self, installation_repos: list) -> list:
        results = []
        for repo_full_name in installation_repos:
            result = self.scan_repo(repo_full_name, "main")
            if result.get("has_capability"):
                results.append({"repo": repo_full_name, "status": "capability_found"})
            else:
                result = self.scan_repo(repo_full_name, "master")
                if result.get("has_capability"):
                    results.append({"repo": repo_full_name, "status": "capability_found"})
                else:
                    results.append({"repo": repo_full_name, "status": "no_capability"})
        return results
