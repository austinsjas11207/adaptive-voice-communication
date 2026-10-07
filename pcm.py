import numpy as np
import wave

# PCM parameters
sample_rate = 8000
bits_per_sample = 8

# Read the audio file
with wave.open("test_audio.wav", "rb") as wav:
    audio = np.frombuffer(
        wav.readframes(wav.getnframes()),
        dtype=np.int16
    )

# Convert to int32 to avoid overflow
audio = audio.astype(np.int32)

# Convert 16-bit samples to 8-bit PCM
pcm_8bit = ((audio + 32768) / 256).astype(np.uint8)

# Calculate PCM bit rate
bit_rate = sample_rate * bits_per_sample

print("PCM Encoding")
print("----------------------")
print("Sample rate:", sample_rate, "samples/sec")
print("Bits per sample:", bits_per_sample)
print("Number of samples:", len(audio))
print("PCM bit rate:", bit_rate, "bits/sec")
print("PCM bit rate:", bit_rate / 1000, "kbps")