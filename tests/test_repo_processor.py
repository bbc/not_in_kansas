import unittest
from unittest.mock import MagicMock, patch
import tempfile
import os
import logging

# Import your classes (adjust the import paths as necessary)
from repo_processor import RepoProcessor
from openai_client import OpenAIClient
from github_client import GitHubClient
from test_runner import TestRunner

class TestRepoProcessor(unittest.TestCase):
    @patch('openai_client.OpenAI')
    @patch('repo_processor.GitHubClient')
    @patch('repo_processor.OpenAIClient')
    @patch('repo_processor.TestRunner')
    def test_repo_processor_long_output(self, mock_test_runner_class, mock_openai_client_class, mock_github_client_class, mock_openai_class):
        # Set up logging
        logging.basicConfig(level=logging.DEBUG)

        # Mock the OpenAI client instance
        mock_openai_instance = mock_openai_class.return_value

        # Simulate incomplete responses
        incomplete_response_part1 = '{"updated_files": [{"file_path": "pom.xml", "updated_content": "<project><modelVersion>4.0.0</modelVersion><groupId>com.example</groupId><artifactId>my-app</artifactId><version>1.0-SNAPSHOT</version>'  # Note: intentionally incomplete
        incomplete_response_part2 = '</project>"}]}'

        # Side effect to simulate multiple API calls
        mock_openai_instance.chat.completions.create.side_effect = [
            # First call returns incomplete response
            MagicMock(choices=[MagicMock(message=MagicMock(content=incomplete_response_part1))]),
            # Second call returns the continuation
            MagicMock(choices=[MagicMock(message=MagicMock(content=incomplete_response_part2))]),
        ]

        # Mock the TestRunner to always return True
        mock_test_runner = mock_test_runner_class.return_value
        mock_test_runner.run_tests.return_value = True

        # Mock the GitHubClient methods
        mock_github_client = mock_github_client_class.return_value
        mock_github_client.clone_repo = MagicMock()
        mock_github_client.create_branch = MagicMock()
        mock_github_client.commit_changes = MagicMock()
        mock_github_client.push_branch = MagicMock()
        mock_github_client.create_pull_request = MagicMock()

        # Prepare context and prompt
        context = {
            "repositories": ["microservice-repo1"],
            "global_settings": {
                "reviewers": ["dev1", "dev2"],
                "build_command": "echo test",
                "target_files": ["pom.xml"]
            },
            "repository_settings": {
                "microservice-repo1": {
                    "target_files": ["pom.xml"]
                }
            }
        }
        prompt = "Upgrade dependencies in pom.xml to the latest versions."

        # Use a temporary directory for the repository path
        with tempfile.TemporaryDirectory() as temp_repo_path:
            repo_path = os.path.join(temp_repo_path, "microservice-repo1")
            os.makedirs(repo_path, exist_ok=True)

            # Create a dummy pom.xml file
            target_file_path = os.path.join(repo_path, "pom.xml")
            with open(target_file_path, 'w') as f:
                f.write("<project><modelVersion>4.0.0</modelVersion></project>")

            # Instantiate RepoProcessor with mocked clients
            processor = RepoProcessor(
                repo_name="microservice-repo1",
                context=context,
                prompt=prompt,
                openai_client=OpenAIClient(),  # This will use the mocked OpenAI
                github_client=mock_github_client,
                repo_path=repo_path
            )

            # Run the process method
            processor.process()

            # Assertions to verify that the assistant was called multiple times
            self.assertEqual(
                mock_openai_instance.chat.completions.create.call_count,
                2,
                "Expected generate_code to handle continuations and make multiple API calls."
            )

            # Ensure that the file was updated with the concatenated content
            with open(target_file_path, 'r') as f:
                updated_content = f.read()
            expected_content = "<project><modelVersion>4.0.0</modelVersion><groupId>com.example</groupId><artifactId>my-app</artifactId><version>1.0-SNAPSHOT</version></project>"
            self.assertEqual(updated_content, expected_content)


    @patch('repo_processor.GitHubClient')
    @patch('repo_processor.OpenAIClient')
    @patch('repo_processor.TestRunner')
    def test_repo_processor_github_calls(self, mock_test_runner_class, mock_openai_client_class, mock_github_client_class):
        # Mock the OpenAIClient to return a controlled response
        mock_openai_client = mock_openai_client_class.return_value
        mock_openai_client.generate_code.return_value = {
            "updated_files": [
                {
                    "file_path": "src/main/java/App.java",
                    "updated_content": "public class App { /* updated content */ }"
                }
            ]
        }

        # Mock the GitHubClient methods
        mock_github_client = mock_github_client_class.return_value
        mock_github_client.clone_repo = MagicMock()
        mock_github_client.create_branch = MagicMock()
        mock_github_client.commit_changes = MagicMock()
        mock_github_client.push_branch = MagicMock()
        mock_github_client.create_pull_request = MagicMock()

        # Mock the TestRunner to always return True (tests pass)
        mock_test_runner = mock_test_runner_class.return_value
        mock_test_runner.run_tests.return_value = True

        # Prepare context and prompt
        context = {
            "repositories": ["microservice-repo1"],
            "global_settings": {
                "reviewers": ["dev1", "dev2"],
                "build_command": "mvn test",
                "target_files": ["src/main/java/App.java"]
            },
            "repository_settings": {
                "microservice-repo1": {
                    "target_files": ["src/main/java/App.java"]
                }
            }
        }
        prompt = "Upgrade Java version from 1.8 to 11 in specified files."

        # Use a temporary directory for the repository path
        with tempfile.TemporaryDirectory() as temp_repo_path:
            repo_path = os.path.join(temp_repo_path, "microservice-repo1")
            os.makedirs(repo_path, exist_ok=True)

            # Create a dummy file to represent the target file
            target_file_path = os.path.join(repo_path, "src/main/java/App.java")
            os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
            with open(target_file_path, 'w') as f:
                f.write("public class App { /* original content */ }")

            # Instantiate RepoProcessor with mocked clients
            processor = RepoProcessor(
                repo_name="microservice-repo1",
                context=context,
                prompt=prompt,
                openai_client=mock_openai_client,
                github_client=mock_github_client,
                repo_path=repo_path
            )

            # Run the process method
            processor.process()

            # Assertions to verify GitHubClient methods were called correctly
            repo_url = "https://github.com/bbc/microservice-repo1"
            branch_name = "automated-tech-debt-fix"
            commit_message = "Automated update: Applied tech debt fix"
            pr_title = "[Automated PR] Tech debt fix for microservice-repo1"
            pr_body = "This PR was created automatically to apply a tech debt fix.\n\nPlease review and merge."
            reviewers = ["dev1", "dev2"]

            # Check that clone_repo was called correctly
            mock_github_client.clone_repo.assert_called_once_with(repo_url, repo_path)

            # Check that create_branch was called correctly
            mock_github_client.create_branch.assert_called_once_with(repo_path, branch_name)

            # Check that apply_change was called and returned True
            # Since apply_change is internal, we ensure that run_tests was called

            # Check that run_tests was called correctly
            mock_test_runner.run_tests.assert_called_once_with(repo_path)

            # Check that commit_changes was called correctly
            mock_github_client.commit_changes.assert_called_once_with(repo_path, commit_message)

            # Check that push_branch was called correctly
            mock_github_client.push_branch.assert_called_once_with(repo_path, branch_name)

            # Check that create_pull_request was called correctly
            mock_github_client.create_pull_request.assert_called_once_with(
                repo_path, pr_title, pr_body, reviewers
            )

            # Ensure that OpenAIClient's generate_code was called correctly
            mock_openai_client.generate_code.assert_called_once()

            # Verify that the updated file was written correctly
            with open(target_file_path, 'r') as f:
                updated_content = f.read()
            self.assertEqual(updated_content, "public class App { /* updated content */ }")

if __name__ == '__main__':
    unittest.main()