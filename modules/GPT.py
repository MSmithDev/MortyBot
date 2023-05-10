import openai
import os

# Get .env variables
openai.api_key = os.getenv('OPENAI_API_KEY')