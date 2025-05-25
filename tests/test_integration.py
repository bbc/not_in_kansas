import unittest
import os
import shutil
import tempfile
import json
from unittest.mock import patch, MagicMock
import difflib
import logging

from openai_client import OpenAIClient # For type hinting and instantiation if needed under patch
from github_client import GitHubClient
from repo_processor import RepoProcessor
from status_enums import RepoStatus


class TestIntegration(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.INFO) # Use INFO for less verbosity unless debugging
        self.temp_dir = tempfile.mkdtemp()
        self.fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.llm_responses_dir = os.path.join(self.fixture_dir, 'llm_responses') # For mock LLM JSONs
        os.makedirs(self.llm_responses_dir, exist_ok=True) # Ensure it exists

        logging.debug(f"Fixture directory: {self.fixture_dir}")

        self.context_path = os.path.join(os.path.dirname(__file__), 'context.json')
        logging.debug(f"Context path: {self.context_path}")
        with open(self.context_path, 'r') as f:
            self.context = json.load(f)

        self.prompt_path = os.path.join(os.path.dirname(__file__), 'prompt_general.txt')
        logging.debug(f"Prompt path: {self.prompt_path}")
        with open(self.prompt_path, 'r') as f:
            self.prompt = f.read()

        # self.github_client will be the MagicMock instance from the patch decorator
        # self.openai_client_instance = OpenAIClient() # No longer needed here

        # Prepare mock LLM response files (example for componenta)
        # You'll need to create these JSON files based on your 'expected_updates'
        for repo_name in self.context["repositories"]:
            # Copy initial fixtures
            fixture_repo_path = os.path.join(self.fixture_dir, repo_name)
            temp_repo_path = os.path.join(self.temp_dir, repo_name)
            if os.path.exists(fixture_repo_path):
                shutil.copytree(fixture_repo_path, temp_repo_path)
            else:
                os.makedirs(temp_repo_path, exist_ok=True) # Create dir if no fixtures for it

            # Create dummy LLM response fixture if it doesn't exist
            mock_llm_response_file = os.path.join(self.llm_responses_dir, f"{repo_name}_response.json")
            if not os.path.exists(mock_llm_response_file):
                logging.warning(f"Mock LLM response fixture not found: {mock_llm_response_file}. Creating a default one.")
                default_llm_response = {"updated_files": []}
                # Try to populate from expected_updates
                expected_update_dir_for_repo = os.path.join(self.fixture_dir, 'expected_updates', repo_name)
                if os.path.isdir(expected_update_dir_for_repo):
                    for target_file_rel in self.context.get("repository_settings", {}).get(repo_name, {}).get("target_files", self.context.get("global_settings", {}).get("target_files", [])):
                        expected_file_abs_path = os.path.join(expected_update_dir_for_repo, target_file_rel)
                        if os.path.exists(expected_file_abs_path):
                            with open(expected_file_abs_path, 'r') as f_content:
                                default_llm_response["updated_files"].append({
                                    "file_path": target_file_rel,
                                    "updated_content": f_content.read()
                                })
                with open(mock_llm_response_file, 'w') as f_mock:
                    json.dump(default_llm_response, f_mock, indent=2)


    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('repo_processor.GitHubClient') # Mocks the class where RepoProcessor imports it
    @patch('repo_processor.TestRunner')   # Mocks the class where RepoProcessor imports it
    @patch('openai_client.OpenAIClient.generate_code') # Mocks the method on the class
    def test_apply_changes_to_all_repos(self,
                                        mock_generate_code_method, # This is the mock for OpenAIClient.generate_code
                                        MockTestRunner, # This is the TestRunner class mock
                                        MockGitHubClient): # This is the GitHubClient class mock

        mock_github_instance = MockGitHubClient.return_value
        mock_test_runner_instance = MockTestRunner.return_value

        # Configure mocks
        mock_github_instance.clone_repo.return_value = None
        mock_github_instance.create_or_reset_branch.return_value = None
        mock_github_instance.commit_changes.return_value = None
        mock_github_instance.push_branch.return_value = None
        mock_github_instance.create_pull_request.return_value = None
        mock_test_runner_instance.run_tests.return_value = (True, "Mocked tests passed")

        def mock_openai_responses_from_fixtures(*args, **kwargs):
            # args[0] is self (the OpenAIClient instance), args[1] is prompt, args[2] is context dict
            repo_context = args[2]
            repo_name = repo_context.get("repository")
            response_fixture_path = os.path.join(self.llm_responses_dir, f"{repo_name}_response.json")
            logging.debug(f"Mocking OpenAI response for {repo_name} using {response_fixture_path}")
            if os.path.exists(response_fixture_path):
                with open(response_fixture_path, 'r') as f:
                    return json.load(f)
            else:
                logging.warning(f"LLM response fixture not found for {repo_name} at {response_fixture_path}. Returning empty updates.")
                return {"updated_files": []}

        mock_generate_code_method.side_effect = mock_openai_responses_from_fixtures

        # We need an instance of OpenAIClient to pass to RepoProcessor.
        # The @patch for generate_code will apply to this instance's method.
        openai_client_instance_for_test = OpenAIClient()
        openai_client_instance_for_test.set_model_from_config(self.context.get("global_settings", {}))


        results = {}
        for repo_name in self.context["repositories"]:
            repo_path_for_processing = os.path.join(self.temp_dir, repo_name)
            logging.debug(f"Integration test processing repository: {repo_name} at {repo_path_for_processing}")

            processor = RepoProcessor(repo_name, self.context, self.prompt,
                                      openai_client_instance_for_test, # Pass the instance
                                      mock_github_instance, # Pass the GitHub mock instance
                                      repo_path=repo_path_for_processing, # Use pre-copied fixture path
                                      keep_temp_dir=True) # Keep for inspection if needed

            processor.process()
            results[repo_name] = processor.status

            # Compare updated files to expected results
            expected_dir = os.path.join(self.fixture_dir, 'expected_updates', repo_name)
            if not os.path.isdir(expected_dir):
                logging.warning(f"No expected_updates directory for {repo_name}, skipping file content validation for it.")
                if processor.status == RepoStatus.SUCCESS_PR_CREATED: # if LLM returned empty, status would be NO_CHANGES
                    # This might be an issue if LLM was supposed to make changes but didn't
                    pass # Or self.fail(f"Expected updates for {repo_name} but directory missing and PR created.")
                continue

            for root_dir, _, files_in_dir in os.walk(expected_dir):
                for file_name in files_in_dir:
                    expected_file_full_path = os.path.join(root_dir, file_name)
                    relative_path = os.path.relpath(expected_file_full_path, expected_dir)
                    actual_file_full_path = os.path.join(repo_path_for_processing, relative_path)

                    self.assertTrue(os.path.exists(actual_file_full_path),
                                    f"Actual file {actual_file_full_path} does not exist for repo {repo_name}")

                    with open(expected_file_full_path, 'r', encoding='utf-8') as ef, \
                            open(actual_file_full_path, 'r', encoding='utf-8') as af:
                        expected_content = ef.read()
                        actual_content = af.read()
                        if expected_content != actual_content:
                            diff = difflib.unified_diff(
                                expected_content.splitlines(keepends=True),
                                actual_content.splitlines(keepends=True),
                                fromfile=f'expected/{relative_path}',
                                tofile=f'actual/{relative_path}',
                                lineterm=''
                            )
                            diff_text = ''.join(diff) # Keep newlines for readability
                            logging.error(f"Mismatch in {relative_path} for repository {repo_name}:\n{diff_text}")
                            self.fail(f"Updated file {relative_path} does not match expected for {repo_name}")
                        else:
                            logging.debug(f"File {relative_path} matches expected for {repo_name}")

        self.assertEqual(len(results), len(self.context["repositories"]))
        for repo_name, status_result in results.items():
            # Adjust assertion based on whether changes are expected for that repo by the mock
            expected_llm_response_file = os.path.join(self.llm_responses_dir, f"{repo_name}_response.json")
            with open(expected_llm_response_file, 'r') as f_resp:
                llm_resp_data = json.load(f_resp)
            if llm_resp_data.get("updated_files"):
                self.assertEqual(status_result, RepoStatus.SUCCESS_PR_CREATED, f"PR not created as expected for {repo_name}")
            else:
                self.assertEqual(status_result, RepoStatus.SUCCESS_NO_CHANGES, f"Expected no changes for {repo_name} but got {status_result}")

        self.assertEqual(mock_create_pr.call_count, sum(1 for r in self.context["repositories"] if json.load(open(os.path.join(self.llm_responses_dir, f"{r}_response.json")))["updated_files"]))
        self.assertEqual(mock_generate_code_method.call_count, len(self.context["repositories"]))

if __name__ == '__main__':
    unittest.main()