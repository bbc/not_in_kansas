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