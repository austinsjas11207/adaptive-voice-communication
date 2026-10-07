import math
import numpy as np
import wave


# =========================================================
# PROJECT PARAMETERS
# =========================================================

PCM_RATE = 128000
ADPCM_RATE = 32000
BANDWIDTH = 100000
SAMPLE_RATE = 8000

# Test channel SNR
SNR_DB = -7.0


# =========================================================
# SHANNON CAPACITY
# =========================================================

def shannon_capacity(snr_db):

    snr_linear = 10 ** (snr_db / 10)

    return BANDWIDTH * math.log2(1 + snr_linear)


# =========================================================
# ADAPTIVE DECISION WITH HYSTERESIS
# =========================================================

def select_coding(snr_db, previous_mode):

    PCM_TO_ADPCM = 1.0
    ADPCM_TO_PCM = 2.0

    ADPCM_TO_UNAVAILABLE = -6.5
    UNAVAILABLE_TO_ADPCM = -5.5

    capacity = shannon_capacity(snr_db)

    if previous_mode == "PCM":

        if capacity < ADPCM_RATE:
            return "LINK UNAVAILABLE"

        elif snr_db < PCM_TO_ADPCM:
            return "ADPCM"

        return "PCM"

    elif previous_mode == "ADPCM":

        if capacity < ADPCM_RATE:
            return "LINK UNAVAILABLE"

        elif snr_db > ADPCM_TO_PCM:
            return "PCM"

        return "ADPCM"

    elif previous_mode == "LINK UNAVAILABLE":

        if capacity >= ADPCM_RATE and snr_db > UNAVAILABLE_TO_ADPCM:
            return "ADPCM"

        return "LINK UNAVAILABLE"

# =========================================================
# IMA ADPCM TABLES
# =========================================================

STEP_TABLE = [
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
    19, 21, 23, 25, 28, 31, 34, 37, 41, 45,
    50, 55, 60, 66, 73, 80, 88, 97, 107, 118,
    130, 143, 157, 173, 190, 209, 230, 253, 279,
    307, 337, 371, 408, 449, 494, 544, 598,
    658, 724, 796, 876, 963, 1060, 1166, 1282,
    1411, 1552, 1707, 1878, 2066, 2272, 2499,
    2749, 3024, 3327, 3660, 4026, 4428, 4871,
    5358, 5894, 6484, 7132, 7845, 8630, 9493,
    10442, 11487, 12635, 13899, 15289, 16818,
    18500, 20350, 22385, 24623, 27086, 29794,
    32767
]

INDEX_TABLE = [-1, -1, -1, -1, 2, 4, 6, 8]


# =========================================================
# ADPCM ENCODER
# =========================================================

def adpcm_encode(samples):

    predictor = 0
    index = 0

    encoded = []

    for sample in samples:

        step = STEP_TABLE[index]

        difference = int(sample) - predictor

        sign = 0

        if difference < 0:
            sign = 8
            difference = -difference

        delta = 0

        if difference >= step:
            delta |= 4
            difference -= step

        if difference >= step // 2:
            delta |= 2
            difference -= step // 2

        if difference >= step // 4:
            delta |= 1

        code = delta | sign

        diffq = step // 8

        if delta & 4:
            diffq += step

        if delta & 2:
            diffq += step // 2

        if delta & 1:
            diffq += step // 4

        if sign:
            predictor -= diffq
        else:
            predictor += diffq

        predictor = max(-32768, min(32767, predictor))

        index += INDEX_TABLE[code & 7]

        index = max(0, min(88, index))

        encoded.append(code)

    # Pack two 4-bit ADPCM samples into one byte

    packed = []

    for i in range(0, len(encoded), 2):

        high = encoded[i] & 0x0F

        if i + 1 < len(encoded):
            low = encoded[i + 1] & 0x0F
        else:
            low = 0

        packed.append((high << 4) | low)

    return np.array(packed, dtype=np.uint8)


# =========================================================
# ADPCM DECODER
# =========================================================

def adpcm_decode(encoded, number_of_samples):

    predictor = 0
    index = 0

    decoded = []

    for byte in encoded:

        codes = [
            (byte >> 4) & 0x0F,
            byte & 0x0F
        ]

        for code in codes:

            step = STEP_TABLE[index]

            sign = code & 8
            delta = code & 7

            diffq = step // 8

            if delta & 4:
                diffq += step

            if delta & 2:
                diffq += step // 2

            if delta & 1:
                diffq += step // 4

            if sign:
                predictor -= diffq
            else:
                predictor += diffq

            predictor = max(-32768, min(32767, predictor))

            index += INDEX_TABLE[code & 7]

            index = max(0, min(88, index))

            decoded.append(predictor)

            if len(decoded) >= number_of_samples:
                return np.array(decoded, dtype=np.int16)

    return np.array(decoded, dtype=np.int16)


# =========================================================
# LOAD AUDIO
# =========================================================

input_file = "test_audio.wav"

with wave.open(input_file, "rb") as wav:

    sample_rate = wav.getframerate()
    channels = wav.getnchannels()
    sample_width = wav.getsampwidth()
    frames = wav.getnframes()

    audio = np.frombuffer(
        wav.readframes(frames),
        dtype=np.int16
    )


# =========================================================
# INITIAL MODE
# =========================================================

previous_mode = "PCM"

capacity = shannon_capacity(SNR_DB)

selected_mode = select_coding(
    SNR_DB,
    previous_mode
)


# =========================================================
# ADAPTIVE ENCODING
# =========================================================

print()
print("ADAPTIVE AUDIO CODING")
print("=====================")

print()
print("Input file       :", input_file)
print("Sample rate      :", sample_rate, "Hz")
print("Number of samples:", len(audio))

print()
print("SNR              :", SNR_DB, "dB")
print(
    "Channel Capacity :",
    round(capacity / 1000, 2),
    "kbps"
)

print("Selected Coding  :", selected_mode)


# =========================================================
# PCM
# =========================================================

if selected_mode == "PCM":

    pcm_data = audio.astype(np.int16)

    data_rate = SAMPLE_RATE * 16

    output_file = "adaptive_pcm.wav"

    with wave.open(output_file, "wb") as wav:

        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        wav.writeframes(
            pcm_data.tobytes()
        )

    print()
    print("Data Rate        :", data_rate / 1000, "kbps")
    print("Output file      :", output_file)


# =========================================================
# ADPCM
# =========================================================

elif selected_mode == "ADPCM":

    adpcm_data = adpcm_encode(audio)

    data_rate = SAMPLE_RATE * 4

    reconstructed = adpcm_decode(
        adpcm_data,
        len(audio)
    )

    output_file = "adaptive_adpcm_reconstructed.wav"

    with wave.open(output_file, "wb") as wav:

        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        wav.writeframes(
            reconstructed.tobytes()
        )

    # Quality calculation

    original = audio.astype(np.float64)

    reconstructed_float = reconstructed.astype(
        np.float64
    )

    error = original - reconstructed_float

    signal_power = np.mean(
        original ** 2
    )

    error_power = np.mean(
        error ** 2
    )

    if error_power > 0:

        reconstruction_snr = (
            10 *
            math.log10(
                signal_power /
                error_power
            )
        )

    else:

        reconstruction_snr = float("inf")

    print()
    print("Data Rate        :", data_rate / 1000, "kbps")
    print("Compression Ratio:", 4.0)
    print("Data Reduction   :", "75 %")
    print(
        "Reconstruction SNR:",
        round(reconstruction_snr, 2),
        "dB"
    )
    print("Output file      :", output_file)


# =========================================================
# LINK UNAVAILABLE
# =========================================================

else:

    print()
    print("Data Rate        : Communication stopped")
    print("Reason           : Channel capacity is too low")