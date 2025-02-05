This code is a sample code for later integration in the GUPPY project.
It uses a Raspberry pi 5 with Debian GNU/Linux 12 (bookworm) to read out the AZDelivery DHT11 sensor.
The code is written in Python and uses the lgpio library, which is specifically designed for Raspberry Pi 5.
The code displays the temperature and humidity values on a simple web page. 

## Features
- Shows temperature and humidity readings from DHT11 sensor
- Displays a red warning sign if the temperature is above 40°C (blinking)
- Shows a green "IN LIMIT" sign if the temperature is below 40°C (not blinking)
- Shows a red warning sign if the humidity is above 89% (blinking)
- Shows a green "IN LIMIT" sign if the humidity is below 89% (not blinking)

## Setup Instructions

1. Install required system packages:
```bash
sudo apt update
sudo apt install python3-full python3-dev python3-pip python3-lgpio
```

2. Create and activate a virtual environment:
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

3. Install the Python dependencies in the virtual environment:
```bash
pip install -r requirements.txt
```

4. Set up GPIO permissions:
```bash
# Add your user to the gpio group
sudo usermod -a -G gpio $USER

# Log out and log back in for the changes to take effect
```

5. Run the application:
```bash
python app.py
```

6. Access the web interface by opening a browser and navigating to:
```
http://<raspberry_pi_ip>:5000
```

Note: Every time you want to run the application, make sure to activate the virtual environment first using:
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
- DATA (Middle pin) → GPIO17 (Pin 11 on Raspberry Pi)
- GND (Right pin) → Ground (Pin 6 on Raspberry Pi)

### Pin Diagram
```
Raspberry Pi   AZDelivery DHT11
3.3V (Pin 1) → VCC (Left)
GPIO17 (Pin 11) → DATA (Middle)
GND (Pin 6)  → GND (Right)
```








