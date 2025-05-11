import subprocess
import os

def get_git_history(repo_url: str, branch: str):
    """
    Clones the given repository (or fetches it if it already exists), checks out the given branch,
    and retrieves the commit history and the most frequently changed files.
    """
    # Ensure the repo directory exists
    repo_dir = "repo_dir"
    if os.path.exists(repo_dir):
        subprocess.run(["git", "fetch"], cwd=repo_dir)
    else:
        subprocess.run(["git", "clone", repo_url, repo_dir])

    # Checkout the provided branch
    subprocess.run(["git", "checkout", branch], cwd=repo_dir)

    # Get the total number of commits in the repository
    total_commits = int(subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=repo_dir))

    # If no commits are available, return an error
    if total_commits == 0:
        return {"error": "No commits found in the repository."}

    # Get the commit history (all commits in reverse order)
    commits = subprocess.check_output(
        ["git", "log", "--pretty=format:'%h %s'"],
        cwd=repo_dir
    )

    # Get the files changed between the most recent commit and the previous commit
    changed_files = subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        cwd=repo_dir
    )

    return {
        "commits": commits.decode('utf-8').splitlines(),
        "changed_files": changed_files.decode('utf-8').splitlines(),
    }
