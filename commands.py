import re
from config import set_name, get_name

RENAME_PATTERNS = [
    r"change your name to (.+)",
    r"rename yourself to (.+)",
    r"i(?:'m| am) going to call you (.+)",
    r"your new name is (.+)",
    r"from now on you(?:'re| are) (.+)",
]


def try_handle_command(text: str):
    """
    Checks if the user's text is a recognized local command
    (like renaming). Returns a response string if handled,
    or None if the text should be passed on to the LLM as normal.
    """
    lowered = text.lower().strip()

    for pattern in RENAME_PATTERNS:
        match = re.search(pattern, lowered)
        if match:
            new_name = match.group(1).strip().strip(".!?")
            new_name = new_name.title()  # "sufi" -> "Sufi"

            if set_name(new_name):
                return f"Alright, I'll respond to {new_name} from now on."
            else:
                return "Sorry, I didn't catch the new name clearly."

    return None