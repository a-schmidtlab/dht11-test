from flask import Flask, render_template_string, jsonify
import time
import lgpio
from threading import Thread
import signal

app = Flask(__name__)

# Global variables to store sensor data
current_temperature = 0
current_humidity = 0

def cleanup_gpio():
    """Release all GPIO resources"""
    try:
        # Get list of all GPIO chips
        for i in range(4):  # Usually there are 0-3 GPIO chips
            try:
                h = lgpio.gpiochip_open(i)
                # Try to free our pin from each chip
                try:
                    lgpio.gpio_free(h, 4)   # Free GPIO4
                    lgpio.gpio_free(h, 17)  # Free GPIO17
                    lgpio.gpio_free(h, 23)  # Free GPIO23
                except:
                    pass
                lgpio.gpiochip_close(h)
            except:
                pass
    except Exception as e:
        print(f"Cleanup error: {e}")

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
        <div class="status-box {% if humidity > 89 %}warning{% else %}safe{% endif %}">
            {% if humidity > 89 %}WARNING{% else %}IN LIMIT{% endif %}
        </div>
    </div>
</body>
</html>
'''

class DHT11:
    def __init__(self, pin=17):
        """Initialize DHT11 sensor with specified GPIO pin"""
        self.pin = pin
        
        # Clean up any existing GPIO resources
        cleanup_gpio()
        
        try:
            self.h = lgpio.gpiochip_open(0)
        except Exception as e:
            raise RuntimeError(f"Failed to open GPIO chip: {e}")
            
        self.temperature = None
        self.humidity = None
        self.last_reading = 0
        
        # Verify connection on initialization
        if not self.verify_connection():
            cleanup_gpio()
            raise RuntimeError("Failed to verify sensor connection")

    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up GPIO resources"""
        try:
            lgpio.gpio_free(self.h, self.pin)
            lgpio.gpiochip_close(self.h)
        except:
            pass

    def _wait_for_edge(self, level, timeout):
        """Wait for a signal edge (rising or falling) with timeout"""
        start = time.time()
        last_level = not level  # For debug output
        
        while lgpio.gpio_read(self.h, self.pin) != level:
            current_level = lgpio.gpio_read(self.h, self.pin)
            if current_level != last_level:
                print(f"Signal changed to {current_level} after {(time.time() - start)*1000000:.0f}µs")
                last_level = current_level
            
            if (time.time() - start) > timeout:
                return False
            time.sleep(0.000001)  # 1µs delay
        return True

    def read(self):
        """Read temperature and humidity from DHT11 sensor"""
        try:
            current_time = time.time()
            if current_time - self.last_reading < 2:
                return self.humidity, self.temperature

            print("\nAttempting to read DHT11 sensor...")
            
            # Free the pin first
            try:
                lgpio.gpio_free(self.h, self.pin)
            except:
                pass
            
            # Initialize the sensor with precise timing
            try:
                # Start with pin as input with pull-up
                lgpio.gpio_claim_input(self.h, self.pin, lgpio.SET_PULL_UP)
                time.sleep(1.0)  # Let voltage stabilize
                
                # Switch to output and send start signal
                lgpio.gpio_free(self.h, self.pin)
                lgpio.gpio_claim_output(self.h, self.pin)
                print("Successfully claimed GPIO for output")
                
                # Pull down for at least 18ms
                lgpio.gpio_write(self.h, self.pin, 0)
                print("Sent start signal (LOW)")
                time.sleep(0.018)
                
                # Pull up for 20-40µs
                lgpio.gpio_write(self.h, self.pin, 1)
                time.sleep(0.000040)
                print("Released line (HIGH)")
                
                # Switch back to input mode to receive data
                lgpio.gpio_free(self.h, self.pin)
                lgpio.gpio_claim_input(self.h, self.pin)  # No pull-up this time
                print("Switched to input mode")
                
            except Exception as e:
                print(f"Error during initialization: {str(e)}")
                return None, None
            
            # Wait for sensor response (should pull low within 20-40µs)
            print("Waiting for sensor response...")
            start_time = time.time()
            timeout = start_time + 0.000100  # 100µs timeout
            
            # Wait for LOW (response start)
            while lgpio.gpio_read(self.h, self.pin) == 1:
                if time.time() > timeout:
                    print("Timeout waiting for sensor response (still HIGH)")
                    return None, None
            response_time = (time.time() - start_time) * 1000000
            print(f"Sensor pulled LOW after {response_time:.1f}µs")
            
            # Wait for HIGH (response signal)
            start_time = time.time()
            timeout = start_time + 0.000100  # 100µs timeout
            while lgpio.gpio_read(self.h, self.pin) == 0:
                if time.time() > timeout:
                    print("Timeout waiting for sensor response (still LOW)")
                    return None, None
            response_time = (time.time() - start_time) * 1000000
            print(f"Sensor pulled HIGH after {response_time:.1f}µs")
            
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
                bit = 1 if (t1 - t0) > 0.00007 else 0
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
        finally:
            try:
                lgpio.gpio_free(self.h, self.pin)
            except:
                pass

    def verify_connection(self):
        """Verify the sensor connection by testing GPIO control"""
        try:
            print("\nVerifying sensor connection...")
            
            # Free the pin first
            try:
                lgpio.gpio_free(self.h, self.pin)
            except:
                pass
            
            # Test output mode
            lgpio.gpio_claim_output(self.h, self.pin)
            print("Successfully set pin to output mode")
            
            # Test writing HIGH
            lgpio.gpio_write(self.h, self.pin, 1)
            time.sleep(0.1)
            print("Set pin HIGH")
            
            # Test writing LOW
            lgpio.gpio_write(self.h, self.pin, 0)
            time.sleep(0.1)
            print("Set pin LOW")
            
            # Free the pin before switching modes
            lgpio.gpio_free(self.h, self.pin)
            
            # Test input mode
            lgpio.gpio_claim_input(self.h, self.pin)
            value = lgpio.gpio_read(self.h, self.pin)
            print(f"Pin value in input mode: {value}")
            
            # Free the pin when done
            lgpio.gpio_free(self.h, self.pin)
            
            return True
        except Exception as e:
            print(f"Connection verification failed: {str(e)}")
            return False

    def monitor_pin(self, duration=5.0):
        """Monitor the pin state for a specified duration"""
        print(f"\nMonitoring pin {self.pin} for {duration} seconds...")
        
        try:
            # Free the pin first
            try:
                lgpio.gpio_free(self.h, self.pin)
            except:
                pass
            
            # Configure as input with pull-up
            lgpio.gpio_claim_input(self.h, self.pin, lgpio.SET_PULL_UP)
            
            start_time = time.time()
            last_state = lgpio.gpio_read(self.h, self.pin)
            transitions = 0
            
            while (time.time() - start_time) < duration:
                current_state = lgpio.gpio_read(self.h, self.pin)
                if current_state != last_state:
                    transitions += 1
                    print(f"Pin changed to {current_state} at {(time.time() - start_time)*1000:.1f}ms")
                    last_state = current_state
                time.sleep(0.0001)  # 100µs sampling
                
            print(f"Monitoring complete. Observed {transitions} transitions.")
            
        except Exception as e:
            print(f"Error monitoring pin: {str(e)}")
        finally:
            try:
                lgpio.gpio_free(self.h, self.pin)
            except:
                pass

# Create a global DHT11 instance
dht11 = DHT11(pin=23)

def read_sensor():
    """Background thread function to continuously read sensor data"""
    global current_temperature, current_humidity
    
    print("Starting sensor readings on GPIO23...")
    
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
                # Monitor pin after failure
                dht11.monitor_pin(2.0)
                
        except Exception as e:
            print(f"Unexpected error: {e}")
            try:
                lgpio.gpio_free(dht11.h, dht11.pin)
            except:
                pass
            
        time.sleep(2.0)

@app.route('/')
def index():
    """Route for the main dashboard page"""
    return render_template_string(HTML_TEMPLATE, 
                                temperature=current_temperature,
                                humidity=current_humidity)

@app.route('/sensor')
def get_sensor_data():
    """API endpoint for getting current sensor data"""
    return jsonify({
        'temperature': current_temperature,
        'humidity': current_humidity
    })

# Add cleanup to signal handler
def signal_handler(signum, frame):
    print("\nSignal received, cleaning up...")
    cleanup_gpio()
    exit(0)

if __name__ == '__main__':
    try:
        # Register signal handler
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the sensor reading in a separate thread
        sensor_thread = Thread(target=read_sensor, daemon=True)
        sensor_thread.start()
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        print("Cleaning up...")
        try:
            lgpio.gpiochip_close(dht11.h)
        except:
            pass 