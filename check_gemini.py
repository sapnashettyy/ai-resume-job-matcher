
import os

from dotenv import load_dotenv
from google import genai

# Load the API key from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

# Create the Gemini client
client = genai.Client(api_key=api_key)

try:
    print("Checking available Gemini models...\n")

    models = client.models.list()

    for model in models:
        print(model.name)

except Exception as error:
    print("Model check failed:", repr(error))
