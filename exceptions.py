class BaseAppException(Exception):
    """Base class for custom exceptions in this application."""
    pass

class OpenAIClientError(BaseAppException):
    """Custom exception for OpenAI API client errors."""
    pass

class OpenAIResponseError(OpenAIClientError):
    """Custom exception for errors in OpenAI API response format or content."""
    pass

class GitHubClientError(BaseAppException):
    """Custom exception for GitHub client errors."""
    pass

class TestRunnerError(BaseAppException):
    """Custom exception for TestRunner errors."""
    pass