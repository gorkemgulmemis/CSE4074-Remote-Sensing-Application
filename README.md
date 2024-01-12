CSE 4074 Programming Assignment: Remote Sensing Application
Due Date: January 7th, Sunday, 23:59
In this assigment, you will implement a networked system which consists of two sensors, a
gateway, and a server. You will implement all of these modules as applications (no need for
any hardware other than your computers). The specification is given below.
Sensors:
You will have a temperature sensor and a humidity sensor. However, these are not actual
sensors; they are two applications that generate sensor values randomly and periodically send
them to the gateway. The temperature sensor is connected to the gateway via TCP, while the
humidity sensor sends values to the gateway via UDP. Every second, the temperature sensor
generates a value randomly between 20 and 30 and sends it to the gateway along with the
timestamp. Meanwhile, the humidity sensor generates random values between 40 and 90 every
second but sends information only if the humidity value exceeds 80. Additionally, every 3
seconds, the humidity sensor should send an 'ALIVE' message to indicate that it is working
properly.
Gateway:
The gateway is an application that reads values from the sensors and sends them, along with
their timestamps, to the server. Additionally, the gateway monitors sensor activities. If the
temperature sensor fails to send any values for 3 seconds, a 'TEMP SENSOR OFF' message
will be sent to the server. Similarly, if an 'ALIVE' message is not received from the humidity
sensor for more than 7 seconds, a 'HUMIDITY SENSOR OFF' message will be sent to the
server.
Server:
The server is connected to the gateway and receives messages based on a protocol defined by
you. Initially, the gateway and server should perform a handshake, after which the gateway
provides information about the connected devices. Subsequently, all data related to the
connected devices will be transmitted to the server, where it will be stored. The server will also
feature a web interface, with an HTTP process listening on port 8080. If the server is accessed
via 'http://localhost:8080/temperature,' it will send an HTML object containing all temperature
data. Similarly, when connected through 'http://localhost:8080/humidity,' an HTML object with
all humidity data will be sent. These values will be displayed in text format by any web browser.
(If you would like you may add more sophisticated graphical illustrations.)
Bonus: You will get maximum of 10 points bonus, if the humidity sensor is also capable of
sending the last measured humidity value when requested by the server (this request may be
triggered by the user via the web interface. You may define another url as
http://localhost:8080/gethumidity).
Note that the server does not have any direct communication with the sensors. The gateway
does not have any storage unit, all the values are stored in the server. The sensors are only
capable of storing the last measured value.
All the processes should display the sent and received messages on the screen. Also please
provide log files which include these received and sent messages.

Implementation
You can use any programming language of your choice (Java, Python, C, C++, etc). You should
use only socket programming. Do not use any sophisticated libraries downloaded from the
web. You will need to use multi-threaded server processes. Although we have covered the
implementation of single-threaded servers in the lecture, there are tons of materials that you
may refer for the description of multi-threaded server implementation, and also it is expected
that you have some familiarity from the Operating Systems course.
