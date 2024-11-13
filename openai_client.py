import logging
import json
import os
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("The OPENAI_API_KEY environment variable is not set.")
        self.client = OpenAI(api_key=api_key)

    def generate_code(self, prompt: str, context: dict) -> dict:
        logging.debug("Generating code with OpenAI API")

        component_name = context.get('repository', '')
        prompt = prompt.replace('{component_name}', component_name)

        system_prompt = "You are a code assistant that outputs code in JSON format."
        user_prompt = f"{prompt}\n\nContext:\n{json.dumps(context)}"

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
                                "description": "The file path."
                            },
                            "updated_content": {
                                "type": "string",
                                "description": "The updated content of the file."
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
        continuation_prompt = "Continue from where you left off."

        try:
            while True:
                response = self.client.chat.completions.create(
                    model="gpt-4o-2024-08-06",
                    messages=messages,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "updated_files_schema",
                            "schema": json_schema,
                            "strict": True
                        }
                    },
                    temperature=0,
                )

                logging.debug(f"Full response: {response}")

                assistant_message = response.choices[0].message
                assistant_content = assistant_message.content

                full_response_content += assistant_content

                # Check if the assistant indicates continuation is needed
                if "Continue" in assistant_content or self._response_incomplete(assistant_content):
                    # Prepare continuation message
                    messages.append({"role": "assistant", "content": assistant_content})
                    messages.append({"role": "user", "content": continuation_prompt})
                    continue
                else:
                    break

            try:
                result = json.loads(full_response_content)
                logging.debug(f"Assistant's response parsed successfully.")
                return result
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse assistant's response: {e}")
                return {}

        except Exception as e:
            logging.error(f"OpenAI API call failed: {e}")
            return {}

    def _response_incomplete(self, content: str) -> bool:
        # Implement logic to detect incomplete JSON content
        try:
            json.loads(content)
            return False
        except json.JSONDecodeError:
            return True