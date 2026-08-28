import io
import base64

import pyautogui
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types

from retry_helper import call_with_retry

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def capture_screen():
    """Takes a screenshot and returns it as PNG bytes."""
    screenshot = pyautogui.screenshot()

    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    return buffer.getvalue()


def ask_about_screen(question):
    """
    Captures the current screen and asks Gemini vision to answer
    a question about what's visible.
    """
    image_bytes = capture_screen()

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type="image/png"
    )

    prompt = (
        "You are looking at a screenshot of the user's laptop screen. "
        f"Answer this question about what you see: {question}\n\n"
        "Be concise and specific about what's visible (app names, buttons, "
        "text, etc.) since this answer will be spoken aloud."
    )

    try:
        response = call_with_retry(
            client.models.generate_content,
            model="gemini-flash-latest",
            contents=[image_part, prompt]
        )
        return response.text.strip()

    except Exception as e:
        print(f"Screen vision call failed: {e}")
        return "I couldn't analyze the screen right now, something went wrong."


if __name__ == "__main__":
    print(ask_about_screen("What application is currently open?"))