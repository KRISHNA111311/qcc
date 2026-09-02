import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GEMINI_API_KEY1") or os.getenv("GEMINI_API_KEY")
if not key:
    print("No API key found")
    exit(1)

client = genai.Client(api_key=key)

# Test 1: interactions.create with explicit timeout
try:
    response = client.interactions.create(
        model="gemini-2.5-flash",
        input="Say hello in one sentence.",
        timeout=300   # <-- timeout in seconds
    )
    print("interactions.create response:", response.output_text)
except Exception as e:
    print("interactions.create error:", e)

# Test 2: models.generate_content with timeout via http_options (if first fails)
try:
    from google.genai import types
    client2 = genai.Client(api_key=key, http_options={"timeout": 300})
    response = client2.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello in one sentence.",
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=50
        )
    )
    print("models.generate_content response:", response.text)
except Exception as e:
    print("models.generate_content error:", e)
