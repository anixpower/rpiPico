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
import ds18x20
from machine import Pin, I2C
import utime as time
from dht import DHT11, InvalidChecksum
#try use ds18b20 temp sensor

#FOR Dallas sensor
# ds_pin = machine.Pin(28)
# ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
# roms = ds_sensor.scan()
# print('Found DS devices: ', roms)
#END Dallas sensor

#FOR DHT sensor
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=200000)
#END DHT sensor

temperature = 0
humidity = -1

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
DeviceID = '"PicoW1"'
Status = ('""') #default status
Timer = 60 # in seconds
urlError = 'https://192.168.0.10:5002/meteo/error'
url = 'https://192.168.0.10:5002/'
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
        time.sleep(.1)
        led.off()
        time.sleep(.1)
    
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
    
        #FUNCTIONS \/
    def error():
        payloadbody = '"'+payload+'"'
        header = {'Content-type': 'application/json'}
        payloadError = ('{"DeviceID": "PicoW1", "body": ' + Status + '}')
        print(payloadError)
        print("Executing ERROR POST")
        response2 = requests.post(urlError, headers=header, data=payloadError)
        print("sent (" + str(response.status_code) + "), status = " + str(wlan.status()) )
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

    def readDS():
        try:
            ds_sensor.convert_temp()
            time.sleep_ms(750)
            for rom in roms:
                print(rom)
                print(ds_sensor.read_temp(rom))
                global temperature
                temperature = ds_sensor.read_temp(rom)
            print(temperature)
        except:
            Status = ('"Error reading DS sensor."')
            temperature = 0
            humidity = 0
            print(Status)

    def readDHT():
        try:
            pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
            time.sleep(1)
            sensor = DHT11(pin)
            t  = (sensor.temperature)
            h = (sensor.humidity)
            print("Temperature: {}".format(sensor.temperature))
            print("Humidity: {}".format(sensor.humidity))
            global temperature
            temperature = t
            global humidity 
            humidity = h
            #print(temperature)
        except:
            Status = ('"Error reading DHT sensor."')
            temperature = 0
            humidity = 0
    # END FUNCTIONS /\
    
    
    #GET test
#     url1 = 'https://192.168.0.10:5001/meteo/s'
#     request = requests.get(url1)
#     print(str(request.content))
#     request.close()
#     time.sleep(1)
#     
    readDHT()
    #readDS():
        
    time.sleep_ms(750)
    #print(temperature)

    
    #Post temp
    payload = ('{"DeviceID": '+ DeviceID +',"DeviceIP": '+ ip +', "temp": ' + str(temperature) + ', "humidity": '+ str(round(humidity)) + ', "Status": ' + Status + '}')
    print(payload)
    try:
        print("Executing POST")
        blink_onboard_led(1)
        response = requests.post(url+'meteo/temp', headers=header, data=payload)
        print("sent (" + str(response.status_code) + "), status = " + str(wlan.status()) )
        print("POST executed. Code: "+str(response.status_code))
        if response.status_code==200:
            Status = '""'
        response.close()
    except:
            print('Post failed.No connection or API server unreachable.')
            reconnect()
    #End Post temp
        
        
    
    print("Run finalized. Now waiting: " + str(Timer) + " seconds.")
    time.sleep(Timer)
    
