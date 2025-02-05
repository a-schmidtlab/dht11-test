from flask import Flask, render_template_string, jsonify
import time
import lgpio
from threading import Thread
import sys

app = Flask(__name__)

# Global variables to store sensor data
current_temperature = 0
current_humidity = 0

# DHT11 timing constants
INIT_DELAY = 0.018  # 18ms for start signal
RESPONSE_DELAY = 0.00004  # 40µs
BIT_DELAY = 0.00005  # 50µs
HIGH_LEVEL_TIME = 0.00007  # 70µs threshold for bit value

# HTML template with CSS styling
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>DHT11 Sensor Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        .sensor-data {
            font-size: 24px;
            margin: 20px;
        }
        .warning {
            color: red;
            animation: blink 1s infinite;
        }
        .safe {
            color: green;
        }
        @keyframes blink {
            50% { opacity: 0; }
        }
        .status-box {
            padding: 10px;
            margin: 10px;
            border-radius: 5px;
            display: inline-block;
        }
    </style>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <h1>DHT11 Sensor Dashboard</h1>
    
    <div class="sensor-data">
        <h2>Temperature</h2>
        <p>{{ temperature }}°C</p>
        <div class="status-box {% if temperature > 40 %}warning{% else %}safe{% endif %}">
            {% if temperature > 40 %}WARNING{% else %}IN LIMIT{% endif %}
        </div>
    </div>

    <div class="sensor-data">
        <h2>Humidity</h2>
        <p>{{ humidity }}%</p>
        <div class="status-box {% if humidity > 95 %}warning{% else %}safe{% endif %}">
            {% if humidity > 95 %}WARNING{% else %}IN LIMIT{% endif %}
        </div>
    </div>
</body>
</html>
'''

class DHT11:
    def __init__(self, pin=17):
        self.pin = pin
        self.h = lgpio.gpiochip_open(0)
        self.temperature = None
        self.humidity = None
        self.last_reading = 0
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            lgpio.gpio_free(self.h, self.pin)
            lgpio.gpiochip_close(self.h)
        except:
            pass

    def _wait_for_edge(self, level, timeout):
        start = time.time()
        while lgpio.gpio_read(self.h, self.pin) != level:
            if (time.time() - start) > timeout:
                return False
            time.sleep(0.000001)  # 1µs delay to reduce CPU usage
        return True

    def read(self):
        try:
            current_time = time.time()
            if current_time - self.last_reading < 2:
                return self.humidity, self.temperature

            print("\nAttempting to read DHT11 sensor...")
            # Initialize the sensor
            try:
                # Configure with internal pull-up
                lgpio.gpio_claim_output(self.h, self.pin)
                print("Successfully claimed GPIO for output")
                
                # Send start signal
                lgpio.gpio_write(self.h, self.pin, 1)  # Pull up first
                time.sleep(0.1)  # Wait for stable state
                lgpio.gpio_write(self.h, self.pin, 0)  # Pull down for start signal
                print("Sent start signal (LOW)")
                time.sleep(INIT_DELAY)  # Hold low for 18ms
                print("Waited for start signal")
            except Exception as e:
                print(f"Error during initialization: {str(e)}")
                return None, None
            
            # Release the line and switch to input
            try:
                lgpio.gpio_free(self.h, self.pin)
                # Configure input with pull-up
                lgpio.gpio_claim_input(self.h, self.pin)
                print("Switched to input mode")
            except Exception as e:
                print(f"Error switching to input mode: {str(e)}")
                return None, None
            
            # Wait for sensor response
            print("Waiting for sensor response...")
            time.sleep(0.00004)  # Wait 40µs for sensor to pull down
            
            if not self._wait_for_edge(0, 0.001):  # Wait for low with 1ms timeout
                print("Timeout waiting for sensor response (LOW)")
                return None, None
            if not self._wait_for_edge(1, 0.001):  # Wait for high with 1ms timeout
                print("Timeout waiting for sensor response (HIGH)")
                return None, None
            
            print("Sensor responded, reading data...")
            # Read the data
            data = []
            for i in range(40):
                if not self._wait_for_edge(0, 0.001):  # Wait for low
                    print(f"Timeout waiting for bit {i} (LOW)")
                    return None, None
                t0 = time.time()
                if not self._wait_for_edge(1, 0.001):  # Wait for high
                    print(f"Timeout waiting for bit {i} (HIGH)")
                    return None, None
                t1 = time.time()
                bit = 1 if (t1 - t0) > HIGH_LEVEL_TIME else 0
                data.append(bit)
                
            print(f"Read {len(data)} bits")
            
            # Convert data to humidity and temperature
            bytes_data = []
            byte = 0
            for i in range(40):
                byte = (byte << 1) | data[i]
                if (i + 1) % 8 == 0:
                    bytes_data.append(byte)
                    byte = 0
            
            print(f"Converted to bytes: {bytes_data}")
                    
            # Verify checksum
            checksum = ((bytes_data[0] + bytes_data[1] + bytes_data[2] + bytes_data[3]) & 0xFF)
            if bytes_data[4] == checksum:
                self.humidity = bytes_data[0]
                self.temperature = bytes_data[2]
                self.last_reading = current_time
                print(f"Checksum OK: {checksum}")
                return self.humidity, self.temperature
            else:
                print(f"Checksum failed: got {bytes_data[4]}, expected {checksum}")
                return None, None
            
        except Exception as e:
            print(f"Error reading sensor: {str(e)}")
            return None, None

# Create a global DHT11 instance
dht11 = DHT11(pin=17)

def read_sensor():
    global current_temperature, current_humidity
    
    print("Starting sensor readings on GPIO17...")
    
    while True:
        try:
            # Read from DHT11 sensor
            humidity, temperature = dht11.read()
            
            if humidity is not None and temperature is not None:
                current_temperature = temperature
                current_humidity = humidity
                print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
            else:
                print("Failed to get reading (None values)")
                
        except Exception as e:
            print(f"Unexpected error: {e}")
            
        time.sleep(2.0)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, 
                                temperature=current_temperature,
                                humidity=current_humidity)

@app.route('/sensor')
def get_sensor_data():
    humidity, temperature = dht11.read()
    if humidity is not None and temperature is not None:
        return jsonify({
            'temperature': temperature,
            'humidity': humidity
        })
    return jsonify({'error': 'Failed to read sensor'}), 500

if __name__ == '__main__':
    try:
        # Start the sensor reading in a separate thread
        sensor_thread = Thread(target=read_sensor, daemon=True)
        sensor_thread.start()
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        print("Cleaning up...")
        GPIO.cleanup() 