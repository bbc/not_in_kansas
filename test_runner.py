import logging
import subprocess
import shlex # For robust command splitting
from exceptions import TestRunnerError

class TestRunner:
    """Runs tests for the given repository."""

    def __init__(self, build_command: str):
        self.build_command = build_command

    def run_tests(self, repo_path: str) -> tuple[bool, str]:
        """
        Runs tests in the given repository.
        Returns a tuple: (success_boolean, combined_output_string).
        """
        logging.debug(f"Running tests in {repo_path} using command: {self.build_command}")
        try:
            cmd = shlex.split(self.build_command) # Use shlex for robust splitting
            # Use subprocess.run to capture output
            process = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True, # Decodes stdout/stderr to string
                check=False # We'll check returncode manually
            )
            combined_output = f"STDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"

            if process.returncode == 0:
                logging.info(f"Tests passed in {repo_path}.")
                return True, combined_output
            else:
                logging.error(f"Tests failed in {repo_path}. Return code: {process.returncode}")
                return False, combined_output
        except subprocess.CalledProcessError as e: # Should not be reached if check=False
            err_msg = f"Test execution failed with CalledProcessError for command '{self.build_command}': {e}"
            logging.error(err_msg, exc_info=True)
            # Capture output if possible, though e.stdout/stderr might be None
            output = f"STDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}" if hasattr(e, 'stdout') else "Output not captured."
            raise TestRunnerError(f"{err_msg}\n{output}") from e
        except FileNotFoundError as e:
            err_msg = f"Test command executable not found: {self.build_command.split()[0] if self.build_command else 'N/A'}. Error: {e}"
            logging.error(err_msg, exc_info=True)
            raise TestRunnerError(err_msg) from e
        except Exception as e: # Catch any other exception during test run
            err_msg = f"An unexpected error occurred during test execution for command '{self.build_command}': {e}"
            logging.error(err_msg, exc_info=True)
            raise TestRunnerError(err_msg) from e