from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from config import openrouter_api_key

def agent_model():
    # define the model with provider
    model = OpenAIModel(
        "z-ai/glm-4.5-air:free",
        provider=OpenRouterProvider(api_key=openrouter_api_key),
    )

    # pass that model into an Agent
    agent = Agent(model)
    return agent