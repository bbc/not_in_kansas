import logging
import os
import tempfile
import shutil # For cleanup if repo_path is provided and we don't want to keep it

from openai_client import OpenAIClient, OpenAIClientError, OpenAIResponseError
from github_client import GitHubClient, GitHubClientError
from test_runner import TestRunner, TestRunnerError
from status_enums import RepoStatus
from exceptions import BaseAppException


class RepoProcessor:
    def __init__(self, repo_name: str, context: dict, prompt: str,
                 openai_client: OpenAIClient, github_client: GitHubClient,
                 # Allow repo_path to be explicitly None or a path
                 repo_path: str | None = None,
                 keep_temp_dir: bool = False): # For debugging
        self.repo_name = repo_name
        self.context = context
        self.prompt = prompt
        self.openai_client = openai_client
        self.github_client = github_client
        self.provided_repo_path = repo_path # Store if a path was provided
        self.repo_path = repo_path # This will be the actual path used
        self.status = RepoStatus.NOT_PROCESSED
        self.keep_temp_dir = keep_temp_dir

        self.global_settings = context.get("global_settings", {})
        self.repo_settings = context.get("repository_settings", {}).get(repo_name, {})

        self.build_command = self._get_setting("build_command", "make test")
        self.target_files = self._get_setting("target_files", [])
        self.reviewers = self._get_setting("reviewers", [])
        self.repo_base_url = self._get_setting("repo_base_url", "https://github.com/bbc/")
        # For future templating, though not implemented in this refactor
        self.branch_name_template = self._get_setting("branch_name_template", "automated-tech-debt-fix/{repo_name}")
        self.commit_message_template = self._get_setting("commit_message_template", "Automated update: Applied tech debt fix for {repo_name}")
        self.pr_title_template = self._get_setting("pr_title_template", "[Automated PR] Tech debt fix for {repo_name}")
        self.pr_body_template = self._get_setting("pr_body_template", "This PR was created automatically to apply a tech debt fix for {repo_name}.\n\nPlease review and merge.")


        logging.debug(f"Build command for {self.repo_name}: {self.build_command}")
        self.test_runner = TestRunner(self.build_command)

    def _get_setting(self, key: str, default: any = None) -> any:
        return self.repo_settings.get(key, self.global_settings.get(key, default))

    def process(self):
        logging.info(f"Processing repository {self.repo_name}")

        if self.provided_repo_path:
            self.repo_path = self.provided_repo_path
            logging.debug(f"Using provided repo path: {self.repo_path}")
            self._process_repository()
        else:
            with tempfile.TemporaryDirectory() as tmpdirname:
                self.repo_path = os.path.join(tmpdirname, self.repo_name)
                logging.debug(f"Created temporary directory: {self.repo_path}")
                try:
                    self._process_repository()
                finally:
                    if self.keep_temp_dir:
                        logging.info(f"Keeping temporary directory: {tmpdirname} (repo: {self.repo_path})")
                        # To keep it, we need to move it out of the context manager's control
                        # This is a bit hacky; for real "keep", copy elsewhere before exiting.
                        # For now, just log and let it be deleted if not keep_temp_dir.
                        pass
                    # If not self.keep_temp_dir, it's cleaned up automatically by TemporaryDirectory

    def _process_repository(self):
        try:
            repo_full_url = f"{self.repo_base_url.rstrip('/')}/{self.repo_name}"
            logging.debug(f"Repository URL: {repo_full_url}")
            logging.debug(f"Repository path for operations: {self.repo_path}")

            if not self.provided_repo_path: # Only clone if not using a pre-existing path
                logging.info(f"Cloning repository {self.repo_name} into {self.repo_path}")
                self.github_client.clone_repo(repo_full_url, self.repo_path)
            else:
                logging.info(f"Skipping clone for provided repo_path: {self.repo_path}")


            branch_name = self.branch_name_template.format(repo_name=self.repo_name)
            logging.info(f"Ensuring branch {branch_name} (create or reset)")
            self.github_client.create_or_reset_branch(self.repo_path, branch_name) # Changed to create_or_reset

            num_files_changed = self.apply_changes()
            if num_files_changed == 0: # No files were targeted or found to update by LLM
                logging.info(f"No changes applied to {self.repo_name} by LLM or no target files found.")
                self.status = RepoStatus.SUCCESS_NO_CHANGES # Or a more specific status if files weren't found
                return
            elif num_files_changed < 0: # Indicates an error in apply_changes itself
                # Status already set by apply_changes
                return


            logging.info(f"Running tests for {self.repo_name}")
            tests_passed, test_output = self.test_runner.run_tests(self.repo_path)
            if not tests_passed:
                logging.error(f"Tests failed in {self.repo_name}. Output:\n{test_output}")
                self.status = RepoStatus.ERROR_TESTS_FAILED
                return
            logging.info(f"Tests passed for {self.repo_name}. Output:\n{test_output}")

            commit_message = self.commit_message_template.format(repo_name=self.repo_name)
            logging.info(f"Committing changes in {self.repo_name}")
            self.github_client.commit_changes(self.repo_path, commit_message)

            logging.info(f"Pushing branch {branch_name}")
            self.github_client.push_branch(self.repo_path, branch_name)

            pr_title = self.pr_title_template.format(repo_name=self.repo_name)
            pr_body = self.pr_body_template.format(repo_name=self.repo_name)
            logging.info(f"Creating pull request for {self.repo_name}")
            self.github_client.create_pull_request(self.repo_path, pr_title, pr_body, self.reviewers)

            self.status = RepoStatus.SUCCESS_PR_CREATED

        except GitHubClientError as e:
            logging.error(f"GitHub client error processing repository {self.repo_name}: {e}", exc_info=True)
            # More specific status based on the type of GitHubClientError if defined
            if "clone" in str(e).lower(): self.status = RepoStatus.ERROR_CLONING
            elif "branch" in str(e).lower(): self.status = RepoStatus.ERROR_BRANCHING
            elif "commit" in str(e).lower(): self.status = RepoStatus.ERROR_COMMITTING
            elif "push" in str(e).lower(): self.status = RepoStatus.ERROR_PUSHING
            elif "pull request" in str(e).lower(): self.status = RepoStatus.ERROR_PR_CREATION
            else: self.status = RepoStatus.ERROR_GENERIC
        except TestRunnerError as e: # Assuming TestRunner might raise this
            logging.error(f"Test runner error for {self.repo_name}: {e}", exc_info=True)
            self.status = RepoStatus.ERROR_TESTS_FAILED # Or a more specific test error
        except BaseAppException as e: # Catch other custom app exceptions
            logging.error(f"Application error processing repository {self.repo_name}: {e}", exc_info=True)
            if isinstance(e, OpenAIClientError): self.status = RepoStatus.ERROR_OPENAI_API
            elif isinstance(e, OpenAIResponseError): self.status = RepoStatus.ERROR_OPENAI_RESPONSE_FORMAT
            else: self.status = RepoStatus.ERROR_GENERIC
        except Exception as e:
            logging.error(f"Unexpected error processing repository {self.repo_name}: {e}", exc_info=True)
            self.status = RepoStatus.ERROR_GENERIC

    def apply_changes(self) -> int:
        """
        Applies changes using OpenAI and writes them to files.
        Returns the number of files successfully updated by the LLM.
        Returns 0 if LLM returns no files to update or no target files were processed.
        Returns -1 if a critical error occurs during the process (e.g., OpenAI API error).
        """
        logging.debug(f"Applying changes to {self.repo_name} in path {self.repo_path}")

        repo_context = {
            "repository": self.repo_name,
            "repo_path": self.repo_path, # Pass the actual processing path
            "target_files": self.target_files,
        }

        current_files = {}
        found_any_target_file = False
        for file_rel_path in self.target_files:
            full_path = os.path.join(self.repo_path, file_rel_path)
            if os.path.exists(full_path):
                found_any_target_file = True
                with open(full_path, 'r', encoding='utf-8') as f: # Specify encoding
                    current_files[file_rel_path] = f.read()
                logging.debug(f"Read content of {file_rel_path} in {self.repo_name}")
            else:
                logging.warning(f"Target file {file_rel_path} does not exist in {self.repo_path}")

        if not found_any_target_file and self.target_files:
            logging.error(f"None of the target files {self.target_files} were found in {self.repo_path}.")
            self.status = RepoStatus.ERROR_TARGET_FILES_NOT_FOUND_ALL
            return -1 # Indicate error
        elif not self.target_files:
            logging.info(f"No target files specified for {self.repo_name}. Skipping LLM call.")
            self.status = RepoStatus.SUCCESS_NO_CHANGES
            return 0


        repo_context["current_files"] = current_files

        try:
            response = self.openai_client.generate_code(self.prompt, repo_context)
        except OpenAIClientError as e: # Catch specific client errors
            logging.error(f"OpenAI API client error during apply_changes for {self.repo_name}: {e}")
            self.status = RepoStatus.ERROR_OPENAI_API
            return -1
        except OpenAIResponseError as e:
            logging.error(f"OpenAI response format error for {self.repo_name}: {e}")
            self.status = RepoStatus.ERROR_OPENAI_RESPONSE_FORMAT
            return -1


        updated_files_data = response.get("updated_files")
        if not updated_files_data: # Handles None or empty list
            logging.warning(f"No updated files returned by LLM for {self.repo_name}")
            # This isn't necessarily an error, could be that LLM found no changes needed
            # or the prompt asked it to return empty if no changes.
            # If the expectation is that *some* files should always be returned (even if unchanged),
            # this might become an ERROR_OPENAI_RESPONSE_FORMAT. For now, treat as no changes.
            self.status = RepoStatus.SUCCESS_NO_CHANGES
            return 0

        files_changed_count = 0
        for file_info in updated_files_data:
            file_path = file_info.get('file_path')
            updated_code = file_info.get('updated_content')

            if not file_path: # updated_code can be empty if LLM wants to delete a file (not handled here)
                logging.warning(f"Missing 'file_path' in LLM response item: {file_info} for {self.repo_name}")
                continue
            if updated_code is None: # Explicitly check for None, as empty string is valid
                logging.warning(f"Missing 'updated_content' in LLM response item: {file_info} for {self.repo_name}")
                continue


            full_write_path = os.path.join(self.repo_path, file_path)
            # Ensure the original file was one of the targets to prevent arbitrary writes
            if file_path not in self.target_files:
                logging.warning(f"LLM tried to update non-target file '{file_path}'. Skipping.")
                continue

            try:
                os.makedirs(os.path.dirname(full_write_path), exist_ok=True)
                with open(full_write_path, 'w', encoding='utf-8') as f: # Specify encoding
                    f.write(updated_code)
                logging.debug(f"Updated file {file_path} in {self.repo_name}")
                files_changed_count += 1
            except IOError as e:
                logging.error(f"Failed to write updated file {full_write_path}: {e}")
                self.status = RepoStatus.ERROR_APPLYING_CHANGES # Or a more specific IO error status
                # Decide if one file write error should stop the whole process for this repo
                # For now, let's continue trying to write other files but mark overall as error.
                # If this happens, it might be better to return -1 to stop further processing.

        if files_changed_count == 0 and updated_files_data:
            # LLM returned file data, but none were valid targets or writable
            logging.warning(f"LLM returned data but no valid target files were updated for {self.repo_name}.")
            # This could be an error or just an indication that the LLM's suggestions were not applicable.
            # Let's consider it no changes for now, but this might need refinement.
            self.status = RepoStatus.SUCCESS_NO_CHANGES
            return 0

        return files_changed_count