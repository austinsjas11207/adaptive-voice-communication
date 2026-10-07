import math

bandwidth = 100000

pcm_rate = 128000
adpcm_rate = 32000


def required_snr(data_rate):
    snr_linear = (2 ** (data_rate / bandwidth)) - 1
    snr_db = 10 * math.log10(snr_linear)
    return snr_db


pcm_threshold = required_snr(pcm_rate)
adpcm_threshold = required_snr(adpcm_rate)

print("REQUIRED SNR")
print("====================")
print("PCM threshold   :", round(pcm_threshold, 2), "dB")
print("ADPCM threshold :", round(adpcm_threshold, 2), "dB")