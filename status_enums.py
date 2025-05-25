from enum import Enum, auto

class RepoStatus(Enum):
    NOT_PROCESSED = auto()
    SUCCESS_PR_CREATED = auto()
    SUCCESS_NO_CHANGES = auto()
    ERROR_CLONING = auto()
    ERROR_BRANCHING = auto()
    ERROR_APPLYING_CHANGES = auto()
    ERROR_OPENAI_API = auto()
    ERROR_OPENAI_RESPONSE_FORMAT = auto()
    ERROR_TESTS_FAILED = auto()
    ERROR_COMMITTING = auto()
    ERROR_PUSHING = auto()
    ERROR_PR_CREATION = auto()
    ERROR_GENERIC = auto()
    ERROR_TARGET_FILES_NOT_FOUND_PARTIAL = auto() # Some target files were not found
    ERROR_TARGET_FILES_NOT_FOUND_ALL = auto() # All target files were not found

    def __str__(self):
        return self.name.replace("_", " ").title()