import math

PCM_RATE = 128000
ADPCM_RATE = 32000
BANDWIDTH = 100000


def shannon_capacity(snr_db):
    snr_linear = 10 ** (snr_db / 10)
    return BANDWIDTH * math.log2(1 + snr_linear)


# ---------------------------------------------------------
# HYSTERESIS THRESHOLDS
# ---------------------------------------------------------

PCM_TO_ADPCM = 1.0
ADPCM_TO_PCM = 2.0

ADPCM_TO_UNAVAILABLE = -6.5
UNAVAILABLE_TO_ADPCM = -5.5


# ---------------------------------------------------------
# Adaptive coding decision
# ---------------------------------------------------------

def select_coding(snr_db, previous_mode):

    capacity = shannon_capacity(snr_db)

    # -----------------------------------------
    # PCM state
    # -----------------------------------------

    if previous_mode == "PCM":

        if snr_db < PCM_TO_ADPCM:
            return "ADPCM"

        return "PCM"

    # -----------------------------------------
    # ADPCM state
    # -----------------------------------------

    elif previous_mode == "ADPCM":

        if snr_db > ADPCM_TO_PCM:
            return "PCM"

        elif snr_db < ADPCM_TO_UNAVAILABLE:
            return "LINK UNAVAILABLE"

        return "ADPCM"

    # -----------------------------------------
    # Link unavailable state
    # -----------------------------------------

    elif previous_mode == "LINK UNAVAILABLE":

        if snr_db > UNAVAILABLE_TO_ADPCM:
            return "ADPCM"

        return "LINK UNAVAILABLE"


# ---------------------------------------------------------
# Test channel conditions
# ---------------------------------------------------------

snr_values = [
    10,
    5,
    2,
    1.5,
    1.0,
    0.5,
    0,
    -5,
    -6,
    -6.5,
    -7,
    -6,
    -5,
    0,
    3,
    5
]


print("ADAPTIVE VOICE CODING WITH HYSTERESIS")
print("======================================")

previous_mode = "PCM"

for snr in snr_values:

    capacity = shannon_capacity(snr)

    coding = select_coding(
        snr,
        previous_mode
    )

    print()
    print("SNR              :", snr, "dB")
    print(
        "Channel Capacity :",
        round(capacity / 1000, 2),
        "kbps"
    )
    print("Selected Coding  :", coding)

    if coding == "PCM":

        print("Data Rate        : 128 kbps")

    elif coding == "ADPCM":

        print("Data Rate        : 32 kbps")

    else:

        print(
            "Data Rate        : Communication stopped"
        )

    # Save current state
    previous_mode = coding