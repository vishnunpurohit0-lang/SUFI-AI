import asyncio
import re
import os
import time
import uuid

import edge_tts
import pygame

VOICE = "en-US-GuyNeural"

pygame.mixer.init()


def split_sentences(text):
    # Split on sentence-ending punctuation, keep it simple and robust
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p for p in parts if p]


async def _generate(sentence, filename):
    communicate = edge_tts.Communicate(sentence, VOICE)
    await communicate.save(filename)


def _play_blocking(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.05)
    pygame.mixer.music.unload()


async def speak(text):
    sentences = split_sentences(text)

    if not sentences:
        return

    # Pre-generate filenames so producer/consumer don't collide
    filenames = [f"temp_voice_{uuid.uuid4().hex}.mp3" for _ in sentences]

    queue = asyncio.Queue()

    async def producer():
        for sentence, filename in zip(sentences, filenames):
            await _generate(sentence, filename)
            await queue.put(filename)
        await queue.put(None)  # sentinel: done

    async def consumer():
        loop = asyncio.get_event_loop()
        while True:
            filename = await queue.get()
            if filename is None:
                break
            # play() blocks, run it in a thread so the producer keeps generating
            await loop.run_in_executor(None, _play_blocking, filename)
            os.remove(filename)

    await asyncio.gather(producer(), consumer())


if __name__ == "__main__":
    asyncio.run(
        speak(
            "Hello Vishnu. I am Jarvis. This is the first sentence. "
            "And here is a second sentence, generated while the first one was still playing."
        )
    )