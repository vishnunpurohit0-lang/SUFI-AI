import os
import json
import subprocess

import pyautogui
from dotenv import load_dotenv
from google import genai

from retry_helper import call_with_retry
from screen_vision import ask_about_screen
from voice.speak import speak
import asyncio

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ---------------------------------------------------------------------------
# CONFIRMATION — spoken yes/no before any state-changing action runs
# ---------------------------------------------------------------------------

def confirm_action(description):
    """
    Speaks the proposed action out loud and waits for a typed y/n
    confirmation in the terminal. (Using terminal input rather than
    voice here keeps this fast/reliable — swap for listen() from
    voice.listen if you want fully spoken confirmation instead.)
    """
    asyncio.run(speak(f"Do you want me to {description}? Say yes or no."))

    answer = input(f"Confirm '{description}'? (y/n): ").strip().lower()
    return answer.startswith("y")


# ---------------------------------------------------------------------------
# ACTION IMPLEMENTATIONS
# Every function here takes `target` (string, may be empty) and returns
# a short spoken confirmation string.
# ---------------------------------------------------------------------------

APP_COMMANDS = {
    "chrome": "start chrome",
    "vscode": "code",
    "vs code": "code",
    "notepad": "notepad",
    "calculator": "calc",
    "explorer": "explorer",
    "file explorer": "explorer",
    "settings": "start ms-settings:",
    "paint": "mspaint",
    "spotify": "start spotify",
}

CLOSE_PROCESS_NAMES = {
    "chrome": "chrome.exe",
    "vscode": "Code.exe",
    "vs code": "Code.exe",
    "notepad": "notepad.exe",
    "calculator": "CalculatorApp.exe",
    "spotify": "Spotify.exe",
}


def open_app(target):
    key = (target or "").strip().lower()

    for name, command in APP_COMMANDS.items():
        if name in key:
            if not confirm_action(f"open {name}"):
                return "Okay, not opening it."
            os.system(command)
            return f"Opening {name}"

    return f"I don't know how to open '{target}' yet."


def close_app(target):
    key = (target or "").strip().lower()

    for name, process in CLOSE_PROCESS_NAMES.items():
        if name in key:
            if not confirm_action(f"close {name}"):
                return "Okay, leaving it open."
            subprocess.run(
                ["taskkill", "/IM", process, "/F"],
                capture_output=True
            )
            return f"Closing {name}"

    return f"I don't know how to close '{target}' yet."


def open_website(target):
    url = (target or "").strip()

    if not url:
        return "I didn't catch which website to open."

    if not url.startswith("http"):
        url = "https://" + url

    if not confirm_action(f"open {url}"):
        return "Okay, not opening it."

    os.system(f'start {url}')
    return f"Opening {url}"


def adjust_volume(target):
    import keyboard

    direction = (target or "").strip().lower()
    steps = 5

    if "up" in direction:
        if not confirm_action("turn the volume up"):
            return "Okay."
        for _ in range(steps):
            keyboard.send("volume up")
        return "Turning volume up"

    if "down" in direction:
        if not confirm_action("turn the volume down"):
            return "Okay."
        for _ in range(steps):
            keyboard.send("volume down")
        return "Turning volume down"

    if "mute" in direction:
        if not confirm_action("mute the volume"):
            return "Okay."
        keyboard.send("volume mute")
        return "Muting volume"

    return "Say volume up, down, or mute."


def search_file(target):
    # Read-only — no confirmation needed.
    query = (target or "").strip().lower()

    if not query:
        return "What file should I search for?"

    search_dirs = [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Downloads"),
    ]

    matches = []

    for directory in search_dirs:
        if not os.path.isdir(directory):
            continue

        for root, _, files in os.walk(directory):
            for f in files:
                if query in f.lower():
                    matches.append(os.path.join(root, f))
                    if len(matches) >= 5:
                        break
            if len(matches) >= 5:
                break

    if not matches:
        return f"No files found matching '{target}'."

    names = ", ".join(os.path.basename(m) for m in matches)
    return f"Found: {names}"


def describe_screen(target):
    # Read-only — no confirmation needed.
    question = (target or "").strip() or "What is currently on the screen?"
    return ask_about_screen(question)


def click_on(target):
    # Requires the user to tell us roughly where (Gemini vision could be
    # extended to return coordinates — kept simple/manual for now).
    if not confirm_action(f"click on {target}"):
        return "Okay, not clicking."
    return ("I can see the screen but I don't have precise click "
            "coordinates wired up yet — that needs an extra vision "
            "step to map '{}' to an x,y position.").format(target)


def type_text(target):
    text = target or ""

    if not text:
        return "What should I type?"

    if not confirm_action(f"type '{text}'"):
        return "Okay, not typing."

    pyautogui.typewrite(text, interval=0.03)
    return "Typed it."


# ---------------------------------------------------------------------------
# WHITELIST — only actions listed here can ever be executed.
# ---------------------------------------------------------------------------

ACTIONS = {
    "open_app": open_app,
    "close_app": close_app,
    "open_website": open_website,
    "adjust_volume": adjust_volume,
    "search_file": search_file,
    "describe_screen": describe_screen,
    "click_on": click_on,
    "type_text": type_text,
}


# ---------------------------------------------------------------------------
# CLASSIFICATION — ask Gemini to map free text to a structured action
# ---------------------------------------------------------------------------

CLASSIFY_PROMPT = """
You are a command classifier for a desktop assistant.

Given the user's message, decide if it is a request to control the
computer or see the screen. If it is, respond with ONLY a JSON object
in this exact form:

{{"action": "<one of: open_app, close_app, open_website, adjust_volume, search_file, describe_screen, click_on, type_text>", "target": "<the relevant target>"}}

Use describe_screen when the user asks what's on screen, what app is
open, or asks you to look at / read something visible.

If the message is NOT a system control command (e.g. it's a question,
a greeting, small talk, or anything conversational), respond with
ONLY:

{{"action": "none", "target": ""}}

Respond with raw JSON only. No markdown, no explanation.

User message: "{user_input}"
"""


def classify_command(user_input):
    prompt = CLASSIFY_PROMPT.format(user_input=user_input)

    try:
        response = call_with_retry(
            client.models.generate_content,
            model="gemini-flash-latest",
            contents=prompt,
            max_retries=6,
            base_delay=2.0,
            config={"response_mime_type": "application/json"}
        )
    except Exception as e:
        print(f"Classifier call failed after retries: {e}")
        return "none", ""

    try:
        data = json.loads(response.text)
        return data.get("action", "none"), data.get("target", "")
    except (json.JSONDecodeError, AttributeError):
        return "none", ""


def execute_command(text):
    action, target = classify_command(text)

    if action == "none" or action not in ACTIONS:
        return None

    try:
        return ACTIONS[action](target)
    except Exception as e:
        return f"Something went wrong trying to do that: {e}"