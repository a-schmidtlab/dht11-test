import time
import board
import adafruit_dht

# Create DHT11 device instance on GPIO12
dht_device = adafruit_dht.DHT11(board.D12)

print("[Press Ctrl+C to end the script]")

try:
    while True:
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity

            if humidity is not None and temperature is not None:
                print(f"Temp = {temperature:.1f}°C, Humidity = {humidity:.1f}%")
            else:
                print("Failed to get a valid reading. Trying again...")
        
        except RuntimeError as e:
            # Reading doesn't always work, try again
            print("Reading from DHT failure:", e)

        time.sleep(1.5)

except KeyboardInterrupt:
    print("Script ended!")
