from llama_index.llms.azure_openai import AzureOpenAI
from config.properties import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    LLM_DEPLOYMENT_NAME,
)


llm = AzureOpenAI(
    api_version="2024-02-01",
    model="gpt-4.1",
    engine=LLM_DEPLOYMENT_NAME,
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)
