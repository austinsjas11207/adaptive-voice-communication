import numpy as np
import wave

# -----------------------------
# IMA ADPCM tables
# -----------------------------

STEP_TABLE = [
    7, 8, 9, 10, 11, 12, 13, 14,
    16, 17, 19, 21, 23, 25, 28, 31,
    34, 37, 41, 45, 50, 55, 60, 66,
    73, 80, 88, 97, 107, 118, 130, 143,
    157, 173, 190, 209, 230, 253, 279, 307,
    337, 371, 408, 449, 494, 544, 598, 658,
    724, 796, 876, 963, 1060, 1166, 1282, 1411,
    1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024,
    3327, 3660, 4026, 4428, 4871, 5358, 5894, 6484,
    7132, 7845, 8630, 9493, 10442, 11487, 12635,
    13899, 15289, 16818, 18500, 20350, 22385,
    24623, 27086, 29794, 32767
]

INDEX_TABLE = [-1, -1, -1, -1, 2, 4, 6, 8]


# -----------------------------
# ADPCM Encoder
# -----------------------------

def encode_adpcm(samples):

    predictor = 0
    index = 0

    encoded = []

    for sample in samples:

        step = STEP_TABLE[index]

        difference = int(sample) - predictor

        code = 0

        if difference < 0:
            code = 8
            difference = -difference

        if difference >= step:
            code |= 4
            difference -= step

        step2 = step >> 1

        if difference >= step2:
            code |= 2
            difference -= step2

        step4 = step >> 2

        if difference >= step4:
            code |= 1

        # Reconstruct difference

        delta = step >> 3

        if code & 4:
            delta += step

        if code & 2:
            delta += step >> 1

        if code & 1:
            delta += step >> 2

        if code & 8:
            predictor -= delta
        else:
            predictor += delta

        predictor = max(-32768, min(32767, predictor))

        # Update step index

        index += INDEX_TABLE[code & 7]

        index = max(0, min(88, index))

        encoded.append(code)

    return np.array(encoded, dtype=np.uint8)


# -----------------------------
# ADPCM Decoder
# -----------------------------

def decode_adpcm(encoded):

    predictor = 0
    index = 0

    decoded = []

    for code in encoded:

        step = STEP_TABLE[index]

        delta = step >> 3

        if code & 4:
            delta += step

        if code & 2:
            delta += step >> 1

        if code & 1:
            delta += step >> 2

        if code & 8:
            predictor -= delta
        else:
            predictor += delta

        predictor = max(-32768, min(32767, predictor))

        decoded.append(predictor)

        index += INDEX_TABLE[code & 7]

        index = max(0, min(88, index))

    return np.array(decoded, dtype=np.int16)


# -----------------------------
# Read original audio
# -----------------------------

with wave.open("test_audio.wav", "rb") as wav:

    sample_rate = wav.getframerate()

    audio = np.frombuffer(
        wav.readframes(wav.getnframes()),
        dtype=np.int16
    )


# -----------------------------
# Encode
# -----------------------------

adpcm_data = encode_adpcm(audio)


# -----------------------------
# Decode
# -----------------------------

reconstructed = decode_adpcm(adpcm_data)


# -----------------------------
# Save reconstructed audio
# -----------------------------

with wave.open("adpcm_reconstructed.wav", "wb") as wav:

    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(sample_rate)

    wav.writeframes(reconstructed.tobytes())


# -----------------------------
# Results
# -----------------------------

pcm_bitrate = sample_rate * 16
adpcm_bitrate = sample_rate * 4

error = audio.astype(np.float64) - reconstructed.astype(np.float64)

mse = np.mean(error ** 2)

print("ADPCM TEST")
print("----------------------")

print("Sample rate:", sample_rate)
print("Number of samples:", len(audio))

print()
print("Original PCM rate:", pcm_bitrate / 1000, "kbps")
print("ADPCM rate:", adpcm_bitrate / 1000, "kbps")

print()
print("Compression ratio:",
      pcm_bitrate / adpcm_bitrate)

print("Data reduction:",
      (1 - adpcm_bitrate / pcm_bitrate) * 100, "%")

print()
print("Mean Squared Error:", mse)

print()
print("Reconstructed audio saved as:")
print("adpcm_reconstructed.wav")