import os
import requests
from urllib.parse import urlparse
from typing import Dict,Any
from dotenv import load_dotenv
from pathlib import Path
from collections import defaultdict
from datetime import datetime




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


def get_repo_git_analysis(repo: str, branch: str = "main") -> Dict[str, Any]:
    owner, repo = extract_owner_repo(repo)
    headers = {
        "Accept": "application/vnd.github+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    base_url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        # Repo metadata
        repo_resp = requests.get(base_url, headers=headers)
        repo_resp.raise_for_status()
        repo_data = repo_resp.json()

        # Contributors
        contrib_resp = requests.get(f"{base_url}/contributors", headers=headers, params={"per_page": 100})
        contrib_resp.raise_for_status()
        contributors = contrib_resp.json()

        # Commits (first + last)
        commits_resp = requests.get(f"{base_url}/commits", headers=headers, params={"sha": branch, "per_page": 100})
        commits_resp.raise_for_status()
        commit_data = commits_resp.json()

        total_commits = len(commit_data)
        all_commits = commit_data[:]

        # Paginate to get more commits (optional: GitHub allows up to 1000 with pagination)
        page = 2
        while len(commit_data) == 100 and page <= 10:
            more = requests.get(f"{base_url}/commits", headers=headers, params={"sha": branch, "per_page": 100, "page": page})
            if more.status_code != 200:
                break
            more_data = more.json()
            all_commits.extend(more_data)
            commit_data = more_data
            page += 1

        # Build commit statistics
        commit_activity = defaultdict(int)
        file_activity = defaultdict(int)
        author_stats = defaultdict(int)
        recent_commits = []

        for commit in all_commits:
            if "commit" not in commit:
                continue
            date_str = commit["commit"]["author"]["date"]
            date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").date()
            commit_activity[str(date)] += 1

            author = commit["commit"]["author"]["name"]
            author_stats[author] += 1

            sha = commit["sha"]
            # For top file activity: fetch files per commit (optional, costly)
            detail_url = f"{base_url}/commits/{sha}"
            detail = requests.get(detail_url, headers=headers)
            if detail.status_code == 200:
                files = detail.json().get("files", [])
                for f in files:
                    file_activity[f["filename"]] += 1

            if len(recent_commits) < 10:
                recent_commits.append({
                    "sha": sha,
                    "message": commit["commit"]["message"],
                    "author": author,
                    "date": date_str
                })

        return {
            "repo": repo,
            "owner": owner,
            "default_branch": repo_data.get("default_branch", "main"),
            "description": repo_data.get("description"),
            "total_commits_fetched": len(all_commits),
            "top_contributors": sorted(
                [{"name": name, "commits": count} for name, count in author_stats.items()],
                key=lambda x: x["commits"],
                reverse=True
            )[:5],
            "most_changed_files": sorted(
                [{"file": name, "changes": count} for name, count in file_activity.items()],
                key=lambda x: x["changes"],
                reverse=True
            )[:10],
            "commit_activity_by_day": commit_activity,
            "recent_commits": recent_commits,
            "first_commit_date": all_commits[-1]["commit"]["author"]["date"] if all_commits else None,
            "last_commit_date": all_commits[0]["commit"]["author"]["date"] if all_commits else None
        }

    except requests.HTTPError as e:
        print(f"GitHub API error: {e}")
        return {"error": str(e)}