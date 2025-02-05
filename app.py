from flask import Flask, render_template_string
import Adafruit_DHT
import time
from threading import Thread

app = Flask(__name__)

# Global variables to store sensor data
current_temperature = 0
current_humidity = 0

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

def read_sensor():
    global current_temperature, current_humidity
    # DHT11 sensor connected to GPIO4
    DHT_SENSOR = Adafruit_DHT.DHT11
    DHT_PIN = 4

    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        if humidity is not None and temperature is not None:
            current_temperature = temperature
            current_humidity = humidity
        time.sleep(2)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, 
                                temperature=current_temperature,
                                humidity=current_humidity)

if __name__ == '__main__':
    # Start the sensor reading in a separate thread
    sensor_thread = Thread(target=read_sensor, daemon=True)
    sensor_thread.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000) 