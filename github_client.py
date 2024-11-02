import logging
import subprocess
from typing import List


class GitHubClient:
    """Client to interact with GitHub using the gh CLI."""

    def clone_repo(self, repo_url: str, dest_path: str):
        logging.debug(f"Cloning repository {repo_url} into {dest_path}")
        cmd = ["gh", "repo", "clone", repo_url, dest_path]
        subprocess.check_call(cmd)

    def create_branch(self, repo_path: str, branch_name: str):
        logging.debug(f"Creating branch {branch_name} in {repo_path}")
        cmd = ["git", "-C", repo_path, "checkout", "-b", branch_name]
        subprocess.check_call(cmd)

    def commit_changes(self, repo_path: str, message: str):
        logging.debug(f"Committing changes in {repo_path}")
        cmd_add = ["git", "-C", repo_path, "add", "."]
        subprocess.check_call(cmd_add)
        cmd_commit = ["git", "-C", repo_path, "commit", "-m", message]
        subprocess.check_call(cmd_commit)

    def push_branch(self, repo_path: str, branch_name: str):
        logging.debug(f"Pushing branch {branch_name} from {repo_path}")
        cmd = ["git", "-C", repo_path, "push", "--set-upstream", "origin", branch_name]
        subprocess.check_call(cmd)

    def create_pull_request(self, repo_path: str, title: str, body: str, reviewers: List[str]):
        logging.debug(f"Creating pull request in {repo_path}")
        cmd = ["gh", "pr", "create", "--title", title, "--body", body]
        for reviewer in reviewers:
            cmd.extend(["--reviewer", reviewer])
        subprocess.check_call(cmd, cwd=repo_path)