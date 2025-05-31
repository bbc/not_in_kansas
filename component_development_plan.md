I write and maintain java microservices. 

These services run in the aws cloud, normally on ec2 instances but sometimes on the aws lambda service. 

I have hundreds of such microservices.  

Currently, most of these microservice components use aws java 1 sdk to interact with the aws cloud.  

However, aws sdk 1 is being depreciated in favour of aws java sdk 2.  

So each component needs to updated to use aws java sdk 2.  

We use the sdk 1 in three different ways.  

(1) Some componets use sdk1 directly; 

(2) Some use the sdk1 via a BBC internal library and 

(3) Some do both, using the BBC internal library for some functions and the sdk1 for other functions, but split varies between components.  

I only want to update case (1) and (3) to sdk2, as the BBC library is being update separately.  

I want to write a job to do this update.  

I want to use self-built AI agents with a human in the workflow.  

I want the work to be done in a transparent human readable way. 

As a developer I use BDD and TDD.  

So all code updates have human approved BDD and TDD "tests".  

The upgrade needs to be done via PRs that must have at least one human reviewer. 

Each change should have a 100% passing BDD tests as well as unit tests.  

So when PR is approved it is approved that the functionality of the component has not regressed.  

I see several stages to coming up with a solution.  

The solution will differ depending whether it is AI based or developer based.  

And if it is AI based it will vary depending on whether an end-user ai tool is used 
or an engineer codes a job that works as a workflow that upgrades one component at a time 
and a developer is in the loop to approve some parts of process to ensure that they can take responsibility for the change.  

OK, lets think about the first start on how  exactly the AI workflow solution can be specified.  

As background this is what AWS suggest for doing it manually plus other ideas for 'manual' update: 

```text 
The AWS-supported recipe-based tool is the AWS SDK for Java Migration Tool (preview), which uses OpenRewrite recipes (software.amazon.awssdk.v2migration.AwsSdkJavaV1ToV2) 
to automate much of the 1.x→2.x refactoring ([AWS Documentation][1], [docs.openrewrite.org][2]).

Ten other approaches you can use to automate or semi-automate your upgrade:

1. **OpenRewrite CLI**
   Install the rewrite CLI and run the AWS SDK v2 migration recipe across your entire codebase in one go ([docs.openrewrite.org][2]).

2. **OpenRewrite Maven plugin**
   Add the `org.openrewrite.rewrite` plugin to your POM and execute `mvn rewrite:run` to apply the AWS SDK v1→v2 recipes automatically ([AWS Documentation][1]).

3. **OpenRewrite Gradle plugin**
   Apply the same plugin in your `build.gradle` and invoke `gradle rewriteRun` to trigger the migration refactorings ([AWS Documentation][1]).

4. **Custom OpenRewrite recipes**
   Fork or extend the AWS-provided recipe list to handle any specialty cases in your codebase, writing your own recipe definitions if needed ([docs.openrewrite.org][2]).

5. **IntelliJ Structural Search & Replace**
   Define structural-search templates for v1 import patterns and builder calls, then supply v2 replacement templates to semi-automate refactorings inside the IDE ([JetBrains][3]).

6. **Error Prone + Refaster templates**
   Write Refaster “before/after” templates to match v1 SDK usage (`@BeforeTemplate`) and specify the v2 equivalent (`@AfterTemplate`), then apply them via the Error Prone compiler plugin ([errorprone.info][4]).

7. **Eclipse JDT ASTRewrite API**
   Script batch refactorings by writing an Eclipse plugin or headless JDT application that uses ASTRewrite to record and apply the necessary node-level changes ([Eclipse Help][5]).

8. **JavaParser-based transforms**
   Use the JavaParser library to parse each source file into an AST, traverse to find SDK v1 constructs and programmatically replace them with v2 calls ([Strumenta][6]).

9. **grep/sed shell scripts**
   For straightforward tasks (package renames, import updates, simple method substitutions), write find | xargs sed one-liners to do in-place editing across many files ([gitar.ai][7]).

10. **jSparrow (rule-based refactoring tool)**
    Integrate jSparrow into Eclipse or Maven to run its library of Java refactoring rules (over 90 available) and configure or select those that target AWS SDK v1→v2 patterns ([jsparrow.io][8]).

[1]: https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/migration-tool.html?utm_source=chatgpt.com "Migration tool (preview release) - AWS SDK for Java 2.x"
[2]: https://docs.openrewrite.org/recipes/software/amazon/awssdk/v2migration/awssdkjavav1tov2?utm_source=chatgpt.com "Migrate from the AWS SDK for Java v1 to the AWS SDK for Java v2"
[3]: https://www.jetbrains.com/help/idea/structural-search-and-replace.html?utm_source=chatgpt.com "Structural search and replace | IntelliJ IDEA Documentation - JetBrains"
[4]: https://errorprone.info/docs/refaster?utm_source=chatgpt.com "Refaster templates - Error Prone"
[5]: https://help.eclipse.org/latest/topic/org.eclipse.jdt.doc.isv/reference/api/org/eclipse/jdt/core/dom/rewrite/ASTRewrite.html?utm_source=chatgpt.com "ASTRewrite (Eclipse JDT API Specification)"
[6]: https://tomassetti.me/getting-started-with-javaparser-analyzing-java-code-programmatically/?utm_source=chatgpt.com "Getting started with JavaParser: a tutorial on processing Java Code"
[7]: https://gitar.ai/blog/automated-code-refactoring?utm_source=chatgpt.com "Automated Code Refactoring - Gitar | Blog"
[8]: https://jsparrow.io/?utm_source=chatgpt.com "5 minutes instead of hours - Do Java refactoring with this plugin"
```

======

Okay, this is a significant but essential upgrade task. 

Given your requirements for an AI-driven workflow with strong human oversight, transparency, and integration with BDD/TDD practices, 
here's a specification for the first start of an AI workflow solution to upgrade your Java microservices from AWS SDK v1 to v2. 

This workflow focuses on one component at a time and ensures a developer is in the loop for crucial approval steps.

Workflow Specification: AI-Assisted AWS SDK v1 to v2 Migration

### Overall Goal:
To systematically migrate individual Java microservice components (those using AWS SDK v1 directly or in a mixed scenario) 
from AWS SDK v1 to SDK v2. 

This will be achieved using a workflow orchestrated by self-built AI agents, with integral human oversight, 
ensuring each change is validated by 100% passing BDD/TDD tests and approved via a PR with human review.

### Key Principles:
**Component-by-Component**: The workflow processes one microservice at a time.

**Human-in-the-Loop**: Developers actively participate in scoping, validation, test approval, 
handling complex cases, and final PR review.

**Transparency**: All AI actions and decisions are logged and presented in a human-readable format.

**Test-Driven**: BDD and TDD are central to verifying the correctness and preventing regressions.

**Automated where Possible, Manual where Necessary**: AI handles repetitive tasks, while humans tackle ambiguity and complex logic.

### Actors in the Workflow:
**Migration Orchestration Agent (MOA)**: The primary AI agent managing the end-to-end workflow for a single component.

**Code Analysis Agent (CAA)**: An AI agent responsible for deep code analysis, including identifying SDK v1 usage and assessing test coverage.

**Code Transformation Agent (CTA)**: An AI agent (potentially leveraging tools like OpenRewrite or custom models) that performs the automated code refactoring from SDK v1 to v2.

**Testing Agent (TA)**: An AI agent that executes test suites and reports results.

**Developer (Human)**: The developer responsible for overseeing the migration of a specific component, making key decisions, writing/approving tests, and handling complex code changes.

**Reviewer (Human)**: Another developer who reviews and approves the final Pull Request.

### Workflow Stages & Steps:
#### Stage 1: Initialisation & Scoping (Per Microservice Component)

**Component Selection & Prioritisation**:
MOA: Proposes the next microservice component for migration based on a predefined backlog or criteria (e.g., complexity, usage patterns).
Developer: Reviews the MOA's suggestion and either approves it or selects a different component.
Output: Confirmed microservice component to be migrated.

**Source Code Retrieval & Baseline**:
MOA/CAA: Fetches the latest version of the selected component's source code from the version control system. Establishes a baseline commit.

**SDK v1 Direct Usage Identification**:
CAA: Scans the codebase to precisely identify all direct AWS SDK v1 usage points. This includes:
 - com.amazonaws.* import statements.
 - SDK v1 client builder patterns (e.g., AmazonS3ClientBuilder.standard()).
 - Specific SDK v1 service client method calls.

Crucially, the CAA must differentiate between direct SDK v1 calls (scope of this task) and calls made through the internal company library (out of scope). 

This might require configuration or rules defining the internal library's packages/methods.

Output: A detailed "SDK v1 Direct Usage Report" (human-readable, listing files, line numbers, and SDK v1 constructs used).

Transparency: The report must be clear and allow the developer to verify the findings.

**Scope Validation by Developer**:
Developer: Reviews the "SDK v1 Direct Usage Report."

Confirms the accuracy of identified direct SDK v1 usage.

Approves the precise scope of changes for the migration within this component.

Output: Approved scope for migration.

#### Stage 2: Test-Driven Preparation & Contract Definition
**Existing Test Analysis (BDD & TDD)**:
CAA: Identifies existing BDD scenarios (e.g., in Gherkin *.feature files) and TDD unit tests (e.g., JUnit, Mockito) 
relevant to the functionalities that interact directly with AWS SDK v1 (as per the approved scope).

Assesses the current test coverage for these specific AWS interaction points.

Output: "Test Coverage Report" focused on relevant AWS interactions.

**Test Sufficiency Review & Augmentation Strategy**:
Developer:
Reviews the "Test Coverage Report."
Critically assesses whether the existing tests are sufficient to guarantee that the component's AWS-interacting functionality has not regressed after migration to SDK v2. These tests define the functional contract.
If gaps are identified, the developer defines the necessary new BDD scenarios or TDD test cases. These tests should focus on the behaviour of the AWS interactions.
Output: "Test Augmentation Plan" (listing existing tests to be used and specifications for any new tests required). Human-approved BDD/TDD "tests."

**New Test Implementation (If Required)**:
Developer: (Optionally assisted by an AI agent for boilerplate/stub generation for new tests).

Implements any new BDD scenarios or TDD unit tests defined in the "Test Augmentation Plan."

Ensures all relevant existing and newly added tests pass with the current SDK v1 implementation before any migration occurs. This confirms the baseline behaviour.

Output: An updated test suite. Confirmation that all relevant tests pass on the SDK v1 codebase.

#### Stage 3: AI-Powered Code Migration
**Automated Code Transformation to SDK v2**:
CTA: Applies automated refactoring techniques to the scoped parts of the codebase. This will likely involve:

Using OpenRewrite with the software.amazon.awssdk.v2migration.AwsSdkJavaV1ToV2 recipe as a foundation.

Potentially using custom OpenRewrite recipes developed by developer to handle specific internal patterns or common issues not covered by the standard recipe.

If "self-built AI agents" means more advanced capabilities, this could involve fine-tuned LLMs or custom JavaParser-based transformation scripts guided by AI.

**Key transformations include**:
Updating import statements from com.amazonaws.* to software.amazon.awssdk.*.

Converting SDK v1 client builders to their SDK v2 counterparts (e.g., fluent builders, create() methods).

Adapting request and response object instantiation and method calls.

Refactoring exception handling (from v1 checked exceptions to v2 unchecked exceptions).

Migrating configuration for credentials, regions, and HTTP clients.

Output:
A new branch in version control with the transformed codebase.

A detailed "Transformation Log" (human-readable, listing every change made, the rule/recipe applied, and before/after snippets for clarity).

Transparency: The log is crucial for the developer to understand the AI's actions.

Identification of Complex or Unhandled Cases:

CTA:
During the transformation, identifies and flags code sections where:

Automated migration failed or has low confidence.

Known complex patterns exist (e.g., intricate waiter logic, custom retry mechanisms directly using v1 features, specific paginator usage).

Ambiguity requires human interpretation.

(Optional Advanced Feature) The CTA might suggest several potential SDK v2 patterns for these complex cases, citing AWS documentation or examples.

Output: "Complex Cases Report" detailing these areas, with links to the code and the Transformation Log entries.

#### Stage 4: Iterative Refinement & Verification (Human-AI Collaboration)
**Developer Review of Automated Changes & Complex Cases**:
Developer:

Reviews the "Transformation Log" and the "Complex Cases Report."

Examines the AI-transformed code, paying close attention to the flagged complex areas.

Manually refactors the complex cases to use SDK v2 correctly, applying their expertise and consulting AWS SDK v2 documentation.

Output: 
Developer-refined codebase.

Compilation & Automated Testing Execution:

TA:
Compiles the refined, migrated codebase.

Executes the full suite of approved BDD and TDD tests (from Stage 2) against the migrated code.


Output: 
Compilation status. Detailed "Test Execution Report" (listing all tests, their pass/fail status, and any error messages/stack traces for failures).

Transparency: Clear linkage between test failures and specific code areas.


**Debugging & Correction Cycle**:
Developer:

If compilation fails or any tests fail, the developer analyzes the "Test Execution Report" and debugs the migrated code.

(Optional AI Assistance) The CAA or CTA might provide diagnostic hints based on common v1-to-v2 migration errors or analyze stack traces to suggest potential causes.

The developer makes necessary corrections.


Loop: The developer commits fixes, and the TA re-runs compilation and tests (Step 4.2). 

This cycle repeats until the codebase compiles successfully and 100% of the BDD/TDD tests pass.

Output: A fully migrated and tested codebase where all relevant BDD/TDD tests pass.

#### Stage 5: Quality Assurance & Deployment Preparation
**Pull Request (PR) Generation**:
MOA/CTA:
Automates the creation of a Pull Request in the version control system.

The PR description is auto-populated with:

A clear title indicating the component and migration type.

A summary of the component migrated.

Links to the "SDK v1 Direct Usage Report," "Transformation Log," and "Complex Cases Report."

Explicit confirmation of 100% BDD and TDD test pass rate, with a link to the final "Test Execution Report."

Notes on any significant manual interventions or assumptions made.

Suggested reviewers (e.g., team lead, other developers familiar with the component).

Output: A drafted Pull Request.

Developer Final PR Review & Polish:

**Developer (who oversaw the migration)**:
Reviews the auto-generated PR for accuracy, completeness, and clarity.

Adds any further context, comments, or specific points for reviewers to consider.

Ensures the PR title, description, and linked issues (if any) meet BBC's standards.

Output: A finalised PR, ready for formal human review.

#### Stage 6: Human Review & Merge
**Peer Code Review**:
**Reviewer(s) (at least one other human developer)**:
**Conduct a thorough code review of the PR. Key focus areas**:

Correctness and completeness of the SDK v2 migration.

Adherence to AWS SDK v2 best practices (client lifecycle, error handling, configuration).

Readability, maintainability, and overall code quality.

Confirmation that the tests adequately cover the changes and verify functionality.

Absence of regressions.
P
rovide feedback, ask questions, and request changes if necessary.

Output: Review comments, approval, or change requests.

**Addressing Review Feedback (If Any)**:
**Developer (who oversaw the migration)**: Addresses any concerns or suggestions from the reviewers. 
This might involve further code changes and re-running the TA (Step 4.2) to ensure tests still pass.

Loop: Iterate with reviewers until all concerns are addressed.

**PR Approval & Merge**:
Reviewer(s): Approve the PR.

Developer (or designated integrator): Merges the approved PR into the main development branch.

Output: The microservice component is now upgraded to AWS SDK v2 in the main codebase.

#### Stage 7: Post-Merge & Monitoring
Deployment: The updated microservice is deployed to staging/production environments through standard CI/CD pipelines.

Monitoring:

Closely monitor the component's behavior in production, focusing on metrics related to its AWS interactions (e.g., latency, error rates, costs).

(Optional AI Assistance) AI agents could be configured to monitor logs and metrics for anomalies post-deployment that might relate to the SDK migration.

This workflow provides a structured, AI-assisted yet human-controlled process for your SDK upgrades, aligning with your development practices and ensuring transparency and accountability. 
The "self-built AI agents" would be the custom software you develop to perform the MOA, CAA, CTA, and TA roles, integrating existing tools where beneficial.


====

Okay, this is a great next step! We'll focus on replacing the OpenAI client with a Gemini client, leveraging function calling for more reliable structured output.

Here's the plan and then the updated code:

**Plan to Update for Gemini:**

1.  **Install Google Generative AI SDK:**
    *   Add `google-generativeai` to your `pyproject.toml`.
    *   Run `poetry lock` and `poetry install`.

2.  **API Key Handling:**
    *   The new client will expect the `GOOGLE_API_KEY` environment variable.
    *   Update documentation (README) to reflect this.

3.  **Configuration for Model Name:**
    *   Allow specifying the Gemini model name via an environment variable (e.g., `GEMINI_MODEL_NAME`) or in `context.json` (e.g., `global_settings.gemini_model_name`).
    *   Default to a reasonable model like `gemini-1.5-pro-latest`.

4.  **Create `GeminiClient` (`gemini_client.py`):**
    *   This new class will encapsulate interactions with the Gemini API.
    *   **`__init__`**:
        *   Initialize `genai.configure(api_key=...)`.
        *   Initialize `genai.GenerativeModel(model_name=...)`.
    *   **`generate_code` method:**
        *   Define a `Tool` with a `FunctionDeclaration` for Gemini. This declaration will describe the function Gemini should "call" to return the structured data (i.e., your `updated_files` schema).
        *   Construct the prompt. The user prompt might need to be adjusted to explicitly ask Gemini to use the provided tool.
        *   Call `model.generate_content(..., tools=[your_tool])`.
        *   Process the response:
            *   Extract the `FunctionCall` part from the response.
            *   The arguments of this `FunctionCall` (`response.candidates[0].content.parts[0].function_call.args`) will be a dictionary that *should* match your desired JSON structure.
            *   No complex continuation logic should be needed if function calling works as expected.
        *   Handle errors: If the LLM doesn't call the function or if there are API errors, raise appropriate custom exceptions (we can reuse/rename `OpenAIClientError` and `OpenAIResponseError` to be more generic `LLMClientError` and `LLMResponseError`).

5.  **Update `main.py`:**
    *   Modify `main.py` to instantiate and use `GeminiClient` instead of `OpenAIClient`.
    *   Pass any necessary model configuration to the `GeminiClient`.

6.  **Update `repo_processor.py`:**
    *   Change type hints and import from `OpenAIClient` to `GeminiClient`.
    *   Update exception handling to catch `LLMClientError` / `LLMResponseError` if we made them generic.

7.  **Adjust Prompts:**
    *   The main user-facing prompt (`prompt_general.txt` or similar) might need slight adjustments to better guide Gemini, especially if you add an instruction to use the provided tool.
    *   The system prompt within `GeminiClient` will also be specific to guiding tool use.

8.  **Update Tests:**
    *   **`tests/test_gemini_client.py` (New File):**
        *   Create unit tests for `GeminiClient`, mocking the `google.generativeai` library calls.
        *   Test successful function call parsing.
        *   Test scenarios where Gemini might not call the function or returns unexpected data.
    *   **`tests/test_repo_processor.py`:**
        *   Update `@patch` decorators if the client class name or method path changes in `RepoProcessor`'s imports.
        *   The mock for `generate_code` should now return a dictionary that simulates the `args` of a Gemini `FunctionCall`.
    *   **`tests/test_integration.py`:**
        *   Change the primary client mock from `OpenAIClient` to `GeminiClient`.
        *   The `mock_llm_responses_from_fixtures` side_effect function will need to ensure its fixture JSON files (`tests/fixtures/llm_responses/`) contain the JSON structure that `GeminiClient.generate_code` is expected to return (which is directly the parsed `args` from the function call).

---

**Updated Code:**

**1. `pyproject.toml` (add `google-generativeai`)**
```toml
[tool.poetry]
package-mode = false
name = "not-in-kansas"
version = "0.1.0"
description = ""
authors = ["errolelliott <ezzy.elliott@gmail.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11" # You were using 3.11 in your last test run output
openai = "^1.53.0" # Keep for now, can be removed if fully switching
langchain = "^0.3.7" # Keep for now, might be useful later
google-generativeai = "^0.7.0" # Added Gemini SDK

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```
**Action:** Run `poetry lock && poetry install` after updating.

---

**2. `exceptions.py` (Rename to be more generic)**
```python
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
```

---

**3. `gemini_client.py` (New File)**
```python
import logging
import json
import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold, Tool, FunctionDeclaration # Import necessary types

from exceptions import LLMClientError, LLMResponseError # Use renamed exceptions

# Define the schema for the function Gemini should call
# This mirrors the JSON schema previously used with OpenAI
FILE_UPDATE_SCHEMA = {
    "type": "object",
    "properties": {
        "updated_files": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The file path relative to the repository root.",
                    },
                    "updated_content": {
                        "type": "string",
                        "description": (
                            "The full updated content of the file. "
                            "If no changes are needed for a file, this should be the original content."
                        ),
                    },
                },
                "required": ["file_path", "updated_content"],
            },
        }
    },
    "required": ["updated_files"],
}

class GeminiClient:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            # Fallback to OpenAI key if GOOGLE_API_KEY is not set, for smoother transition during dev.
            # Remove this fallback once fully on Gemini.
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                logging.warning("GOOGLE_API_KEY not set, falling back to OPENAI_API_KEY for Gemini client init. This is for transition and should be updated.")
            else:
                raise ValueError("Neither GOOGLE_API_KEY nor OPENAI_API_KEY environment variable is set.")
        
        genai.configure(api_key=api_key)
        
        self.model_name = os.getenv('GEMINI_MODEL_NAME', "gemini-1.5-pro-latest")
        self.model = None # Will be configured by set_model_from_config or on first use
        self.tool = Tool(
            function_declarations=[
                FunctionDeclaration(
                    name="update_code_files",
                    description="Updates specified code files and returns their new content.",
                    parameters=FILE_UPDATE_SCHEMA,
                )
            ]
        )
        self.generation_config = GenerationConfig(
            temperature=0.0, # For deterministic output
            # top_p= Not typically used with temperature 0
            # top_k= Not typically used with temperature 0
        )
        # Safety settings - adjust as needed. For code generation, some categories might be less restrictive.
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        logging.info(f"GeminiClient initialized. Model to be used: {self.model_name}")


    def set_model_from_config(self, global_settings: dict):
        """Allows setting model name from config if not set by env var."""
        if 'GEMINI_MODEL_NAME' not in os.environ: # Env var takes precedence
            self.model_name = global_settings.get("gemini_model_name", self.model_name)
        
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
            tools=[self.tool] # Pass tool during model initialization
        )
        logging.info(f"Using Gemini model: {self.model_name}")

    def generate_code(self, prompt_template: str, context: dict) -> dict:
        if not self.model:
            # This would happen if set_model_from_config was not called.
            # Or, you can initialize self.model in __init__ if global_settings is passed there.
            logging.warning("Gemini model not explicitly configured via set_model_from_config. Initializing with default/env model name.")
            self.set_model_from_config({}) # Initialize with default

        logging.debug(f"Generating code with Gemini API (Model: {self.model_name})")

        component_name = context.get('repository', '')
        # Ensure prompt is formatted correctly for Gemini, especially if using function calling.
        # It's often good to explicitly instruct the model to use the tool.
        user_prompt_instruction = (
            "Please analyze the provided code files based on the initial instructions. "
            "Use the 'update_code_files' tool to return the updated content for all specified target files. "
            "If a file does not require changes, return its original content."
        )
        
        # The 'prompt_template' is the core instruction (e.g., upgrade Java 8 to 11)
        # The 'context' contains the file contents.
        final_user_prompt = f"{prompt_template.format(component_name=component_name)}\n\n{user_prompt_instruction}\n\nContext (current file contents):\n{json.dumps(context.get('current_files', {}), indent=2)}"

        messages = [
            # Gemini works well with a direct user prompt containing all info for simpler tasks.
            # For more complex chat, you might build up a history.
            {'role': 'user', 'content': final_user_prompt}
        ]
        
        logging.debug(f"Sending to Gemini: {messages}")

        try:
            response = self.model.generate_content(
                messages,
                # Tools are now part of the model's configuration, but can be overridden here if needed
                # tool_config={'function_calling_config': "AUTO"} # AUTO is default
            )
            logging.debug(f"Raw Gemini response object: {response}")

            if not response.candidates or not response.candidates[0].content.parts:
                raise LLMResponseError("Gemini response is empty or malformed (no candidates/parts).")

            # Expecting the model to use the function call
            part = response.candidates[0].content.parts[0]
            if not part.function_call:
                error_message = "Gemini did not call the 'update_code_files' function as expected."
                logging.error(error_message + f" Response text: {part.text if hasattr(part, 'text') else 'N/A'}")
                raise LLMResponseError(error_message + f" Response text: {part.text if hasattr(part, 'text') else 'N/A'}")

            function_call_args = dict(part.function_call.args)
            logging.debug(f"Gemini function call arguments: {function_call_args}")

            # Validate the structure (optional, but good practice)
            if "updated_files" not in function_call_args or not isinstance(function_call_args["updated_files"], list):
                raise LLMResponseError("Gemini function call 'args' missing 'updated_files' list or it's not a list.")
            
            # The function_call_args should directly be the dictionary we want
            return function_call_args

        except Exception as e:
            logging.error(f"Gemini API call failed: {e}", exc_info=True)
            # Catch specific genai errors if they exist and are more informative
            # For now, wrap generic Exception into LLMClientError
            raise LLMClientError(f"Gemini API call failed: {e}") from e

```

---

**4. `main.py` (Updated to use `GeminiClient`)**
```python
#!/usr/bin/env python3

import argparse
import json
import logging
import sys
import os

# from openai_client import OpenAIClient # Comment out or remove
from gemini_client import GeminiClient # Import new client
from github_client import GitHubClient
from repo_processor import RepoProcessor
from status_enums import RepoStatus
from exceptions import BaseAppException # For catching general app errors

def main():
    parser = argparse.ArgumentParser(description="Automate tech debt fixes across multiple repositories")
    parser.add_argument("--prompt-file", required=True, help="Path to the prompt text file")
    parser.add_argument("--context-file", required=True, help="Path to JSON file containing context")
    parser.add_argument("--repo-path", help="Optional path to a single pre-cloned repository for local processing.")
    parser.add_argument("--repo-name", help="Name of the single repository to process (required if --repo-path is used and repo not in context file).")
    parser.add_argument("--keep-temp-dir", action="store_true", help="Keep temporary directories after processing (for debugging).")
    parser.add_argument("--llm-provider", default="gemini", choices=["gemini", "openai"], help="Specify the LLM provider (gemini or openai)")


    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    try:
        with open(args.context_file, 'r') as f:
            context_data = json.load(f)
    except FileNotFoundError:
        logging.error(f"Context file not found: {args.context_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from context file: {args.context_file}")
        sys.exit(1)

    try:
        with open(args.prompt_file, 'r') as f:
            prompt = f.read()
    except FileNotFoundError:
        logging.error(f"Prompt file not found: {args.prompt_file}")
        sys.exit(1)

    llm_client = None
    try:
        if args.llm_provider == "gemini":
            google_api_key = os.getenv('GOOGLE_API_KEY')
            if not google_api_key:
                logging.warning("GOOGLE_API_KEY environment variable is not set. Gemini calls will fail if not mocked.")
            llm_client = GeminiClient()
            llm_client.set_model_from_config(context_data.get("global_settings", {}))
        elif args.llm_provider == "openai":
            from openai_client import OpenAIClient # Import only if needed
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                logging.warning("OPENAI_API_KEY environment variable is not set. OpenAI calls will fail if not mocked.")
            llm_client = OpenAIClient()
            llm_client.set_model_from_config(context_data.get("global_settings", {})) # Assuming similar method
        else:
            logging.error(f"Unsupported LLM provider: {args.llm_provider}")
            sys.exit(1)

    except ValueError as e: 
        logging.error(f"Error initializing LLM client: {e}")
        sys.exit(1)
    except BaseAppException as e: # Catch our custom app exceptions from client init
        logging.error(f"Error initializing LLM client: {e}")
        sys.exit(1)


    github_client = GitHubClient()
    results = {}

    if args.repo_path:
        if not args.repo_name:
            args.repo_name = os.path.basename(args.repo_path)
            logging.info(f"Inferred repo_name as '{args.repo_name}' from --repo-path.")
            if args.repo_name not in context_data.get("repository_settings", {}):
                if "repository_settings" not in context_data:
                    context_data["repository_settings"] = {}
                context_data["repository_settings"][args.repo_name] = {} 
                logging.info(f"Using global settings for locally processed repo: {args.repo_name}")
        repos_to_process = [args.repo_name]
        logging.info(f"Processing single specified repository: {args.repo_name} at path {args.repo_path}")
    else:
        repos_to_process = context_data.get("repositories", [])
        if not repos_to_process:
            logging.error("No repositories specified in context file and --repo-path not used.")
            sys.exit(1)

    for repo_name in repos_to_process:
        current_repo_path_arg = args.repo_path if args.repo_path and repo_name == args.repo_name else None
        
        processor = RepoProcessor(
            repo_name,
            context_data,
            prompt,
            llm_client, # Pass the initialized LLM client
            github_client,
            repo_path=current_repo_path_arg,
            keep_temp_dir=args.keep_temp_dir
        )
        processor.process()
        results[repo_name] = processor.status

    logging.info("\nProcessing Complete. Summary:")
    for repo_name, status in results.items():
        logging.info(f"{repo_name}: {status}")


if __name__ == "__main__":
    main()
```

---

**5. `repo_processor.py` (Minor updates for new exceptions)**
   ```python
   import logging
   import os
   import tempfile
   import shutil

   # from openai_client import OpenAIClient, OpenAIClientError, OpenAIResponseError # Old
   # Assuming a generic LLMClient interface in the future, or specific client for now
   # For this step, we assume main.py passes an initialized GeminiClient instance
   # (or an OpenAIClient instance if that path is taken by main.py)
   # So, the type hint for openai_client can be more generic or specific.
   from gemini_client import GeminiClient # Or from llm_client_base import LLMClientBase
   from github_client import GitHubClient, GitHubClientError
   from test_runner import TestRunner, TestRunnerError
   from status_enums import RepoStatus
   from exceptions import BaseAppException, LLMClientError, LLMResponseError # Use new generic LLM exceptions


   class RepoProcessor:
       def __init__(self, repo_name: str, context: dict, prompt: str,
                    llm_client: GeminiClient, # Changed type hint to GeminiClient (or a base class)
                    github_client: GitHubClient,
                    repo_path: str | None = None,
                    keep_temp_dir: bool = False):
           self.repo_name = repo_name
           self.context = context
           self.prompt = prompt
           self.llm_client = llm_client # Renamed from openai_client
           self.github_client = github_client
           # ... (rest of __init__ largely the same, just ensure openai_client is now llm_client) ...
           self.provided_repo_path = repo_path 
           self.repo_path = repo_path 
           self.status = RepoStatus.NOT_PROCESSED
           self.keep_temp_dir = keep_temp_dir

           self.global_settings = context.get("global_settings", {})
           self.repo_settings = context.get("repository_settings", {}).get(repo_name, {})

           self.build_command = self._get_setting("build_command", "make test")
           self.target_files = self._get_setting("target_files", [])
           self.reviewers = self._get_setting("reviewers", [])
           self.repo_base_url = self._get_setting("repo_base_url", "https://github.com/bbc/")
           self.branch_name_template = self._get_setting("branch_name_template", "automated-tech-debt-fix/{repo_name}")
           self.commit_message_template = self._get_setting("commit_message_template", "Automated update: Applied tech debt fix for {repo_name}")
           self.pr_title_template = self._get_setting("pr_title_template", "[Automated PR] Tech debt fix for {repo_name}")
           self.pr_body_template = self._get_setting("pr_body_template", "This PR was created automatically to apply a tech debt fix for {repo_name}.\n\nPlease review and merge.")
           
           logging.debug(f"Build command for {self.repo_name}: {self.build_command}")
           self.test_runner = TestRunner(self.build_command)


       def _get_setting(self, key: str, default: any = None) -> any:
           return self.repo_settings.get(key, self.global_settings.get(key, default))

       def process(self):
           logging.info(f"Processing repository {self.repo_name}")
           if self.provided_repo_path:
               self.repo_path = self.provided_repo_path
               logging.debug(f"Using provided repo path: {self.repo_path}")
               self._process_repository()
           else:
               with tempfile.TemporaryDirectory() as tmpdirname:
                   self.repo_path = os.path.join(tmpdirname, self.repo_name)
                   logging.debug(f"Created temporary directory: {self.repo_path}")
                   try:
                       self._process_repository()
                   finally:
                       if self.keep_temp_dir and os.path.exists(tmpdirname): # Check if dir still exists
                           logging.info(f"Keeping temporary directory: {tmpdirname} (repo: {self.repo_path})")
                           # To truly keep it, you'd need to copy it out or not use TemporaryDirectory
                           # For now, this mostly prevents it from being deleted if keep_temp_dir is true
                           # but this part of the logic is tricky with context managers.
                           # A more robust "keep" might involve copying to a known location.
                           pass


       def _process_repository(self):
           try:
               repo_full_url = f"{self.repo_base_url.rstrip('/')}/{self.repo_name}"
               logging.debug(f"Repository URL: {repo_full_url}")
               logging.debug(f"Repository path for operations: {self.repo_path}")

               if not self.provided_repo_path:
                   logging.info(f"Cloning repository {self.repo_name} into {self.repo_path}")
                   self.github_client.clone_repo(repo_full_url, self.repo_path)
               else:
                   logging.info(f"Skipping clone for provided repo_path: {self.repo_path}")

               branch_name = self.branch_name_template.format(repo_name=self.repo_name)
               logging.info(f"Ensuring branch {branch_name} (create or reset)")
               self.github_client.create_or_reset_branch(self.repo_path, branch_name)

               num_files_changed = self.apply_changes()
               if num_files_changed == 0:
                   logging.info(f"No changes applied to {self.repo_name} by LLM or no target files to process.")
                   self.status = RepoStatus.SUCCESS_NO_CHANGES
                   return
               elif num_files_changed < 0:
                   # Status should have been set by apply_changes
                   return

               logging.info(f"Running tests for {self.repo_name}")
               tests_passed, test_output = self.test_runner.run_tests(self.repo_path)
               if not tests_passed:
                   logging.error(f"Tests failed in {self.repo_name}. Output:\n{test_output}")
                   self.status = RepoStatus.ERROR_TESTS_FAILED
                   return
               logging.info(f"Tests passed for {self.repo_name}. Output:\n{test_output}")

               commit_message = self.commit_message_template.format(repo_name=self.repo_name)
               logging.info(f"Committing changes in {self.repo_name}")
               self.github_client.commit_changes(self.repo_path, commit_message)

               logging.info(f"Pushing branch {branch_name}")
               self.github_client.push_branch(self.repo_path, branch_name)

               pr_title = self.pr_title_template.format(repo_name=self.repo_name)
               pr_body = self.pr_body_template.format(repo_name=self.repo_name)
               logging.info(f"Creating pull request for {self.repo_name}")
               self.github_client.create_pull_request(self.repo_path, pr_title, pr_body, self.reviewers)

               self.status = RepoStatus.SUCCESS_PR_CREATED

           except GitHubClientError as e:
               logging.error(f"GitHub client error processing {self.repo_name}: {e}", exc_info=True)
               if "clone" in str(e).lower(): self.status = RepoStatus.ERROR_CLONING
               elif "branch" in str(e).lower(): self.status = RepoStatus.ERROR_BRANCHING
               # ... (other specific GitHub errors) ...
               else: self.status = RepoStatus.ERROR_GENERIC
           except TestRunnerError as e:
               logging.error(f"Test runner error for {self.repo_name}: {e}", exc_info=True)
               self.status = RepoStatus.ERROR_TESTS_FAILED
           except LLMClientError as e: # Catch generic LLM client error
               logging.error(f"LLM client error processing {self.repo_name}: {e}", exc_info=True)
               self.status = RepoStatus.ERROR_OPENAI_API # Keeping old enum for now, or map to new generic
           except LLMResponseError as e: # Catch generic LLM response error
               logging.error(f"LLM response error processing {self.repo_name}: {e}", exc_info=True)
               self.status = RepoStatus.ERROR_OPENAI_RESPONSE_FORMAT # Same as above
           except BaseAppException as e:
               logging.error(f"Application error processing {self.repo_name}: {e}", exc_info=True)
               self.status = RepoStatus.ERROR_GENERIC
           except Exception as e:
               logging.error(f"Unexpected error processing {self.repo_name}: {e}", exc_info=True)
               self.status = RepoStatus.ERROR_GENERIC

       def apply_changes(self) -> int:
           logging.debug(f"Applying changes to {self.repo_name} in path {self.repo_path}")
           repo_context = {
               "repository": self.repo_name,
               "repo_path": self.repo_path,
               "target_files": self.target_files,
           }
           current_files = {}
           found_any_target_file = False
           if not self.target_files: # If target_files list is empty
                logging.info(f"No target files specified for {self.repo_name} in context. Skipping LLM call.")
                self.status = RepoStatus.SUCCESS_NO_CHANGES
                return 0

           for file_rel_path in self.target_files:
               full_path = os.path.join(self.repo_path, file_rel_path)
               if os.path.exists(full_path):
                   found_any_target_file = True
                   with open(full_path, 'r', encoding='utf-8') as f:
                       current_files[file_rel_path] = f.read()
                   logging.debug(f"Read content of {file_rel_path} in {self.repo_name}")
               else:
                   logging.warning(f"Target file {file_rel_path} does not exist in {self.repo_path}")

           if not found_any_target_file:
               logging.error(f"None of the target files {self.target_files} were found in {self.repo_path}.")
               self.status = RepoStatus.ERROR_TARGET_FILES_NOT_FOUND_ALL
               return -1
           
           repo_context["current_files"] = current_files

           try:
               response_data = self.llm_client.generate_code(self.prompt, repo_context) # Use self.llm_client
           except LLMClientError as e:
               logging.error(f"LLM client error during apply_changes for {self.repo_name}: {e}")
               self.status = RepoStatus.ERROR_OPENAI_API # Or map to a more generic LLM_API_ERROR
               return -1
           except LLMResponseError as e:
               logging.error(f"LLM response format error for {self.repo_name}: {e}")
               self.status = RepoStatus.ERROR_OPENAI_RESPONSE_FORMAT # Or map to generic LLM_RESPONSE_ERROR
               return -1

           updated_files_data = response_data.get("updated_files")
           if not updated_files_data:
               logging.warning(f"No updated files returned by LLM for {self.repo_name}")
               self.status = RepoStatus.SUCCESS_NO_CHANGES
               return 0

           files_changed_count = 0
           for file_info in updated_files_data:
               file_path = file_info.get('file_path')
               updated_code = file_info.get('updated_content')

               if not file_path or updated_code is None:
                   logging.warning(f"Missing 'file_path' or 'updated_content' in LLM response: {file_info}")
                   continue
               
               if file_path not in self.target_files:
                   logging.warning(f"LLM tried to update non-target file '{file_path}'. Skipping.")
                   continue
               
               full_write_path = os.path.join(self.repo_path, file_path)
               try:
                   os.makedirs(os.path.dirname(full_write_path), exist_ok=True)
                   with open(full_write_path, 'w', encoding='utf-8') as f:
                       f.write(updated_code)
                   logging.debug(f"Updated file {file_path} in {self.repo_name}")
                   files_changed_count += 1
               except IOError as e:
                   logging.error(f"Failed to write updated file {full_write_path}: {e}")
                   self.status = RepoStatus.ERROR_APPLYING_CHANGES
                   # Potentially return -1 here if one write failure is critical
           
           if files_changed_count == 0 and updated_files_data:
               logging.warning(f"LLM returned data but no valid target files were updated for {self.repo_name}.")
               self.status = RepoStatus.SUCCESS_NO_CHANGES # Or a more specific status
               return 0
               
           return files_changed_count
   ```

---

**6. `tests/test_gemini_client.py` (New File)**
   ```python
   import unittest
   from unittest.mock import patch, MagicMock
   import os
   import json

   from gemini_client import GeminiClient, FILE_UPDATE_SCHEMA # Assuming FILE_UPDATE_SCHEMA is accessible
   from exceptions import LLMClientError, LLMResponseError
   import google.generativeai as genai # For mocking specific Gemini types

   class TestGeminiClient(unittest.TestCase):

       def setUp(self):
           # Store original env var if exists and clear it for tests
           self.original_google_api_key = os.environ.get("GOOGLE_API_KEY")
           self.original_openai_api_key = os.environ.get("OPENAI_API_KEY")
           os.environ["GOOGLE_API_KEY"] = "test_google_api_key" # Mock API key
           if "OPENAI_API_KEY" in os.environ:
               del os.environ["OPENAI_API_KEY"]


       def tearDown(self):
           # Restore original env vars
           if self.original_google_api_key:
               os.environ["GOOGLE_API_KEY"] = self.original_google_api_key
           elif "GOOGLE_API_KEY" in os.environ:
               del os.environ["GOOGLE_API_KEY"]
           
           if self.original_openai_api_key:
               os.environ["OPENAI_API_KEY"] = self.original_openai_api_key
           elif "OPENAI_API_KEY" in os.environ:
               del os.environ["OPENAI_API_KEY"]


       @patch('google.generativeai.GenerativeModel')
       def test_generate_code_successful_function_call(self, MockGenerativeModel):
           mock_model_instance = MockGenerativeModel.return_value
           
           expected_response_args = {
               "updated_files": [
                   {"file_path": "test.java", "updated_content": "public class Test {}"}
               ]
           }
           # Simulate Gemini's response structure for a function call
           mock_function_call = MagicMock()
           mock_function_call.name = "update_code_files"
           mock_function_call.args = expected_response_args # Gemini SDK makes this a dict-like object
           
           mock_part = MagicMock()
           mock_part.function_call = mock_function_call
           
           mock_candidate = MagicMock()
           mock_candidate.content.parts = [mock_part]
           
           mock_genai_response = MagicMock()
           mock_genai_response.candidates = [mock_candidate]
           mock_model_instance.generate_content.return_value = mock_genai_response

           client = GeminiClient()
           client.set_model_from_config({}) # Initialize model
           
           response = client.generate_code("prompt", {"repository": "repo1", "current_files": {"test.java":"old"}})
           
           self.assertEqual(response, expected_response_args)
           mock_model_instance.generate_content.assert_called_once()
           # You can add more assertions about the prompt passed to generate_content

       @patch('google.generativeai.GenerativeModel')
       def test_generate_code_no_function_call(self, MockGenerativeModel):
           mock_model_instance = MockGenerativeModel.return_value
           
           mock_part = MagicMock()
           mock_part.function_call = None # Simulate no function call
           mock_part.text = "I am sorry, I cannot fulfill that request using the tool." # Example text response
           
           mock_candidate = MagicMock()
           mock_candidate.content.parts = [mock_part]
           
           mock_genai_response = MagicMock()
           mock_genai_response.candidates = [mock_candidate]
           mock_model_instance.generate_content.return_value = mock_genai_response

           client = GeminiClient()
           client.set_model_from_config({})
           
           with self.assertRaisesRegex(LLMResponseError, "Gemini did not call the 'update_code_files' function"):
               client.generate_code("prompt", {"repository": "repo1"})

       @patch('google.generativeai.GenerativeModel')
       def test_generate_code_api_error(self, MockGenerativeModel):
           mock_model_instance = MockGenerativeModel.return_value
           mock_model_instance.generate_content.side_effect = genai.types.generation_types.BlockedPromptException("Simulated API block")

           client = GeminiClient()
           client.set_model_from_config({})
           
           with self.assertRaises(LLMClientError): # Should catch the wrapped error
               client.generate_code("prompt", {"repository": "repo1"})

       def test_init_no_api_key(self):
           if "GOOGLE_API_KEY" in os.environ:
               del os.environ["GOOGLE_API_KEY"]
           if "OPENAI_API_KEY" in os.environ: # ensure fallback is also cleared
               del os.environ["OPENAI_API_KEY"]
               
           with self.assertRaisesRegex(ValueError, "Neither GOOGLE_API_KEY nor OPENAI_API_KEY environment variable is set."):
               GeminiClient()

   if __name__ == '__main__':
       unittest.main()
   ```

---

**7. `tests/test_repo_processor.py` (Update mocks for `GeminiClient`)**

The existing structure of `test_repo_processor.py` is mostly good because it mocks the `OpenAIClient` (which we'll now treat as `GeminiClient` in terms of patching) at a high level. The main change is the path used in `@patch`.

```python
import unittest
from unittest.mock import MagicMock, patch
# ... other imports ...
# from openai_client import OpenAIClient, OpenAIClientError, OpenAIResponseError # Old
from gemini_client import GeminiClient # Import the new client
from exceptions import LLMClientError, LLMResponseError # Use new exceptions

class TestRepoProcessor(unittest.TestCase):
    # ... setUp and tearDown largely the same ...
    def setUp(self):
        self.temp_dir_base = tempfile.mkdtemp()
        self.repo_name = "microservice-repo1"
        self.mock_context = {
            "global_settings": {
                "reviewers": ["dev1", "dev2"],
                "build_command": "echo 'mock test run'",
                "target_files": ["pom.xml", "src/main/App.java"],
                "repo_base_url": "https://github.com/mockorg/",
                "gemini_model_name": "gemini-test-model" # Added for GeminiClient
            },
            "repository_settings": {
                self.repo_name: {
                    "target_files": ["pom.xml"] 
                }
            }
        }
        self.prompt = "Test prompt for {component_name}"
        self.provided_test_repo_path = os.path.join(self.temp_dir_base, "provided_repo", self.repo_name)
        os.makedirs(os.path.join(self.provided_test_repo_path, "src/main"), exist_ok=True)
        with open(os.path.join(self.provided_test_repo_path, "pom.xml"), "w") as f:
            f.write("<project_original_in_provided_path></project_original_in_provided_path>")
        with open(os.path.join(self.provided_test_repo_path, "src/main/App.java"), "w") as f:
            f.write("public class OriginalApp {}")

    def tearDown(self):
        shutil.rmtree(self.temp_dir_base)

    @patch('repo_processor.GitHubClient')
    @patch('repo_processor.TestRunner')
    # Patch the new GeminiClient where it's used by RepoProcessor
    def test_full_successful_process(self, MockTestRunner, MockGitHubClient):
        # Instead of patching GeminiClient directly, we'll pass a MagicMock instance
        # This makes the test setup simpler if RepoProcessor's __init__ signature is stable.
        mock_llm_client_instance = MagicMock(spec=GeminiClient) # Mock the instance passed
        mock_github_instance = MockGitHubClient.return_value
        mock_test_runner_instance = MockTestRunner.return_value

        def fake_clone_repo(repo_url, dest_path):
            # ... (same as before)
            logging.debug(f"MOCK clone_repo: Simulating clone of {repo_url} to {dest_path}")
            os.makedirs(os.path.join(dest_path, "src/main"), exist_ok=True)
            with open(os.path.join(dest_path, "pom.xml"), "w") as f:
                f.write("<project_cloned></project_cloned>")
            with open(os.path.join(dest_path, "src/main/App.java"), "w") as f:
                f.write("public class ClonedApp {}")
        mock_github_instance.clone_repo.side_effect = fake_clone_repo

        mock_llm_client_instance.generate_code.return_value = {
            "updated_files": [{"file_path": "pom.xml", "updated_content": "<project_updated_by_llm></project_updated_by_llm>"}]
        }
        mock_test_runner_instance.run_tests.return_value = (True, "Tests passed output")

        processor = RepoProcessor(self.repo_name, self.mock_context, self.prompt,
                                  mock_llm_client_instance, # Pass the mock LLM client
                                  mock_github_instance, repo_path=None)
        processor.process()

        self.assertEqual(processor.status, RepoStatus.SUCCESS_PR_CREATED)
        # ... (rest of assertions are fine, just ensure generate_code is called on mock_llm_client_instance) ...
        mock_llm_client_instance.generate_code.assert_called_once()
        args_list = mock_llm_client_instance.generate_code.call_args_list
        call_args, _ = args_list[0]
        passed_context = call_args[1]
        self.assertEqual(passed_context["current_files"]["pom.xml"], "<project_cloned></project_cloned>")


    @patch('repo_processor.GitHubClient')
    @patch('repo_processor.TestRunner')
    def test_process_with_provided_repo_path(self, MockTestRunner, MockGitHubClient):
        mock_llm_client_instance = MagicMock(spec=GeminiClient)
        # ... (rest of this test is similar, just use mock_llm_client_instance)
        mock_github_instance = MockGitHubClient.return_value
        mock_test_runner_instance = MockTestRunner.return_value

        mock_llm_client_instance.generate_code.return_value = {
            "updated_files": [{"file_path": "pom.xml", "updated_content": "<project>updated by test in provided path</project>"}]
        }
        mock_test_runner_instance.run_tests.return_value = (True, "Tests passed")

        processor = RepoProcessor(self.repo_name, self.mock_context, self.prompt,
                                  mock_llm_client_instance, mock_github_instance, repo_path=self.provided_test_repo_path)
        processor.process()
        
        mock_github_instance.clone_repo.assert_not_called() 
        self.assertEqual(processor.status, RepoStatus.SUCCESS_PR_CREATED)
        
        with open(os.path.join(self.provided_test_repo_path, "pom.xml"), 'r') as f:
            content = f.read()
        self.assertEqual(content, "<project>updated by test in provided path</project>")


    @patch('repo_processor.GitHubClient')
    @patch('repo_processor.TestRunner')
    def test_no_changes_from_llm(self, MockTestRunner, MockGitHubClient): # Renamed
        mock_llm_client_instance = MagicMock(spec=GeminiClient)
        mock_github_instance = MockGitHubClient.return_value
        
        mock_llm_client_instance.generate_code.return_value = {"updated_files": []} 

        processor = RepoProcessor(self.repo_name, self.mock_context, self.prompt,
                                  mock_llm_client_instance, mock_github_instance, repo_path=self.provided_test_repo_path)
        processor.process()

        self.assertEqual(processor.status, RepoStatus.SUCCESS_NO_CHANGES)


    @patch('repo_processor.GitHubClient')
    @patch('repo_processor.TestRunner')
    def test_llm_api_error(self, MockTestRunner, MockGitHubClient): # Renamed
        mock_llm_client_instance = MagicMock(spec=GeminiClient)
        mock_github_instance = MockGitHubClient.return_value
        mock_llm_client_instance.generate_code.side_effect = LLMClientError("Simulated API error")

        processor = RepoProcessor(self.repo_name, self.mock_context, self.prompt,
                                  mock_llm_client_instance, mock_github_instance, repo_path=self.provided_test_repo_path)
        processor.process()
        self.assertEqual(processor.status, RepoStatus.ERROR_OPENAI_API) # Or map to new generic LLM error enum


    @patch('repo_processor.GitHubClient')
    @patch('repo_processor.TestRunner')
    def test_tests_fail(self, MockTestRunner, MockGitHubClient):
        mock_llm_client_instance = MagicMock(spec=GeminiClient)
        # ... (rest of the test, ensuring mock_llm_client_instance is used)
        mock_github_instance = MockGitHubClient.return_value
        mock_test_runner_instance = MockTestRunner.return_value

        mock_llm_client_instance.generate_code.return_value = {
            "updated_files": [{"file_path": "pom.xml", "updated_content": "<project>updated</project>"}]
        }
        mock_test_runner_instance.run_tests.return_value = (False, "Test failed output")

        processor = RepoProcessor(self.repo_name, self.mock_context, self.prompt,
                                  mock_llm_client_instance, mock_github_instance, repo_path=self.provided_test_repo_path)
        processor.process()

        self.assertEqual(processor.status, RepoStatus.ERROR_TESTS_FAILED)


    @patch('repo_processor.GitHubClient')
    @patch('repo_processor.TestRunner')
    def test_target_files_not_found_all(self, MockTestRunner, MockGitHubClient):
        mock_llm_client_instance = MagicMock(spec=GeminiClient)
        # ... (rest of the test, ensuring mock_llm_client_instance is used for generate_code calls)
        mock_github_instance = MockGitHubClient.return_value
        
        empty_repo_path = os.path.join(self.temp_dir_base, "empty_repo_for_not_found_test")
        os.makedirs(empty_repo_path, exist_ok=True)

        context_with_nonexistent_targets = self.mock_context.copy()
        test_specific_repo_name = "empty_repo_for_not_found_test" 
        context_with_nonexistent_targets["repository_settings"] = {
            
