import os
from dotenv import load_dotenv
from google import genai

from chat_memory import add_message, get_history
from long_term_memory import (
    add_profile,
    get_profile,
    add_memory,
    get_memories,
)

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask_jarvis(user_input):

    add_message("You", user_input)

    text = user_input.lower()

    try:
        if "my name is" in text:
            add_profile("name", user_input.split("my name is",1)[1].strip())

        elif "my college is" in text:
            add_profile("college", user_input.split("my college is",1)[1].strip())

        elif "remember that" in text:
            add_memory(user_input)

        elif "my goal is" in text:
            add_memory(user_input)

        elif "i like" in text:
            add_memory(user_input)

    except:
        pass

    profile = get_profile()
    memories = get_memories()
    history = get_history()

    prompt = f"""
You are Jarvis.

You are Vishnu's own AI assistant.

PROFILE:
{profile}

LONG TERM MEMORY:
{memories}

CHAT HISTORY:
{history}

Rules:

- Talk naturally.
- Be friendly.
- Use memories.
- Keep answers concise unless asked otherwise.
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    reply = response.text

    add_message("Jarvis", reply)

    return reply