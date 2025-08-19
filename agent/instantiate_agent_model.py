from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from config import openrouter_api_key


model = OpenAIModel(
    'z-ai/glm-4.5-air:free',
    provider=OpenRouterProvider(api_key=openrouter_api_key),
)
agent = Agent(model)

