conversation = []

def add_message(role, text):
    conversation.append({
        "role": role,
        "text": text
    })

def get_history():
    history = ""

    for msg in conversation:
        history += f"{msg['role']}: {msg['text']}\n"

    return history