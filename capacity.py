import math

# Channel bandwidth
bandwidth = 100000  # 100 kHz

# Required data rates
pcm_rate = 128000      # 128 kbps
adpcm_rate = 32000     # 32 kbps


def shannon_capacity(bandwidth, snr_db):
    # Convert SNR from dB to linear
    snr_linear = 10 ** (snr_db / 10)

    # Shannon-Hartley equation
    capacity = bandwidth * math.log2(1 + snr_linear)

    return capacity


print("SHANNON CHANNEL CAPACITY")
print("-------------------------")

print("Channel bandwidth:", bandwidth / 1000, "kHz")
print("PCM requirement:", pcm_rate / 1000, "kbps")
print("ADPCM requirement:", adpcm_rate / 1000, "kbps")

print()
print("SNR(dB)    Capacity(kbps)    PCM    ADPCM")
print("-------------------------------------------")

for snr_db in range(0, 31, 5):

    capacity = shannon_capacity(bandwidth, snr_db)

    pcm_status = "YES" if capacity >= pcm_rate else "NO"
    adpcm_status = "YES" if capacity >= adpcm_rate else "NO"

    print(
        f"{snr_db:>3}        "
        f"{capacity / 1000:>8.2f}       "
        f"{pcm_status:^5}  "
        f"{adpcm_status:^5}"
    )