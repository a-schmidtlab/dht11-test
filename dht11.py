import Adafruit_DHT
from time import sleep

# Choose the sensor type and the GPIO pin to which it is connected
sensor = Adafruit_DHT.DHT11
pin = 12  # DHT11 sensor connected to GPIO12

print("[Press Ctrl+C to end the script]")

try:
    while True:
        # Read the humidity and temperature from the DHT11
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

        # Wait a bit before reading again
        sleep(1.5)

        # Check if a valid reading was obtained
        if humidity is not None and temperature is not None:
            print("Temp = {0:0.1f}°C, Humidity = {1:0.1f}%".format(temperature, humidity))
        else:
            print("Failed to get reading. Try again!")
except KeyboardInterrupt:
    print("Script ended!")
