from machine import Pin
import machine
import time
import ujson
from umqtt.simple import MQTTClient

led = None
node_name = None
ssid = None
password = None
broker = None

def mqtt_msg(topic, msg):
    print("topic:", topic)
    print("message:", msg.decode("utf-8"))
    
    if topic.decode("utf-8") == (node_name + "/relay/set"):
        if msg.decode("utf-8") == 'OFF':
            print("LED OFF")
            client.publish(node_name + "/relay", "OFF")
            led.value(1)
        if msg.decode("utf-8") == 'ON':
            print("LED ON")
            client.publish(node_name + "/relay", "ON")
            led.value(0)

def mqtt_init():
    global client
    print("Initializing MQTT client.")
    print("node name: ", node_name)
    print("broker: ", broker)
    
    client = MQTTClient(node_name, broker)
    client.set_callback(mqtt_msg)

    client.connect()
    
    print("subscribing to ", node_name + "/hass_set")
    client.subscribe(node_name + "/relay/hass_set")

def wifi_connect(ssid, password):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network: ', ssid )
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

cfg_file = open("config.json", "r")
json_str = cfg_file.read()
cfg_file.close()
json = ujson.loads(json_str)

node_name = json["name"]
ssid = json["ssid"]
password = json["pass"]
broker = json["broker"]

led = Pin(2, Pin.OUT)
led.on()
time.sleep(1)
led.off()
time.sleep(1)
led.on()

try:
    wifi_connect(ssid, password)
    mqtt_init()
except Exception as err:
    machine.reset()

relay_stat = True

last_time = time.time()
while True:
    try:
        client.check_msg()
        if (time.time() - last_time) > 2:
            print("sending to ", node_name + "/relay/hass_set")
            if relay_stat == True:
                client.publish(node_name + "/relay/hass_set", "OFF")
                relay_stat = False
            else:
                client.publish(node_name + "/relay/hass_set", "ON")
                relay_stat = True
                
            last_time = time.time()
    except Exception as e:
        print("Zajeb:",e)
        machine.reset()
        pass
        

