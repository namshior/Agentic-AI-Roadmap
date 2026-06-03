import os
import json
import logging
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

# -------------------------
# Setup
# -------------------------

logging.basicConfig(level=logging.INFO)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

app = FastAPI(
    title="Week 1 Agentic AI",
    description="AI Playground API",
    version="1.0"
)

# -------------------------
# Request Model
# -------------------------

class UserQuestion(BaseModel):
    question: str

# -------------------------
# Response Model
# -------------------------

class AIResponse(BaseModel):
    topic: str
    difficulty: str
    summary: str

# -------------------------
# Endpoint
# -------------------------

@app.post("/ask", response_model=AIResponse)
def ask_ai(user_input: UserQuestion):

    current_date = datetime.now().strftime("%d-%m-%Y")

    prompt = f"""
    Today's date is {current_date}.

    IMPORTANT:
    Return ONLY valid JSON.

    Use EXACTLY this schema:

    {{
        "topic": "string",
        "difficulty": "string",
        "summary": "string"
    }}

    User Question:
    {user_input.question}
    """

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text.strip()

        if raw_text.startswith("```json"):
            raw_text = (
                raw_text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        data = json.loads(raw_text)

        validated = AIResponse(**data)

        return validated

    except Exception as e:
        logging.error(str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )