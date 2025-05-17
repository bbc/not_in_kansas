```shell
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

```json
{
  "object": "list",
  "data": [
    {
      "id": "gpt-4",
      "object": "model",
      "created": 1687882411,
      "owned_by": "openai"
    },
    {
      "id": "gpt-3.5-turbo",
      "object": "model",
      "created": 1677610602,
      "owned_by": "openai"
    }
    // ...
  ]
}
```

*Note: The above output is a partial listing for illustrative purposes. For the complete and up-to-date list of available models, please query the `/v1/models` endpoint.*
