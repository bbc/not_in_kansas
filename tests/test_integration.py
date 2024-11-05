import unittest
import os
import shutil
import tempfile
from unittest.mock import patch

from repo_processor import RepoProcessor
from openai_client import OpenAIClient
from github_client import GitHubClient


class TestIntegration(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory to act as the repository
        self.temp_dir = tempfile.mkdtemp()
        self.fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.repo_name = 'componenta'
        self.repo_path = os.path.join(self.temp_dir, self.repo_name)

        # Copy fixture files to the temporary directory
        shutil.copytree(os.path.join(self.fixture_dir, self.repo_name), self.repo_path)

        # Load context.json
        with open(os.path.join(os.path.dirname(__file__), 'context.json'), 'r') as f:
            self.context = json.load(f)

        # Load prompt.txt
        with open(os.path.join(os.path.dirname(__file__), 'prompt.txt'), 'r') as f:
            self.prompt = f.read()

        self.openai_client = OpenAIClient()
        self.github_client = GitHubClient()

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

        processor = RepoProcessor(self.repo_name, self.context, self.prompt,
                                  self.openai_client, self.github_client)

        # Use the fixture repository path
        processor.process()

        # Compare updated files to expected results
        expected_dir = os.path.join(self.fixture_dir, 'expected_updates', self.repo_name)
        for root, dirs, files in os.walk(expected_dir):
            for file in files:
                expected_file = os.path.join(root, file)
                relative_path = os.path.relpath(expected_file, expected_dir)
                actual_file = os.path.join(self.repo_path, relative_path)

                with open(expected_file, 'r') as ef, open(actual_file, 'r') as af:
                    expected_content = ef.read()
                    actual_content = af.read()
                    self.assertEqual(expected_content, actual_content, f"Mismatch in {file}")

        # Verify that PR was created
        self.assertEqual(processor.result, "PR created")
        mock_create_pr.assert_called_once()


if __name__ == '__main__':
    unittest.main()