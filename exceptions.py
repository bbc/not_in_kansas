class BaseAppException(Exception):
    """Base class for custom exceptions in this application."""
    pass

class LLMClientError(BaseAppException): # Renamed
    """Custom exception for LLM API client errors."""
    pass

class LLMResponseError(LLMClientError): # Renamed and inherits from LLMClientError
    """Custom exception for errors in LLM API response format or content."""
    pass

class GitHubClientError(BaseAppException):
    """Custom exception for GitHub client errors."""
    pass

class TestRunnerError(BaseAppException):
    """Custom exception for TestRunner errors."""
    pass