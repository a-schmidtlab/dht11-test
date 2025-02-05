This code is a sample code for later integration in the GUPPY project.
It uses a Raspberry pi 5 with Debian GNU/Linux 12 (bookworm) to read out the AZDelivery DHT11 sensor.
The code is written in Python.
The code is designed to be run on the Raspberry pi 5.
I displays the temperature and humidity values on a simple web page. 
Is shows a red warning sign if the temperature is above 40° The sign are the red word WARNING and is blinking.
It also shows a green sign if the temperature is below 40° The sign are the green word IN LIMIT and is not blinking.
Is shows a red warning sign if the humidity is above 95% The sign are the red word WARNING and is blinking.
It also shows a green sign if the humidity is below 95% The sign are the green word IN LIMIT and is not blinking.

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the web interface by opening a browser and navigating to:
```
http://<raspberry_pi_ip>:5000
```

## Wiring Details

The AZDelivery DHT11 sensor module comes as a 3-pin module with a built-in pull-up resistor on a blue PCB board. This means no additional resistor is needed for the setup.

### Pin Configuration:
- Pin 1 (Left): VCC (Power Supply)
- Pin 2 (Middle): DATA (Signal)
- Pin 3 (Right): GND (Ground)

### Connection to Raspberry Pi:
- VCC (Left pin) → 3.3V (Pin 1 on Raspberry Pi)
- DATA (Middle pin) → GPIO4 (Pin 7 on Raspberry Pi)
- GND (Right pin) → Ground (Pin 6 on Raspberry Pi)

### Pin Diagram
```
Raspberry Pi   AZDelivery DHT11
3.3V (Pin 1) → VCC (Left)
GPIO4 (Pin 7) → DATA (Middle)
GND (Pin 6)  → GND (Right)
```

## Important Notes
- Make sure the sensor is properly connected before running the code
- The web interface automatically refreshes every 5 seconds
- Temperature warnings trigger at > 40°C
- Humidity warnings trigger at > 95%
- The sensor readings update every 2 seconds
- The AZDelivery DHT11 module has a built-in pull-up resistor, so no additional resistor is needed
- Operating voltage: 3.3V to 5.5V (we use 3.3V for safety with Raspberry Pi)
- Temperature range: 0°C to 50°C
- Humidity range: 20% to 90%
- Sampling rate: 1Hz (one reading every second)







