import logging
import subprocess


class TestRunner:
    """Runs tests for the given repository."""

    def __init__(self, build_command: str):
        self.build_command = build_command

    def run_tests(self, repo_path: str) -> bool:
        logging.debug(f"Running tests in {repo_path} using command: {self.build_command}")
        try:
            cmd = self.build_command.split()
            subprocess.check_call(cmd, cwd=repo_path)
            return True
        except subprocess.CalledProcessError:
            return False