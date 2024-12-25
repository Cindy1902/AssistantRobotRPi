import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)

adc = ADS.ADS1115(i2c)

GAIN = 1


def read_microphone(channel=0):
    """
    Read signal of MAX4466 using ADS1115
    :param channel: ADS channels (0-3).
    :return: ADC value (from -32768 to 32768)
    """
    adc_value = adc.read_adc(channel, gain=GAIN)
    voltage = adc_value * 4.096 / 32767
    return adc_value, voltage


try:
    print("Start recording. Press Ctrl+C to stop!")
    while True:
        adc, voltage = read_microphone(0)
        print(f"ADC Value: {adc}, Voltage: {voltage:.3f} V")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Stop recording.")
