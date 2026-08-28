import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
import tempfile
import os
import numpy as np
import queue
import time

model = WhisperModel(
    "medium",
    device="cuda",
    compute_type="float16"
)

SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 0.015     # tweak if your mic is quieter/louder
SILENCE_DURATION = 1.0        # seconds of silence before stopping
MAX_DURATION = 20             # hard timeout
BLOCK_DURATION = 0.1          # smaller blocks = less clipping at boundaries
DEBUG = True                  # set False once everything works


def print_devices_once():
    """Print available audio devices so you can pick the right index."""
    print("\n===== AUDIO DEVICES =====")
    print(sd.query_devices())
    print("==========================\n")


def listen():

    print("🎤 Listening...")

    # NOTE: sd.default.device was previously hardcoded to (1, 3).
    # That index can silently point to the wrong mic on this machine,
    # which was the real cause of empty transcriptions.
    # Leave this commented out unless you've confirmed the correct
    # index via sd.query_devices() and want to force it explicitly.
    # sd.default.device = (1, 3)

    audio_q = queue.Queue()

    def callback(indata, frames, time_info, status):
        if status:
            print(status)
        audio_q.put(indata.copy())

    audio_chunks = []
    silence_time = 0
    speech_detected = False
    start_time = time.time()
    max_volume_seen = 0.0

    block_size = int(BLOCK_DURATION * SAMPLE_RATE)

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=block_size,
        callback=callback
    ):

        while True:

            chunk = audio_q.get()
            volume = float(np.max(np.abs(chunk)))
            max_volume_seen = max(max_volume_seen, volume)

            if DEBUG:
                print(f"vol={volume:.4f}")

            if volume > SILENCE_THRESHOLD:
                speech_detected = True

            if speech_detected:
                audio_chunks.append(chunk)

                if volume < SILENCE_THRESHOLD:
                    silence_time += BLOCK_DURATION
                else:
                    silence_time = 0

                if silence_time >= SILENCE_DURATION:
                    print("Stopping recording...")
                    break

            if time.time() - start_time > MAX_DURATION:
                print("Timeout reached")
                break

    if DEBUG:
        print(f"Peak volume this recording: {max_volume_seen:.4f} "
              f"(threshold={SILENCE_THRESHOLD})")

    if len(audio_chunks) == 0:
        print("⚠️ No speech detected above threshold. "
              "Check mic device / SILENCE_THRESHOLD.")
        return ""

    recording = np.concatenate(audio_chunks, axis=0)

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as f:

        sf.write(f.name, recording, SAMPLE_RATE)
        temp_audio = f.name

    segments, info = model.transcribe(
        temp_audio,
        beam_size=5,
        language="en",              # stop Whisper from guessing the wrong language
        vad_filter=False            # our own energy-VAD already trims silence;
                                     # Whisper's VAD was dropping borderline-quiet
                                     # clips entirely, causing blank transcripts
    )

    text = ""
    for segment in segments:
        text += segment.text

    os.remove(temp_audio)

    text = text.strip()
    print("RAW TEXT:", text)

    if DEBUG and text == "":
        print("⚠️ Whisper returned empty text even though audio was captured. "
              "Try playing back the temp wav manually, or check mic gain/levels.")

    return text


if __name__ == "__main__":

    print_devices_once()

    while True:
        result = listen()
        print("\nYou said:", result)