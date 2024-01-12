import signal
import random
import socket
import threading
import time
from datetime import datetime


# TCP, UDP and server ports assigned here.
gateway_tcp_port = 8888
gateway_udp_port = 9999
server_port = 8080

# Temp and Humidity data are stored in lists there.
temperature_data = []
humidity_data = []
last_humidity_value = None

class SensorHandler:
    def __init__(self):
        # Multithreading implementation
        self.temperature_sensor_thread = threading.Thread(target=self.temperature_sensor)
        self.humidity_sensor_thread = threading.Thread(target=self.humidity_sensor)
        self.gateway_thread = threading.Thread(target=self.gateway)
        self.server_thread = threading.Thread(target=self.server)
        self.alive_thread = threading.Thread(target=self.send_alive)

        # Flag variables to track sensor status
        self.temperature_sensor_active = True
        self.humidity_sensor_active = True

        self.temperature_log_file = open("temperature_log.txt", "a")
        self.humidity_log_file = open("humidity_log.txt", "a")
        self.alive_log_file = open("alive_log.txt", "a")

        # Signal handling implemented here for exit process.
        signal.signal(signal.SIGINT, self.cleanup)

    def cleanup(self):
        # Log files closing here.
        self.temperature_log_file.close()
        self.humidity_log_file.close()
        self.alive_log_file.close()
        exit()

    def temperature_sensor(self):
        # Thread for temperature sensor and sending data to the gateway with TCP protocol.
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            tcp_socket.connect(('localhost', gateway_tcp_port))

            while self.temperature_sensor_active:
                # Random temperature value and timestamp generated there. Sends to gateway.
                temperature_value = round(random.uniform(20, 30), 1)
                timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M")
                message = f'TEMPERATURE|{temperature_value}|{timestamp}'
                tcp_socket.send(message.encode())
                temperature_data.append((temperature_value, timestamp))
                print(f'Temperature Sensor - Value: {temperature_value}, Timestamp: {timestamp}')
                self.temperature_log_file.write(
                    f'Temperature Sensor - Value: {temperature_value}, Timestamp: {timestamp}\n')
                self.temperature_log_file.flush()
                time.sleep(1)

        except Exception as e:
            print(f"Temperature Sensor - Error: {e}")

        finally:
            tcp_socket.close()
            print('Temperature Sensor - OFF')

    def humidity_sensor(self):
        # Thread for humidity sensor and sending data.
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            while self.humidity_sensor_active:
                # Random humidity value and timestamp implemented there.
                humidity_value = round(random.uniform(40, 90), 1)
                if humidity_value > 80:
                    timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M")
                    message = f'HUMIDITY|{humidity_value}|{timestamp}'
                    udp_socket.sendto(message.encode(), ('localhost', gateway_udp_port))
                    humidity_data.append((humidity_value, timestamp))
                    global last_humidity_value
                    last_humidity_value = humidity_value
                    print(f'Humidity Sensor - Value: {humidity_value}, Timestamp: {timestamp}')
                    self.humidity_log_file.write(f'Humidity Sensor - Value: {humidity_value}, Timestamp: {timestamp}\n')
                    self.humidity_log_file.flush()
                time.sleep(1)

        except Exception as e:
            print(f"Humidity Sensor - Error: {e}")

        finally:
            udp_socket.close()
            print('Humidity Sensor - OFF')

    def send_alive(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            while True:
                # Alive message send with timestamp value in every 3 seconds.
                timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M")
                message = f'ALIVE|{timestamp}'
                udp_socket.sendto(message.encode(), ('localhost', gateway_udp_port))
                print(f'Humidity Sensor - ALIVE message sent at: {timestamp}')
                self.alive_log_file.write(f'Humidity Sensor - ALIVE message sent at: {timestamp}\n')
                self.alive_log_file.flush()
                time.sleep(3)

        except Exception as e:
            print(f"ALIVE Sender - Error: {e}")

        finally:
            udp_socket.close()

    def gateway(self):
        # Thread implementation for handling communication via gateway.(TCP and UDP protocols)
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.bind(('localhost', gateway_tcp_port))
        tcp_server.listen(5)

        udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server.bind(('localhost', gateway_udp_port))

        temperature_last_received = time.time()
        humidity_last_received = time.time()

        while True:
            try:
                # Checking temperature sensor status
                if time.time() - temperature_last_received > 3 and self.temperature_sensor_active:
                    print('Gateway - TEMP SENSOR OFF')
                    self.temperature_sensor_active = False
                    continue

                # Checking humidity sensor status
                if time.time() - humidity_last_received > 7 and self.humidity_sensor_active:
                    print('Gateway - HUMIDITY SENSOR OFF')
                    self.humidity_sensor_active = False

                # Accept and data process comes from TCP client and UDP message.
                tcp_client, _ = tcp_server.accept()
                tcp_data = tcp_client.recv(1024).decode()
                self.process_data(tcp_data)
                temperature_last_received = time.time()

                udp_data, _ = udp_server.recvfrom(1024)
                self.process_data(udp_data.decode())
                humidity_last_received = time.time()

            except Exception as e:
                print(f"Gateway - Error: {e}")

    def process_data(self, data):
        parts = data.split('|')
        sensor_type = parts[0]
        if sensor_type == 'TEMPERATURE':
            temperature_value = float(parts[1])
            timestamp = parts[2]
            temperature_data.append((temperature_value, timestamp))
            print(f'Gateway - Received Temperature Data: {temperature_value:.1f}, Timestamp: {timestamp}')
        elif sensor_type == 'HUMIDITY':
            humidity_value = float(parts[1])
            timestamp = parts[2]
            humidity_data.append((humidity_value, timestamp))
            global last_humidity_value
            last_humidity_value = humidity_value
            print(f'Gateway - Received Humidity Data: {humidity_value:.1f}, Timestamp: {timestamp}')

    def server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('localhost', server_port))
            server_socket.listen()

            while True:
                client_socket, addr = server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        # Method to handle HTTP client requests implemented without HTTP server module.
        with client_socket:
            request = client_socket.recv(1024).decode('utf-8')
            path = request.split(' ')[1]

            response_header = "HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n"
            response_body = ""

            style = """
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    margin: 20px;
                    background-color: #f4f4f4;
                }
                h2 {
                    color: #333;
                    text-align: center;
                    background-color: #e0e0e0;
                    padding: 10px;
                    border-radius: 5px;
                }
                hr {
                    border: 1px solid #ddd;
                }
                .logo {
                    max-width: 100px;
                    max-height: 100px;
                    display: block;
                    margin: 0 auto;
                }
                p {
                    color: #555;
                }
            </style>
            """

            if path == "/temperature":

                response_body += f"<html><head><title>Temperature Data</title>{style}</head><body><h2>Temperature Data</h2><hr>"
                for temp, timestamp in temperature_data:
                    response_body += f"<p>Temperature: {temp}, Timestamp: {timestamp}</p><hr>"
                response_body += "</body></html>"

            elif path == "/humidity":

                response_body += f"<html><head><title>Humidity Data</title>{style}</head><body><h2>Humidity Data</h2><hr>"
                for hum, timestamp in humidity_data:
                    response_body += f"<p>Humidity: {hum}, Timestamp: {timestamp}</p><hr>"
                response_body += "</body></html>"

            elif path == "/gethumidity":

                response_body += f"<html><head><title>Last Humidity Value</title>{style}</head><body><h2>Last Humidity Value</h2><hr>"
                if last_humidity_value is not None:
                    response_body += f"<p>Last Humidity Value: {last_humidity_value}</p><hr>"
                else:
                    response_body += "<p>No humidity data available</p><hr>"
                response_body += "</body></html>"

            else:
                response_header = "HTTP/1.1 404 Not Found\r\nContent-type: text/html\r\n\r\n"
                response_body = "<html><head><title>404 Not Found</title>{style}</head><body><h1>404 Not Found</h1></body></html>"

            client_socket.sendall((response_header + response_body).encode('utf-8'))

    def start(self):
        self.temperature_sensor_thread.start()
        self.humidity_sensor_thread.start()
        self.gateway_thread.start()
        self.server_thread.start()
        self.alive_thread.start()

# Creating an example of SensorHandler class to start thread's process.
sensor_handler = SensorHandler()
sensor_handler.start()
