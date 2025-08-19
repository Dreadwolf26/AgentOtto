#creating a config file to load all env variables
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
openrouter_api_key = os.getenv("OPENROPTER_API_KEY")
