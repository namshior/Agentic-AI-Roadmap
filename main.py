import os
import json
import logging
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

# -----------------------------
# Logging Setup
# -----------------------------
logging.basicConfig(level=logging.INFO)

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

# -----------------------------
# Gemini Client
# -----------------------------
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -----------------------------
# Pydantic Model
# -----------------------------
class AIResponse(BaseModel):
    topic: str
    difficulty: str
    summary: str

print("=== Gemini Structured AI Playground ===")
print("Type 'exit' to quit\n")

while True:

    user_prompt = input("You: ")

    if user_prompt.lower() == "exit":
        print("Goodbye!")
        break

    current_date = datetime.now().strftime("%d-%m-%Y")

    final_prompt = f"""
    Today's date is {current_date}.

    IMPORTANT:
    Return ONLY valid JSON.

    Use EXACTLY this schema:
    {{
        "topic": "string",
        "difficulty": "string",
        "summary": "string"
    }}

    Do NOT add extra fields.
    Do NOT change field names.
    Do NOT return markdown.

    User Question:
    {user_prompt}
    """
    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=final_prompt
        )

        raw_text = response.text.strip()

        # Remove markdown formatting if present
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        print(raw_text)

        # Convert JSON string to Python dict
        data = json.loads(raw_text)

        # Validate using Pydantic
        validated_response = AIResponse(**data)

        print("\nStructured Response:")
        print(validated_response)

    except Exception as e:
        logging.error(f"Error occurred: {e}")

    print("\n" + "-" * 50 + "\n")