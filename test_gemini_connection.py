
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=180000),
)

try:
    print("Testing Gemini text generation...")

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Reply with only the word OK.",
        config=types.GenerateContentConfig(
            max_output_tokens=5,
        ),
    )

    print("SUCCESS:", response.text)

except Exception as error:
    print("FAILED:", repr(error))

finally:
    client.close()
