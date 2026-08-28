import json
import os

MEMORY_FILE = "data/memory.json"


def load_memory():
    """Load memory from JSON file."""
    if not os.path.exists(MEMORY_FILE):
        return {
            "profile": {},
            "memories": [],
            "projects": {}
        }

    with open(MEMORY_FILE, "r") as file:
        return json.load(file)


def save_memory(memory):
    """Save memory to JSON file."""
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)


def add_profile(key, value):
    """Save personal information."""
    memory = load_memory()
    memory["profile"][key] = value
    save_memory(memory)


def get_profile():
    """Return profile information."""
    memory = load_memory()
    return memory["profile"]


def add_memory(text):
    """Save a memory."""
    memory = load_memory()
    memory["memories"].append(text)
    save_memory(memory)


def get_memories():
    """Return all memories."""
    memory = load_memory()
    return memory["memories"]