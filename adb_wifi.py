#!/ust/bin/python

import os
import re
import sys
import time

PORT = 5555
CONFIG_FILE = '.adb_wifi.config'
SCAN_TIME = 5

# Connect to an android device
def connectToDevice(ip):
    print "Trying to connect to " + ip
    result = os.popen("adb connect " + ip + ":" + str(PORT)).read()
    if result.find("connected") != -1:
        return True
    else:
        return False

# Get all device IDs connected in an USB port
def getDecidesIDs(adbDevices):
    return re.findall('(.*?)\tdevice', adbDevices)

# Find ip from the device connect in USB port
def getIPfromDeviceID(deviceID):
    return os.popen("adb -s " + deviceID + " shell ip route | grep wlan0 | awk {\'if( NF >=9){print $9;}\'}").read().rstrip()

# Verify if the device is already connected (wifi)
def verifyIfNotConnected(adbDevices, ip):
    return adbDevices.find(ip) == -1

# Get old connections from the configuration file
def readIPConnections():
    ips = []
    if os.path.isfile(CONFIG_FILE) and os.stat(CONFIG_FILE).st_size > 0:
        with open(CONFIG_FILE, 'r') as f:
            ips = f.read().split(',')
            f.close
    return ips

# Save devices
def saveIPConnections(oldIps):
    with open(CONFIG_FILE, 'w') as f:
        print "Saving the new connections..."
        f.write(','.join(oldIps))
        f.close()


oldIps = readIPConnections()

while True:
    ipsToConnect = []
    ipsToConnect.extend(oldIps)

    adbDevices = os.popen("adb devices").read()
    for deviceID in getDecidesIDs(adbDevices):
        ip = getIPfromDeviceID(deviceID)
        if(ip != "" and verifyIfNotConnected(adbDevices, ip)):
            os.popen("adb -s " + deviceID + " tcpip " + str(PORT))
            print "Added new ip to connect " + ip
            ipsToConnect.append(ip)

    ipsConnected = []
    for ip in list(set(ipsToConnect)):
        if(verifyIfNotConnected(adbDevices, ip)):
            print "Not connected to " + ip
            if connectToDevice(ip):
                print "Connected to " + ip
                ipsConnected.append(ip)
            else:
                print "Failed to connected to " + ip

    if ipsConnected:
        oldIps.extend(ipsConnected)
        oldIps = list(set(oldIps))
        saveIPConnections(oldIps)

    time.sleep(SCAN_TIME)
