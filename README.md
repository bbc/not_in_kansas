Ensure you have set your OpenAI and GOOGLE_API_KEY keys as an environment variable.

```shell
export OPENAI_API_KEY='your-api-key-here'
```


To Run the Script:
```shell
python main.py --prompt-file path/to/prompt_original.txt --context-file path/to/context.json
```
Ensure Environment Setup:
	•	Install dependencies: Use `poetry shell`
	•	Make sure gh, git, and other required CLI tools are installed and authenticated.

Example:
For test:
All tests:
```shell
python -m unittest discover tests
```
Unit tests:
```shell
python -m unittest tests.test_repo_processor
```
Only integration tests:
```shell
python -m unittest tests.test_integration
```

```shell
python main.py --prompt-file /Users/errolelliott/IdeaProjects/not_in_kansas/prompt_original.txt --context-file path/to/context.json
```