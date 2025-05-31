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