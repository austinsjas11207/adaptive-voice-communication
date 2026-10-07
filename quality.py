import numpy as np
import wave

# Read original audio
with wave.open("test_audio.wav", "rb") as wav:
    original = np.frombuffer(
        wav.readframes(wav.getnframes()),
        dtype=np.int16
    ).astype(np.float64)

# Read reconstructed audio
with wave.open("adpcm_reconstructed.wav", "rb") as wav:
    reconstructed = np.frombuffer(
        wav.readframes(wav.getnframes()),
        dtype=np.int16
    ).astype(np.float64)

# Make sure both have the same length
N = min(len(original), len(reconstructed))

original = original[:N]
reconstructed = reconstructed[:N]

# Error
error = original - reconstructed

# Signal power
signal_power = np.mean(original ** 2)

# Error power
error_power = np.mean(error ** 2)

# MSE
mse = error_power

# SNR
snr = 10 * np.log10(signal_power / error_power)

print("ADPCM QUALITY ANALYSIS")
print("----------------------")

print("Number of samples:", N)

print()
print("Signal power:", signal_power)
print("Error power:", error_power)
print("MSE:", mse)

print()
print("ADPCM reconstruction SNR:",
      round(snr, 2), "dB")