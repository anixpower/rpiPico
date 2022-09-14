import rp2
import network
import ubinascii
import machine
import urequests as requests
import time
import utime
import socket
import upip
import onewire
from machine import Pin, I2C
import utime as time
from dht import DHT11, InvalidChecksum


rp2.country('RO')
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(pm = 0xa11140) #Disable powersaving mode


mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode() # MAC address 
print('mac = ' + mac) 
# print(wlan.config('channel'))
# print(wlan.config('essid'))
# print(wlan.config('txpower'))

ssid = "MASA"
pw = "cascaval"
DeviceID = '"PicoW2"'
Status = ('""') #default status
Timer = 60 # in seconds
urlError = 'https://192.168.0.7:5001/meteo/error'
url = 'https://192.168.0.7:5001/'
header = {'Content-type': 'application/json'}
wlan.connect(ssid, pw)

# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    timeout -= 1
    print('Waiting for connection...')
    time.sleep(1)

# error code led function   
def blink_onboard_led(num_blinks):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)
    
# wifi Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth

wlan_status = wlan.status()
blink_onboard_led(wlan_status)

if wlan_status != 3:
    raise RuntimeError('Wi-Fi connection failed')
    blink_onboard_led(10)
else:
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])
    ip = '"'+status[0]+'"'

while True:
    #GET test
#     url1 = 'https://192.168.0.7:5001/testAPI/status'
#     request = requests.get(url1)
#     print(request.content)
#     request.close()
#     time.sleep(1)
    
    pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
    try:
        time.sleep(5)
        sensor = DHT11(pin)
        t  = (sensor.temperature)
        h = (sensor.humidity)
    
        print("Temperature: {}".format(sensor.temperature))
        print("Humidity: {}".format(sensor.humidity))
        temperature = sensor.temperature
        humidity = sensor.humidity
    except:
        temperature = 0
        humidity = 0
        Status = ('"Error reading DHT11"')
        print("Error reading DHT11")
    #Post temp
    payload = ('{"DeviceID": '+ DeviceID +',"DeviceIP": '+ ip +', "temp": ' + str(temperature) + ', "humidity": '+ str(round(humidity)) + ', "Status": ' + Status + '}')
    print(payload)
    try:
        print("Executing POST")
        blink_onboard_led(1)
        response = requests.post(url+'meteo/temp', headers=header, data=payload)
        #print("sent (" + str(response.status_code) + "), status = " + str(wlan.status()) )
        print("POST executed. Code: "+str(response.status_code))
        if response.status_code==200:
            Status = '""'
        response.close()
    except:
#         if status[0]
#         print("could not connect (status =" + str(wlan.status()) + ")")
#         if wlan.status() < 0 or wlan.status() >= 3:
#             print("trying to reconnect...")
#             wlan.disconnect()
#             wlan.connect(ssid, pw)
#             if wlan.status() == 3:
#                 print('connected')
#             else:
#                 print('failed')
#                 blink_onboard_led(5)
#                 time.sleep(5)
                    
        print("Run finalized. Now waiting: " + str(Timer) + " seconds.")
        time.sleep(Timer)
    
    #End Post temp
        
        
        #FUNCTIONS \/
    def error():
        payloadbody = '"'+payload+'"'
        header = {'Content-type': 'application/json'}
        payloadError = ('{"DeviceID": "PicoW1", "body": ' + Status + '}')
        print(payloadError)
        print("Executing ERROR POST")
        response2 = requests.post(urlError, headers=header, data=payloadError)
        #print("sent (" + str(response.status_code) + "), status = " + str(wlan.status()) )
        print("ERROR POST executed. Code: "+str(response2.status_code))
        response.close()
            
    def reconnect():
        print("could not connect (status =" + str(wlan.status()) + ")")
        if wlan.status() < 0 or wlan.status() >= 3:
            print("trying to reconnect...")
            wlan.disconnect()
            wlan.connect(ssid, pw)
            if wlan.status() == 3:
                print('connected')
            else:
                print('failed')
                blink_onboard_led(5)
                time.sleep(5)
                    
        print("Run finalized. Now waiting: " + str(Timer) + " seconds.")
        time.sleep(Timer)
    
