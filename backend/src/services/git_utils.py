import subprocess
import os
import requests
import os
from urllib.parse import urlparse
from tree_sitter import Language
from typing import Dict,Any
from dotenv import load_dotenv
from pathlib import Path



env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_API_BASE = "https://api.github.com"

def extract_owner_repo(repo_url):
    parts = urlparse(repo_url).path.strip("/").split("/")
    if len(parts) >= 2:
        owner = parts[0]
        repo = parts[1].replace(".git", "")
        return owner, repo
    raise ValueError("Invalid GitHub URL format")

def get_repo_tree(owner, repo, branch):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    headers = {
        "Accept": "application/vnd.github+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["tree"]

def download_file(owner, repo, path, branch):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text


def get_file_git_info(owner: str, repo: str, branch: str, filepath: str) -> Dict[str, Any]:
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    params = {
        "path": filepath,
        "sha": branch,
        "per_page": 10  # limit recent commits fetched
    }

    headers = {
        "Accept": "application/vnd.github+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:

        print(f"GitHub API error: {response.status_code} {response.text}")
        return {
            "commit_count": 0,
            "last_modified": None,
            "recent_commits": []
        }

    commits = response.json()
    commit_count = len(commits)

    if commit_count == 0:
        return {
            "commit_count": 0,
            "last_modified": None,
            "recent_commits": []
        }

    recent_commits = []
    for c in commits:
        commit = c.get("commit", {})
        author = commit.get("author", {})
        recent_commits.append({
            "sha": c.get("sha"),
            "message": commit.get("message"),
            "author": author.get("name"),
            "date": author.get("date")
        })

    last_modified = recent_commits[0]["date"]

    # To get total commit count for the file, we might need to paginate or do a separate count
    # But GitHub API doesn't provide total count directly for file commits.
    # For now, we use the number of commits fetched or estimate from pagination headers.
    link_header = response.headers.get("Link")
    if link_header:
        import re
        match = re.search(r'&page=(\d+)>; rel="last"', link_header)
        if match:
            last_page_num = int(match.group(1))
            # commits per page is 10, so estimate total count
            commit_count = last_page_num * 10

    return {
        "commit_count": commit_count,
        "last_modified": last_modified,
        "recent_commits": recent_commits
    }


