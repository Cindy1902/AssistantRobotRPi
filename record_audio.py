import wave
import time
import busio
import board
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
# ads.gain = 1
SAMPLE_RATE = 8000
RECORD_SECONDS = 10
OUTPUT_FILE = "recorded_audio.wav"


def read_microphone(channel=ADS.P0, duration=5):
    """
    Doc du lieu cua MAX4466 thong qua module ADS1115.
    :params channel: So kenh cua ADS1115 (P0 - P3).
    :params duration: Thoi gian ghi am (sec).
    :return: Cac gia tri tuong ung cua ADC.
    """
    adc_values = []
    start_time = time.time()

    while time.time() - start_time < duration:
        chan = AnalogIn(ads, channel)
        adc_values.append(chan.value)
        time.sleep(1 / SAMPLE_RATE)


def save_to_wav(file_name, data, sample_rate):
    """
    Chuyen tin hieu dien qua am thanh va ghi vao file .WAV.
    :params file_name: Ten file am thanh .WAV.
    :params data: Gia tri ADC.
    :params sample_rate: Tan so lay mau.
    """
    audio_data = np.array(data, dtype=np.int16)

    with wave.open(file_name, "w") as wf:
        wf.setnchannels(1)  # 1 for mono, 2 for stereo
        wf.setsampwidth(2)  # 16-bits
        wf.setframerate(sample_rate)  # Tan so mau
        wf.writeframes(audio_data.tobytes())
    print(f"Da luu file WAV: {file_name}")


if __name__ == "__main__":
    print(f"Ghi am trong {RECORD_SECONDS} giay...")
    adc_data = read_microphone(channel=0, duration=RECORD_SECONDS)
    print(f"Da doc {len(adc_data)} mau.")

    save_to_wav(OUTPUT_FILE, adc_data, SAMPLE_RATE)
    print("Hoan tat. Kiem tra file am thanh dau ra.")
