import logging
import json
import os
from openai import OpenAI, APIError # Import APIError for specific OpenAI errors
from exceptions import OpenAIClientError, OpenAIResponseError # Import custom exceptions

MAX_CONTINUATION_ATTEMPTS = 3 # Max attempts for continuation

class OpenAIClient:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("The OPENAI_API_KEY environment variable is not set.")
        self.client = OpenAI(api_key=api_key)
        # Get model from env, then context (passed later or global), then default
        self.model_name = os.getenv('OPENAI_MODEL_NAME', "gpt-4o-2024-08-06") # Default model

    def set_model_from_config(self, global_settings: dict):
        """Allows setting model name from config if not set by env var."""
        if 'OPENAI_MODEL_NAME' not in os.environ: # Env var takes precedence
            self.model_name = global_settings.get("openai_model_name", self.model_name)
        logging.info(f"Using OpenAI model: {self.model_name}")


    def generate_code(self, prompt: str, context: dict) -> dict:
        logging.debug("Generating code with OpenAI API")

        # Allow context to override model_name if not set by env
        # This is now handled by set_model_from_config, called externally if needed
        # or directly in RepoProcessor.
        # For now, we assume self.model_name is set correctly during __init__ or by a call.

        component_name = context.get('repository', '')
        # Use f-string for clarity if only one placeholder, or consider string.Template
        # prompt = prompt.replace('{component_name}', component_name) # Simple replacement
        # For more complex templating in future:
        # from string import Template
        # prompt_template = Template(prompt)
        # final_prompt = prompt_template.safe_substitute(component_name=component_name)
        final_prompt = prompt.format(component_name=component_name) # Assuming prompt uses .format() style

        system_prompt = "You are a code assistant that outputs code in JSON format."
        user_prompt = f"{final_prompt}\n\nContext:\n{json.dumps(context, indent=2)}" # Indent for readability in logs

        json_schema = {
            "type": "object",
            "properties": {
                "updated_files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The file path relative to the repository root."
                            },
                            "updated_content": {
                                "type": "string",
                                "description": "The full updated content of the file. If no changes, this should be the original content."
                            }
                        },
                        "required": ["file_path", "updated_content"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["updated_files"],
            "additionalProperties": False
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        full_response_content = ""
        continuation_prompt = "The previous response was incomplete or not valid JSON. Please continue generating the JSON output from where you left off, ensuring the final output is a single, complete, and valid JSON object matching the schema. If you were in the middle of a string, continue that string. If you were in the middle of a list or object, continue that structure."

        for attempt in range(1, MAX_CONTINUATION_ATTEMPTS + 1):
            logging.debug(f"OpenAI API Call Attempt #{attempt}")
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "updated_files_schema",
                            "schema": json_schema,
                            "strict": True # Request strict adherence
                        }
                    },
                    temperature=0,
                )
                logging.debug(f"Raw OpenAI response object: {response}")

                assistant_message = response.choices[0].message
                assistant_content = assistant_message.content

                if not assistant_content: # Handle empty content from LLM
                    logging.warning("OpenAI returned empty content.")
                    if attempt < MAX_CONTINUATION_ATTEMPTS:
                        messages.append({"role": "assistant", "content": ""}) # Add empty assistant message
                        messages.append({"role": "user", "content": continuation_prompt})
                        continue
                    else:
                        raise OpenAIResponseError("OpenAI returned empty content after multiple attempts.")

                logging.debug(f"Assistant's content (attempt {attempt}): {assistant_content}")

                # It's better to try parsing the current piece if the LLM is supposed to return full JSON each time.
                # However, with the continuation prompt, we are asking it to complete, so we append.
                current_potential_json = full_response_content + assistant_content

                # Try to parse the accumulated content
                try:
                    parsed_json = json.loads(current_potential_json)
                    # If parsing succeeds, assume it's complete if no explicit "Continue"
                    if "continue" not in assistant_content.lower(): # More robust check
                        logging.debug("JSON parsed successfully and no explicit continuation cue.")
                        return parsed_json
                    else:
                        logging.debug("JSON parsed but 'continue' cue found. Will attempt continuation.")
                        full_response_content = current_potential_json # Save successfully parsed part
                        messages.append({"role": "assistant", "content": assistant_content})
                        messages.append({"role": "user", "content": continuation_prompt})
                        # Continue to next attempt
                except json.JSONDecodeError:
                    logging.warning(f"JSON parsing failed for accumulated content (attempt {attempt}). Content so far: '{current_potential_json[:500]}...'")
                    full_response_content = current_potential_json # Keep accumulating
                    if attempt < MAX_CONTINUATION_ATTEMPTS:
                        messages.append({"role": "assistant", "content": assistant_content}) # Add what we got
                        messages.append({"role": "user", "content": continuation_prompt})
                        # Continue to next attempt
                    else:
                        raise OpenAIResponseError(f"Failed to get complete JSON after {MAX_CONTINUATION_ATTEMPTS} attempts. Last content: {current_potential_json[:500]}")

            except APIError as e:
                logging.error(f"OpenAI API error on attempt {attempt}: {e}", exc_info=True)
                if attempt == MAX_CONTINUATION_ATTEMPTS:
                    raise OpenAIClientError(f"OpenAI API error after {MAX_CONTINUATION_ATTEMPTS} attempts: {e}") from e
                # Potentially add a small delay before retrying for transient API errors
                # time.sleep(1)
            except Exception as e: # Catch other unexpected errors during API call
                logging.error(f"Unexpected error during OpenAI API call on attempt {attempt}: {e}", exc_info=True)
                if attempt == MAX_CONTINUATION_ATTEMPTS:
                    raise OpenAIClientError(f"Unexpected error after {MAX_CONTINUATION_ATTEMPTS} attempts: {e}") from e

        # If loop finishes without returning/raising, something went wrong with continuation logic
        raise OpenAIResponseError(f"Failed to obtain a complete JSON response after {MAX_CONTINUATION_ATTEMPTS} attempts. Final accumulated content: {full_response_content[:500]}")

    # _response_incomplete is removed as its logic is now integrated into the loop