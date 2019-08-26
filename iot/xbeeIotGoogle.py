import serial
import os

import argparse
import datetime
import json
import ssl
import time

import jwt
import paho.mqtt.client as mqtt

xbee_cache_list_api_0x83 = []
xbee_cache_list_api_0x81 = []
ser = serial.Serial()

# Variables de conexion de GCC

registry_id = 'casa-consumoTot'
device_id = 'rasp1'
project_id = 'asistente-180018'
private_key_file = 'private-key.pem'
algorithm = 'RS256'
ca_certs = 'roots.pem'
cloud_region = 'us-central1'

mqtt_bridge_hostname = 'mqtt.googleapis.com'
mqtt_bridge_port = 8883
message_type = 'event'
num_messages = 100


def create_jwt(project_id, private_key_file, algorithm):
    """Create a JWT (https://jwt.io) to establish an MQTT connection."""
    token = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1000),
        'aud': project_id
    }
    with open(private_key_file, 'r') as f:
        private_key = f.read()
    print('Creating JWT using {} from private key file {}'.format(
        algorithm, private_key_file))
    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


class Device(object):
    """Represents the state of a single device."""

    def __init__(self):
        #  print "entro aca1"
        self.temperature = 0
        self.fan_on = False
        self.connected = False

    #   print "entro aca2"

    def update_sensor_data(self):
        # print "entro aca3"
        """Pretend to read the device's sensor data.
        If the fan is on, assume the temperature decreased one degree,
        otherwise assume that it increased one degree.
        """
        if self.fan_on:
            self.temperature -= 1
        else:
            self.temperature += 1

    def wait_for_connection(self, timeout):
        """Wait for the device to become connected."""
        total_time = 0
        while not self.connected and total_time < timeout:
            time.sleep(1)
            total_time += 1

        if not self.connected:
            raise RuntimeError('Could not connect to MQTT bridge.')

    def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
        """Callback for when a device connects."""
        print('Connection Result:', error_str(rc))
        self.connected = True

    def on_disconnect(self, unused_client, unused_userdata, rc):
        """Callback for when a device disconnects."""
        print('Disconnected:', error_str(rc))
        self.connected = False

    def on_publish(self, unused_client, unused_userdata, unused_mid):
        """Callback when the device receives a PUBACK from the MQTT bridge."""
        print('Published message acked.')

    def on_subscribe(self, unused_client, unused_userdata, unused_mid,
                     granted_qos):
        """Callback when the device receives a SUBACK from the MQTT bridge."""
        print('Subscribed: ', granted_qos)
        if granted_qos[0] == 128:
            print('Subscription failed.')

    def on_message(self, unused_client, unused_userdata, message):
        """Callback when the device receives a message on a subscription."""
        payload = message.payload.decode('utf-8')
        print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))

        # The device will receive its latest config when it subscribes to the
        # config topic. If there is no configuration for the device, the device
        # will receive a config with an empty payload.
        if not payload:
            return

        # The config is passed in the payload of the message. In this example,
        # the server sends a serialized JSON string.
        data = json.loads(payload)
        if data['fan_on'] != self.fan_on:
            # If changing the state of the fan, print a message and
            # update the internal state.
            self.fan_on = data['fan_on']
            if self.fan_on:
                print('Fan turned on.')
            else:
                print('Fan turned off.')


def enviarmensale(corriente):
    # This is the topic that the device will publish telemetry events
    # (temperature data) to.
    mqtt_telemetry_topic = '/devices/{}/events'.format(device_id)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    # Wait up to 5 seconds for the device to connect.
    device.wait_for_connection(15)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)
    payload = json.dumps({'corriente': corrientecasa})
    print('Publishing payload', payload)
    client.publish(mqtt_telemetry_topic, payload, qos=1)
    # client.disconnect()


def openSerial(port, baudrate):
    ser.port = port
    ser.baudrate = baudrate
    ser.bytesize = serial.EIGHTBITS
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_ONE
    ser.timeout = 1  # non-block read
    ser.xonxoff = False  # disable software flow control
    ser.rtscts = False  # disable hardware (RTS/CTS) flow control
    ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
    try:
        ser.open()
    except Exception as e:
        print( "error open serial port: " + str(e))
        exit()


def getBit(int_type, offset):
    mask = 1 << offset
    if (int_type & mask):
        return True
    else:
        return False


def get_data_type(int_arr):
    return int_arr[3]


def get_xbee16(int_arr):
    return int_arr[4] * 256 + int_arr[5]


def get_rssi(int_arr):
    return int_arr[6]


def get_values_api_0x83(int_arr):
    datalist = [0, 0, 0, 0, 0, 0, 0, 0]  # a[0-6], digital
    data1 = int_arr[9]
    data2 = int_arr[10]
    ddigital = (getBit(data1, 0) or data2 > 0)
    da0 = getBit(data1, 1)
    da1 = getBit(data1, 2)
    da2 = getBit(data1, 3)
    da3 = getBit(data1, 4)
    da4 = getBit(data1, 5)
    da5 = getBit(data1, 6)
    da6 = getBit(data1, 7)
    pos = 11
    keep = True
    while pos + 1 < len(int_arr) and keep:
        keep = False
        if ddigital:
            datalist[7] = 256 * int_arr[pos] + int_arr[pos + 1]  # Digital
            pos += 2
            ddigital = False
            keep = True
        elif da0:
            datalist[0] = 256 * int_arr[pos] + int_arr[pos + 1]
            pos += 2
            da0 = False
            keep = True
        elif da1:
            datalist[1] = 256 * int_arr[pos] + int_arr[pos + 1]
            pos += 2
            da1 = False
            keep = True
        elif da2:
            datalist[2] = 256 * int_arr[pos] + int_arr[pos + 1]
            pos += 2
            da2 = False
            keep = True
        elif da3:
            datalist[3] = 256 * int_arr[pos] + int_arr[pos + 1]
            pos += 2
            da3 = False
            keep = True
        elif da4:
            datalist[4] = 256 * int_arr[pos] + int_arr[pos + 1]
            pos += 2
            da4 = False
            keep = True
        elif da5:
            datalist[5] = 256 * int_arr[pos] + int_arr[pos + 1]
            pos += 2
            da5 = False
            keep = True
        elif da6:
            datalist[6] = 256 * int_arr[pos] + int_arr[pos + 1]
            pos += 2
            da6 = False
            keep = True
    return datalist


def get_values_api_0x81(int_arr):
    datalist = ""
    for x in range(8, len(int_arr) - 2):
        chara = "" + str(chr(int_arr[x]))
        datalist += chara
    return datalist


###################################################################################

openSerial(os.path.realpath("/dev/ttyUSB0"), 9600)

client = mqtt.Client(
    client_id='projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, cloud_region, registry_id,
                                                                         device_id))
client.username_pw_set(username='unused', password=create_jwt(project_id, private_key_file, algorithm))
client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

device = Device()

client.on_connect = device.on_connect
client.on_publish = device.on_publish
client.on_disconnect = device.on_disconnect
client.on_subscribe = device.on_subscribe
client.on_message = device.on_message
client.connect(mqtt_bridge_hostname, mqtt_bridge_port)
client.loop_start()

if ser.isOpen():
    print ("Opened")
    buf = []  # lista
    while (True):
        rawdata_s = ser.read(1)  # es un str
        if len(rawdata_s) > 0:
            rawdata = ord(rawdata_s)  # es un int
            if rawdata == 126:  # inicio de trama 7E

                if len(buf) >= 10:
                    data_type = get_data_type(buf)
                    if data_type == 129:
                        values = get_values_api_0x81(buf)
                        xbee16 = get_xbee16(buf)
                        rssi = get_rssi(buf)
                        print ("API2: " + str(buf) + " -> " + str(values))
                        if buf[5] == 32:
                            print ("potencia es: ")
                            corrientecasa = buf[10] * 256 + buf[11]
                            print (corrientecasa)
                            enviarmensale(corrientecasa)

                    # save_data_api_0x81(values,xbee16,rssi)
                    elif data_type == 131 and len(buf) >= 12:
                        values = get_values_api_0x83(buf)
                        xbee16 = get_xbee16(buf)
                        rssi = get_rssi(buf)
                        # print "API0: " + str(buf) + " -> " + str(values)
                        # save_data_api_0x83(values,xbee16,rssi)
                    else:
                        print ("INVALID: " + str(buf))
                buf = []
                buf.append(rawdata)
            else:
                buf.append(rawdata)




