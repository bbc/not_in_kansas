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
    parser.add_argument("--prompt-file", required=True, help="Path to the prompt text file")
    parser.add_argument("--context-file", required=True, help="Path to JSON file containing context")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    with open(args.context_file, 'r') as f:
        context = json.load(f)

    with open(args.prompt_file, 'r') as f:
        prompt = f.read()

    repos = context.get("repositories", [])
    if not repos:
        logging.error("No repositories specified in context")
        sys.exit(1)

    try:
        openai_client = OpenAIClient()
    except ValueError as e:
        logging.error(e)
        sys.exit(1)

    github_client = GitHubClient()

    results = {}
    for repo_name in repos:
        processor = RepoProcessor(repo_name, context, prompt, openai_client, github_client)
        processor.process()
        results[repo_name] = processor.result

    logging.info("Processing complete. Summary:")
    for repo_name, result in results.items():
        logging.info(f"{repo_name}: {result}")


if __name__ == "__main__":
    main()