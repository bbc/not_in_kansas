import unittest
from unittest.mock import patch, MagicMock

from repo_processor import RepoProcessor
from openai_client import OpenAIClient
from github_client import GitHubClient


class TestRepoProcessor(unittest.TestCase):

    @patch('repo_processor.TestRunner')
    @patch('repo_processor.GitHubClient')
    @patch('repo_processor.OpenAIClient')
    def test_process_success(self, mock_openai_client, mock_github_client, mock_test_runner):
        # Setup mocks
        mock_openai_client_instance = mock_openai_client.return_value
        mock_openai_client_instance.generate_code.return_value = {
            "updated_files": {
                "src/main/java/App.java": "// Updated code"
            }
        }

        mock_test_runner_instance = mock_test_runner.return_value
        mock_test_runner_instance.run_tests.return_value = True

        # Create a RepoProcessor instance
        repo_name = "test-repo"
        context = {
            "repositories": [repo_name],
            "global_settings": {
                "reviewers": ["dev1"],
                "build_command": "echo 'Running tests...'"
            },
            "repository_settings": {
                repo_name: {
                    "target_files": ["src/main/java/App.java"]
                }
            }
        }
        prompt = "Upgrade from Java 8 to Java 11"

        processor = RepoProcessor(repo_name, context, prompt, mock_openai_client_instance, mock_github_client)

        # Run process method
        processor.process()

        # Assertions
        self.assertEqual(processor.result, "PR created")
        mock_openai_client_instance.generate_code.assert_called_once()
        mock_test_runner_instance.run_tests.assert_called_once()
        mock_github_client.clone_repo.assert_called_once()
        mock_github_client.create_branch.assert_called_once()
        mock_github_client.commit_changes.assert_called_once()
        mock_github_client.push_branch.assert_called_once()
        mock_github_client.create_pull_request.assert_called_once()


if __name__ == '__main__':
    unittest.main()