#!/usr/bin/env python3

import argparse
import json
import logging
import sys
import os # For OPENAI_MODEL_NAME

from openai_client import OpenAIClient
from github_client import GitHubClient
from repo_processor import RepoProcessor
from status_enums import RepoStatus # Import status enum

def main():
    parser = argparse.ArgumentParser(description="Automate tech debt fixes across multiple repositories")
    parser.add_argument("--prompt-file", required=True, help="Path to the prompt text file")
    parser.add_argument("--context-file", required=True, help="Path to JSON file containing context")
    parser.add_argument("--repo-path", help="Optional path to a single pre-cloned repository for local processing.")
    parser.add_argument("--repo-name", help="Name of the single repository to process (required if --repo-path is used and repo not in context file).")
    parser.add_argument("--keep-temp-dir", action="store_true", help="Keep temporary directories after processing (for debugging).")

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

    try:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            logging.warning("OPENAI_API_KEY environment variable is not set. OpenAI calls will fail if not mocked.")

        openai_client = OpenAIClient()
        # Set model from config after client initialization
        openai_client.set_model_from_config(context_data.get("global_settings", {}))

    except ValueError as e: # Raised by OpenAIClient if key is missing
        logging.error(e)
        sys.exit(1)

    github_client = GitHubClient()
    results = {}

    if args.repo_path:
        if not args.repo_name:
            # Try to infer from path if it's a direct subdir of a common pattern
            args.repo_name = os.path.basename(args.repo_path)
            logging.info(f"Inferred repo_name as '{args.repo_name}' from --repo-path.")
            # Update context if this repo isn't defined, using global_settings
            if args.repo_name not in context_data.get("repository_settings", {}):
                if "repository_settings" not in context_data:
                    context_data["repository_settings"] = {}
                context_data["repository_settings"][args.repo_name] = {} # Use global if specific is missing
                logging.info(f"Using global settings for locally processed repo: {args.repo_name}")

        repos_to_process = [args.repo_name]
        logging.info(f"Processing single specified repository: {args.repo_name} at path {args.repo_path}")
    else:
        repos_to_process = context_data.get("repositories", [])
        if not repos_to_process:
            logging.error("No repositories specified in context file and --repo-path not used.")
            sys.exit(1)

    for repo_name in repos_to_process:
        # If using --repo-path, this specific repo_path will be used.
        # Otherwise, repo_path in RepoProcessor will be None, and it will create a temp dir.
        current_repo_path_arg = args.repo_path if args.repo_path and repo_name == args.repo_name else None

        processor = RepoProcessor(
            repo_name,
            context_data,
            prompt,
            openai_client,
            github_client,
            repo_path=current_repo_path_arg,
            keep_temp_dir=args.keep_temp_dir
        )
        processor.process()
        results[repo_name] = processor.status # Use the enum status

    logging.info("\nProcessing Complete. Summary:")
    for repo_name, status in results.items():
        logging.info(f"{repo_name}: {status}") # This will use the __str__ of RepoStatus


if __name__ == "__main__":
    main()