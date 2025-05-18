import unittest
import os
import shutil
import tempfile
import json
from unittest.mock import patch, MagicMock # Add MagicMock
import difflib
import logging


from openai_client import OpenAIClient
from github_client import GitHubClient
from repo_processor import RepoProcessor


class TestIntegration(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.temp_dir = tempfile.mkdtemp()
        self.fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        logging.debug(f"Fixture directory: {self.fixture_dir}")

        self.context_path = os.path.join(os.path.dirname(__file__), 'context.json')
        logging.debug(f"Context path: {self.context_path}")
        with open(self.context_path, 'r') as f:
            self.context = json.load(f)

        self.prompt_path = os.path.join(os.path.dirname(__file__), 'prompt_general.txt')
        logging.debug(f"Prompt path: {self.prompt_path}")
        with open(self.prompt_path, 'r') as f:
            self.prompt = f.read()

        # We will mock OpenAIClient.generate_code, so no need to instantiate the real one here for the test logic
        # self.openai_client = OpenAIClient() # REMOVE OR COMMENT OUT
        self.github_client = GitHubClient() # Keep this as it's mocked at the call site

        for repo_name in self.context["repositories"]:
            fixture_repo_path = os.path.join(self.fixture_dir, repo_name)
            logging.debug(f"Copying fixture repo {fixture_repo_path}")
            temp_repo_path = os.path.join(self.temp_dir, repo_name)
            shutil.copytree(fixture_repo_path, temp_repo_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('github_client.GitHubClient.clone_repo')
    @patch('github_client.GitHubClient.create_branch')
    @patch('github_client.GitHubClient.commit_changes')
    @patch('github_client.GitHubClient.push_branch')
    @patch('github_client.GitHubClient.create_pull_request')
    @patch('test_runner.TestRunner.run_tests')
    @patch('openai_client.OpenAIClient.generate_code') # <--- ADD THIS PATCH
    def test_apply_changes(self,
                           mock_generate_code, # <--- Add mock argument
                           mock_run_tests,
                           mock_create_pr,
                           mock_push_branch,
                           mock_commit_changes,
                           mock_create_branch,
                           mock_clone_repo):

        # --- Define what mock_generate_code should return for each repo/call ---
        # This is the tricky part: you need to simulate what OpenAI would return
        # for each set of input files. You could have a dictionary or a more
        # sophisticated side_effect function.
        # For simplicity, let's assume a generic successful update for now.
        # You'd ideally load these expected responses from fixture JSON files.

        def mock_openai_responses(*args, **kwargs):
            # args[0] is the prompt, args[1] is the context dictionary
            repo_context = args[1]
            repo_name = repo_context.get("repository")
            updated_files_list = []

            # Example: Load expected LLM output for 'componenta' from a fixture
            if repo_name == "componenta":
                expected_update_dir = os.path.join(self.fixture_dir, 'expected_updates', repo_name)
                for target_file_rel_path in repo_context["target_files"]:
                    # This is a simplified example: you'd load the *expected LLM JSON output*
                    # which contains the file content, not just the file content directly.
                    # Here, we're constructing the kind of JSON the LLM should return.
                    expected_file_path = os.path.join(expected_update_dir, target_file_rel_path)
                    if os.path.exists(expected_file_path):
                        with open(expected_file_path, 'r') as f:
                            expected_content = f.read()
                        updated_files_list.append({
                            "file_path": target_file_rel_path,
                            "updated_content": expected_content
                        })
                    else: # If no expected update, assume no change by LLM
                        original_file_path_full = os.path.join(repo_context["repo_path"], target_file_rel_path)
                        if os.path.exists(original_file_path_full):
                            with open(original_file_path_full, 'r') as f:
                                original_content = f.read()
                            updated_files_list.append({
                                "file_path": target_file_rel_path,
                                "updated_content": original_content # LLM returns original if no change
                            })
                return {"updated_files": updated_files_list}
            # Add similar logic for other components or a default
            elif repo_name == "componentb": # And so on for other components...
                expected_update_dir = os.path.join(self.fixture_dir, 'expected_updates', repo_name)
                for target_file_rel_path in repo_context["target_files"]:
                    expected_file_path = os.path.join(expected_update_dir, target_file_rel_path)
                    if os.path.exists(expected_file_path):
                        with open(expected_file_path, 'r') as f:
                            expected_content = f.read()
                        updated_files_list.append({
                            "file_path": target_file_rel_path,
                            "updated_content": expected_content
                        })
                    else:
                        original_file_path_full = os.path.join(repo_context["repo_path"], target_file_rel_path)
                        if os.path.exists(original_file_path_full):
                            with open(original_file_path_full, 'r') as f:
                                original_content = f.read()
                            updated_files_list.append({
                                "file_path": target_file_rel_path,
                                "updated_content": original_content
                            })
                return {"updated_files": updated_files_list}
            # ... repeat for componentc, componentd, componente
            else: # Default if not specifically handled
                updated_files_list = []
                for target_file_rel_path in repo_context["target_files"]:
                    original_file_path_full = os.path.join(repo_context["repo_path"], target_file_rel_path)
                    if os.path.exists(original_file_path_full):
                        with open(original_file_path_full, 'r') as f:
                            original_content = f.read()
                        updated_files_list.append({
                            "file_path": target_file_rel_path,
                            "updated_content": original_content # No change
                        })
                return {"updated_files": updated_files_list}


        mock_generate_code.side_effect = mock_openai_responses

        mock_clone_repo.return_value = None
        mock_create_branch.return_value = None
        mock_commit_changes.return_value = None
        mock_push_branch.return_value = None
        mock_create_pr.return_value = None
        mock_run_tests.return_value = True

        results = {}

        # Instantiate the *real* OpenAIClient here, but its .generate_code method is mocked
        # OR, if RepoProcessor instantiates its own, the patch will cover it.
        # Let's assume RepoProcessor instantiates its own OpenAIClient or you pass one.
        # For the test, we pass a MagicMock() instance for openai_client if RepoProcessor expects an instance
        # and its generate_code method is what we've patched via @patch('openai_client.OpenAIClient.generate_code')

        # This line is important: we need an OpenAIClient instance.
        # The @patch decorator handles replacing the *method* on any instance.
        mocked_openai_client_instance = OpenAIClient()


        for repo_name in self.context["repositories"]:
            repo_path = os.path.join(self.temp_dir, repo_name)
            logging.debug(f"Processing repository: {repo_name}")

            # Pass the mocked_openai_client_instance IF RepoProcessor doesn't create its own
            # If RepoProcessor *does* create its own, the patch on the class method will apply.
            # The current RepoProcessor __init__ takes an openai_client argument.
            processor = RepoProcessor(repo_name, self.context, self.prompt,
                                      mocked_openai_client_instance, # Pass an instance whose method is patched
                                      self.github_client, # This is already a mock from the test class
                                      repo_path=repo_path)
            processor.process()
            results[repo_name] = processor.result

            expected_dir = os.path.join(self.fixture_dir, 'expected_updates', repo_name)
            for root_dir, _, files_in_dir in os.walk(expected_dir): # Renamed variables for clarity
                for file_name in files_in_dir: # Renamed variables
                    expected_file_full_path = os.path.join(root_dir, file_name)
                    relative_path = os.path.relpath(expected_file_full_path, expected_dir)
                    actual_file_full_path = os.path.join(repo_path, relative_path) # Renamed variables

                    self.assertTrue(os.path.exists(actual_file_full_path), f"Actual file {actual_file_full_path} does not exist for repo {repo_name}")

                    with open(expected_file_full_path, 'r') as ef, open(actual_file_full_path, 'r') as af:
                        expected_content = ef.read()
                        actual_content = af.read()
                        if expected_content != actual_content:
                            diff = difflib.unified_diff(
                                expected_content.splitlines(),
                                actual_content.splitlines(),
                                fromfile=f'expected/{relative_path}', # More informative diff
                                tofile=f'actual/{relative_path}',   # More informative diff
                                lineterm=''
                            )
                            diff_text = '\n'.join(diff)
                            logging.error(f"Mismatch in {relative_path} for repository {repo_name}:\n{diff_text}")
                            self.fail(f"Updated file {relative_path} does not match expected output for repository {repo_name}")
                        else:
                            logging.debug(f"File {relative_path} matches expected output for repository {repo_name}")

        self.assertEqual(len(results), len(self.context["repositories"]))
        for repo_name in self.context["repositories"]:
            self.assertEqual(results[repo_name], "PR created", f"PR not created for {repo_name}")
        self.assertEqual(mock_create_pr.call_count, len(self.context["repositories"]))
        # Assert that generate_code was called once per repository
        self.assertEqual(mock_generate_code.call_count, len(self.context["repositories"]))

if __name__ == '__main__':
    unittest.main()