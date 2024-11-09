import unittest
import os
import shutil
import tempfile
import json
from unittest.mock import patch
import difflib
import logging

from repo_processor import RepoProcessor
from openai_client import OpenAIClient
from github_client import GitHubClient


class TestIntegration(unittest.TestCase):

    def setUp(self):
        # Configure logging
        logging.basicConfig(level=logging.DEBUG)

        # Create a temporary directory to act as the repositories root
        self.temp_dir = tempfile.mkdtemp()
        self.fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        logging.debug(f"Fixture directory: {self.fixture_dir}")

        # Load context.json
        self.context_path = os.path.join(os.path.dirname(__file__), 'context.json')
        logging.debug(f"Context path: {self.context_path}")
        with open(self.context_path, 'r') as f:
            self.context = json.load(f)

        # Load prompt_general.txt
        self.prompt_path = os.path.join(os.path.dirname(__file__), 'prompt_general.txt')
        logging.debug(f"Prompt path: {self.prompt_path}")
        with open(self.prompt_path, 'r') as f:
            self.prompt = f.read()

        self.openai_client = OpenAIClient()
        self.github_client = GitHubClient()

        # Copy all repositories from fixtures to temp_dir
        for repo_name in self.context["repositories"]:
            fixture_repo_path = os.path.join(self.fixture_dir, repo_name)
            logging.debug(f"Copying fixture repo {fixture_repo_path}")
            temp_repo_path = os.path.join(self.temp_dir, repo_name)
            shutil.copytree(fixture_repo_path, temp_repo_path)

    def tearDown(self):
        # Remove temporary directory after the test
        shutil.rmtree(self.temp_dir)

    @patch('github_client.GitHubClient.clone_repo')
    @patch('github_client.GitHubClient.create_branch')
    @patch('github_client.GitHubClient.commit_changes')
    @patch('github_client.GitHubClient.push_branch')
    @patch('github_client.GitHubClient.create_pull_request')
    @patch('test_runner.TestRunner.run_tests')
    def test_apply_changes(self, mock_run_tests, mock_create_pr, mock_push_branch,
                           mock_commit_changes, mock_create_branch, mock_clone_repo):
        # Mock GitHub operations
        mock_clone_repo.return_value = None
        mock_create_branch.return_value = None
        mock_commit_changes.return_value = None
        mock_push_branch.return_value = None
        mock_create_pr.return_value = None

        # Assume tests pass
        mock_run_tests.return_value = True

        results = {}

        for repo_name in self.context["repositories"]:
            repo_path = os.path.join(self.temp_dir, repo_name)
            logging.debug(f"Processing repository: {repo_name}")
            processor = RepoProcessor(repo_name, self.context, self.prompt,
                                      self.openai_client, self.github_client,
                                      repo_path=repo_path)

            # Process the repository
            processor.process()
            results[repo_name] = processor.result

            # Compare updated files to expected results
            expected_dir = os.path.join(self.fixture_dir, 'expected_updates', repo_name)
            for root, dirs, files in os.walk(expected_dir):
                for file in files:
                    expected_file = os.path.join(root, file)
                    relative_path = os.path.relpath(expected_file, expected_dir)
                    actual_file = os.path.join(repo_path, relative_path)

                    with open(expected_file, 'r') as ef, open(actual_file, 'r') as af:
                        expected_content = ef.read()
                        actual_content = af.read()
                        if expected_content != actual_content:
                            diff = difflib.unified_diff(
                                expected_content.splitlines(),
                                actual_content.splitlines(),
                                fromfile='expected',
                                tofile='actual',
                                lineterm=''
                            )
                            diff_text = '\n'.join(diff)
                            logging.error(f"Mismatch in {file} for repository {repo_name}:\n{diff_text}")
                            self.fail(f"Updated file {file} does not match expected output for repository {repo_name}")
                        else:
                            logging.debug(f"File {file} matches expected output for repository {repo_name}")

        # Verify that PR was created for each repository
        self.assertEqual(len(results), len(self.context["repositories"]))
        for repo_name in self.context["repositories"]:
            self.assertEqual(results[repo_name], "PR created", f"PR not created for {repo_name}")
        self.assertEqual(mock_create_pr.call_count, len(self.context["repositories"]))