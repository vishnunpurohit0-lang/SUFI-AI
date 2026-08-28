import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "identity.json")

DEFAULT_IDENTITY = {
    "name": "Jarvis",
    "wake_words": ["jarvis"],
}


def _load():
    if not os.path.exists(CONFIG_PATH):
        _save(DEFAULT_IDENTITY)
        return DEFAULT_IDENTITY.copy()

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


_identity = _load()


def get_name():
    return _identity["name"]


def get_wake_words():
    return _identity["wake_words"]


def set_name(new_name: str):
    """Rename the assistant. Updates the in-memory identity and
    persists it to identity.json so it survives restarts."""
    new_name = new_name.strip()
    if not new_name:
        return False

    _identity["name"] = new_name
    _identity["wake_words"] = [new_name.lower()]
    _save(_identity)
    return True