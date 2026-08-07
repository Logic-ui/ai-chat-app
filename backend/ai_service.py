import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

async def analyze_sentiment(text: str) -> str:
    """Quick sentiment tag for a message."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        messages=[{
            "role": "user",
            "content": f"Classify sentiment as exactly one word (positive/neutral/negative): {text}"
        }]
    )
    result = response.content[0].text.strip().lower()
    return result if result in ("positive", "neutral", "negative") else "neutral"


async def generate_ai_reply(history: list[dict], user_message: str) -> str:
    """Generate an AI assistant reply given recent chat history."""
    messages = history + [{"role": "user", "content": user_message}]
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system="You are a helpful, concise support assistant. Keep replies under 3 sentences.",
        messages=messages
    )
    return response.content[0].text