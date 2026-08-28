import asyncio

from voice.listen import listen
from voice.speak import speak

from brain.ai import ask_jarvis
from tools.system_control import execute_command

from config import get_name
from commands import try_handle_command


def start():

    print("=" * 50)
    print(f"🤖 {get_name().upper()} AI ASSISTANT")
    print("=" * 50)
    print("Say 'exit' anytime.\n")

    while True:

        user = listen()

        if not user:
            continue

        print(f"\n🧑 You : {user}")

        if user.lower() in ["exit", "quit", "bye"]:

            asyncio.run(
                speak(f"Goodbye Vishnu. Have a great day.")
            )

            break

        print("\n🧠 Thinking...\n")

        try:

            # check local commands first (like renaming) before
            # sending anything to the LLM
            local_reply = try_handle_command(user)

            if local_reply:
                reply = local_reply
            else:
                reply = execute_command(user)

                if reply is None:
                    reply = ask_jarvis(user)

            print(f"🤖 {get_name()} : {reply}\n")

            asyncio.run(
                speak(reply)
            )

        except Exception as e:

            print(e)

            asyncio.run(
                speak("Sorry Vishnu. Something went wrong."))


if __name__ == "__main__":
    start()