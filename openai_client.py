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
        system_prompt = "You are a helpful assistant that writes code changes."
        user_prompt = f"{prompt}\nContext:\n{context}"

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
            )

            content = response['choices'][0]['message']['content']
            # Assume the assistant returns a JSON string
            updated_files = json.loads(content)
            return {"updated_files": updated_files}

        except Exception as e:
            logging.error(f"OpenAI API call failed: {e}")
            return {}