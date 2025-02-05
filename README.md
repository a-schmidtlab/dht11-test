# DHT11 Temperature and Humidity Sensor Test

This code is a sample code for later integration in the GUPPY project.
It uses a Raspberry Pi 5 with Debian GNU/Linux 12 (bookworm) to read out the AZDelivery DHT11 sensor.
The code is written in Python and uses the Adafruit CircuitPython DHT library for simple and reliable sensor readings.

## Features
- Continuously reads temperature and humidity from DHT11 sensor
- Displays readings in the terminal
- Handles reading errors gracefully
- Updates every 1.5 seconds

## Setup Instructions

1. Install required system packages:
```bash
sudo apt update
sudo apt install python3-full python3-dev python3-pip
```

2. Create and activate a virtual environment:
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

3. Install the Python dependencies:
```bash
pip install adafruit-circuitpython-dht
```

4. Run the script:
```bash
python dht11.py
```

Note: Every time you want to run the script, make sure to activate the virtual environment first using:
```bash
source venv/bin/activate
```

## Wiring Details

The AZDelivery DHT11 sensor module comes as a 3-pin module with a built-in pull-up resistor on a blue PCB board. This means no additional resistor is needed for the setup.

### Pin Configuration:
- Pin 1 (Left): VCC (Power Supply)
- Pin 2 (Middle): DATA (Signal)
- Pin 3 (Right): GND (Ground)

### Connection to Raspberry Pi:
- VCC (Left pin) → 3.3V (Pin 1 on Raspberry Pi)
- DATA (Middle pin) → GPIO12 (Pin 32 on Raspberry Pi)
- GND (Right pin) → Ground (Pin 6 on Raspberry Pi)

### Pin Diagram
```
Raspberry Pi   AZDelivery DHT11
3.3V (Pin 1) → VCC (Left)
GPIO12 (Pin 32) → DATA (Middle)
GND (Pin 6)  → GND (Right)
```








