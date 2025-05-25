import logging
import subprocess
from typing import List
from exceptions import GitHubClientError # Import custom exception

class GitHubClient:
    """
    Client to interact with GitHub using the gh CLI and git.
    Requires `gh` and `git` to be installed and authenticated.
    """

    def _run_command(self, cmd: List[str], cwd: str | None = None, operation_desc: str = "command"):
        logging.debug(f"Running {operation_desc}: {' '.join(cmd)} {'in ' + cwd if cwd else ''}")
        try:
            # Capture output for better debugging if needed, though check_call is simpler for now
            subprocess.check_call(cmd, cwd=cwd)
            logging.debug(f"{operation_desc.capitalize()} successful.")
        except subprocess.CalledProcessError as e:
            err_msg = f"Error during {operation_desc}: {e}. Command: '{' '.join(cmd)}'. Output: {e.stderr if hasattr(e, 'stderr') else 'N/A'}"
            logging.error(err_msg)
            raise GitHubClientError(err_msg) from e
        except FileNotFoundError as e:
            err_msg = f"Error during {operation_desc}: Required command-line tool (git or gh) not found. {e}"
            logging.error(err_msg)
            raise GitHubClientError(err_msg) from e


    def clone_repo(self, repo_url: str, dest_path: str):
        cmd = ["gh", "repo", "clone", repo_url, dest_path]
        self._run_command(cmd, operation_desc=f"cloning repository {repo_url}")

    def create_or_reset_branch(self, repo_path: str, branch_name: str):
        # Fetches remote branches and then creates/resets the local branch from origin's main/master or the remote branch if it exists
        # This is a safer approach than just deleting and recreating locally.
        # First, ensure we have the latest from remote
        # self._run_command(["git", "-C", repo_path, "fetch", "origin"], operation_desc=f"fetching origin for {repo_path}")

        # Check if branch exists locally
        try:
            subprocess.check_output(["git", "-C", repo_path, "rev-parse", "--verify", branch_name], stderr=subprocess.STDOUT)
            # If branch exists, check it out
            logging.debug(f"Branch {branch_name} already exists locally. Checking it out.")
            cmd_checkout = ["git", "-C", repo_path, "checkout", branch_name]
            self._run_command(cmd_checkout, operation_desc=f"checking out existing branch {branch_name}")
            # Optional: reset to remote if desired
            # self._run_command(["git", "-C", repo_path, "reset", "--hard", f"origin/{branch_name}"], operation_desc=f"resetting branch {branch_name} to origin")

        except subprocess.CalledProcessError:
            # Branch does not exist locally, create it
            logging.debug(f"Branch {branch_name} does not exist locally. Creating it.")
            # Try to create from remote if it exists there, otherwise create a new orphan or from default branch
            # For simplicity, just create it or use -B to force create/reset
            cmd_create = ["git", "-C", repo_path, "checkout", "-B", branch_name]
            self._run_command(cmd_create, operation_desc=f"creating/resetting branch {branch_name}")


    def commit_changes(self, repo_path: str, message: str):
        cmd_add = ["git", "-C", repo_path, "add", "."]
        self._run_command(cmd_add, cwd=repo_path, operation_desc="staging changes")
        # Check if there are changes to commit
        status_cmd = ["git", "-C", repo_path, "status", "--porcelain"]
        status_output = subprocess.check_output(status_cmd, cwd=repo_path).decode('utf-8').strip()
        if not status_output:
            logging.info(f"No changes to commit in {repo_path}.")
            return # Or raise a specific status/exception if a commit was expected

        cmd_commit = ["git", "-C", repo_path, "commit", "-m", message]
        self._run_command(cmd_commit, cwd=repo_path, operation_desc="committing changes")

    def push_branch(self, repo_path: str, branch_name: str):
        cmd = ["git", "-C", repo_path, "push", "--set-upstream", "origin", branch_name, "--force"] # Added --force for overwriting
        self._run_command(cmd, cwd=repo_path, operation_desc=f"pushing branch {branch_name}")

    def create_pull_request(self, repo_path: str, title: str, body: str, reviewers: List[str]):
        cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--fill"] # --fill can auto-populate from commit
        for reviewer in reviewers:
            cmd.extend(["--reviewer", reviewer])
        # It's safer to run gh commands from within the repo directory
        self._run_command(cmd, cwd=repo_path, operation_desc="creating pull request")