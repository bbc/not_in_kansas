#!/usr/bin/env python3

import argparse
import json
import logging
import sys

from openai_client import OpenAIClient
from github_client import GitHubClient
from repo_processor import RepoProcessor


def main():
    parser = argparse.ArgumentParser(description="Automate tech debt fixes across multiple repositories")
    parser.add_argument("--prompt", required=True, help="Prompt detailing the change")
    parser.add_argument("--context", required=True, help="Path to JSON file containing context")
    parser.add_argument("--api-key", required=True, help="API key for OpenAI")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    with open(args.context, 'r') as f:
        context = json.load(f)

    repos = context.get("repositories", [])
    if not repos:
        logging.error("No repositories specified in context")
        sys.exit(1)

    openai_client = OpenAIClient(api_key=args.api_key)
    github_client = GitHubClient()

    results = {}
    for repo_name in repos:
        processor = RepoProcessor(repo_name, context, args.prompt, openai_client, github_client)
        processor.process()
        results[repo_name] = processor.result

    logging.info("Processing complete. Summary:")
    for repo_name, result in results.items():
        logging.info(f"{repo_name}: {result}")


if __name__ == "__main__":
    main()