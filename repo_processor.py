import logging
import os
import tempfile

from openai_client import OpenAIClient
from github_client import GitHubClient
from test_runner import TestRunner


class RepoProcessor:
    def __init__(self, repo_name: str, context: dict, prompt: str,
                 openai_client: OpenAIClient, github_client: GitHubClient,
                 repo_path: str = None):
        self.repo_name = repo_name
        self.context = context
        self.prompt = prompt
        self.openai_client = openai_client
        self.github_client = github_client
        self.repo_path = repo_path
        self.result = None

        # Initialize global and repository-specific settings
        self.global_settings = context.get("global_settings", {})
        self.repo_settings = context.get("repository_settings", {}).get(repo_name, {})

        build_command = self.repo_settings.get("build_command",
                                               self.global_settings.get("build_command", "make test"))
        logging.debug(f"Build command for {self.repo_name}: {build_command}")
        self.test_runner = TestRunner(build_command)

    def process(self):
        logging.info(f"Processing repository {self.repo_name}")
        if self.repo_path:
            # Use the provided repo_path
            repo_path = self.repo_path
            logging.debug(f"Using provided repo path: {repo_path}")
        else:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as tmpdirname:
                repo_path = os.path.join(tmpdirname, self.repo_name)
                logging.debug(f"Created temporary directory: {repo_path}")
                self._process_repository(repo_path)
                return
        self._process_repository(repo_path)

    def _process_repository(self, repo_path):
        try:
            repo_url = f"https://github.com/bbc/{self.repo_name}"
            logging.debug(f"Repository URL: {repo_url}")
            logging.debug(f"Repository path: {repo_path}")

            # Clone the repository
            logging.info(f"Cloning repository {self.repo_name}")
            self.github_client.clone_repo(repo_url, repo_path)

            branch_name = "automated-tech-debt-fix"
            logging.info(f"Creating branch {branch_name}")
            self.github_client.create_branch(repo_path, branch_name)

            updated = self.apply_change(repo_path)

            if not updated:
                logging.info(f"No changes applied to {self.repo_name}")
                self.result = "No changes applied"
                return

            logging.info(f"Running tests for {self.repo_name}")
            tests_passed = self.test_runner.run_tests(repo_path)

            if not tests_passed:
                logging.info(f"Tests failed in {self.repo_name}")
                self.result = "Tests failed"
                return

            commit_message = "Automated update: Applied tech debt fix"
            logging.info(f"Committing changes in {self.repo_name}")
            self.github_client.commit_changes(repo_path, commit_message)

            logging.info(f"Pushing branch {branch_name}")
            self.github_client.push_branch(repo_path, branch_name)

            pr_title = f"[Automated PR] Tech debt fix for {self.repo_name}"
            pr_body = "This PR was created automatically to apply a tech debt fix.\n\nPlease review and merge."
            reviewers = self.repo_settings.get("reviewers", self.global_settings.get("reviewers", []))
            logging.info(f"Creating pull request for {self.repo_name}")
            self.github_client.create_pull_request(repo_path, pr_title, pr_body, reviewers)

            self.result = "PR created"
        except Exception as e:
            logging.error(f"Error processing repository {self.repo_name}: {e}", exc_info=True)
            self.result = f"Error: {e}"

    def apply_change(self, repo_path: str) -> dict:
        logging.debug(f"Applying changes to {self.repo_name}")

        # Prepare context for OpenAI API
        repo_context = {
            "repository": self.repo_name,
            "repo_path": repo_path,
            "target_files": self.repo_settings.get("target_files",
                                                   self.global_settings.get("target_files", [])),
        }

        # Read current contents of target files
        current_files = {}
        for file_path in repo_context["target_files"]:
            full_path = os.path.join(repo_path, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    current_files[file_path] = f.read()
            else:
                logging.warning(f"File {file_path} does not exist in {self.repo_name}")

        # Include current file contents in the context
        repo_context["current_files"] = current_files

        # Generate code using OpenAI API
        response = self.openai_client.generate_code(self.prompt, repo_context)
        updated_files = response.get("updated_files")
        if not updated_files:
            logging.warning(f"No updated files returned for {self.repo_name}")
            return False

        # Apply updates to files
        for file_info in updated_files:
            file_path = file_info.get('file_path')
            updated_code = file_info.get('updated_content')

            if not file_path or not updated_code:
                logging.warning(f"Missing 'file_path' or 'updated_content' in {file_info}")
                continue

            full_path = os.path.join(repo_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(updated_code)
            logging.debug(f"Updated file {file_path} in {self.repo_name}")

        return True