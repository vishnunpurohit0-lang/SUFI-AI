import sounddevice as sd
import soundfile as sf

print("Speak for 5 seconds...")

recording = sd.rec(
    int(5 * 16000),
    samplerate=16000,
    channels=1,
    dtype="float32"
)

sd.wait()

sf.write("test.wav", recording, 16000)

print("Saved as test.wav")