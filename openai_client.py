import logging
import openai
import os


class OpenAIClient:
    """Client to interact with the OpenAI API."""

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("The OPENAI_API_KEY environment variable is not set.")
        openai.api_key = api_key

    def generate_code(self, prompt: str, context: dict) -> dict:
        """Generates updated code based on the prompt and context."""
        logging.debug("Generating code with OpenAI API")

        # Combine prompt and context for the API call
        system_prompt = "You are a code assistant that only outputs JSON."
        user_prompt = prompt

        # Define the function schema
        function = {
            "name": "update_code",
            "description": "Generates updated code for the specified files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "updated_files": {
                        "type": "object",
                        "description": "A mapping of file paths to their updated content.",
                        "additionalProperties": {
                            "type": "string",
                            "description": "The updated content of the file."
                        }
                    },
                    "comments": {
                        "type": "string",
                        "description": "Any additional comments or explanations."
                    }
                },
                "required": ["updated_files"]
            }
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "user", "content": f"Context:\n{json.dumps(context)}"}
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-0613",
                messages=messages,
                functions=[function],
                function_call={"name": "update_code"},
                temperature=0,
            )

            message = response['choices'][0]['message']

            if message.get('function_call'):
                function_call = message['function_call']
                arguments = json.loads(function_call.get('arguments', '{}'))
                return arguments  # Should contain 'updated_files' and optionally 'comments'

            else:
                logging.error("No function call in response.")
                return {}

        except Exception as e:
            logging.error(f"OpenAI API call failed: {e}")
            return {}