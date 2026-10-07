import numpy as np
import wave

sample_rate = 8000
duration = 2
frequency = 440

t = np.arange(int(sample_rate * duration)) / sample_rate

audio = 0.5 * np.sin(2 * np.pi * frequency * t)

audio_int16 = np.int16(audio * 32767)

with wave.open("test_audio.wav", "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(sample_rate)
    wav.writeframes(audio_int16.tobytes())

print("Audio generated successfully!")
print("Sample rate:", sample_rate)
print("Number of samples:", len(audio_int16))