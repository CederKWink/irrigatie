import sys
import os
import time
import datetime
import select
import serial
import codecs
from multiprocessing import Process,Value
import RPi.GPIO as GPIO
import csv

filename = "adc_data.csv"

fields = ['node', 'waarde']

relayPin = 3
sensorValue = [0,1]

sPort = serial.Serial('/dev/ttyACM0', 115200, timeout=0.2)

#def readSerial():

PI_NODE =   1
NODE_1  =   2

ADC_THRESHOLD = 1000



def main():

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(relayPin, GPIO.OUT)
    GPIO.output(relayPin, GPIO.LOW)
    curNode = 1
    
    
    with open(filename, 'w') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields)
        
        
    with open(filename, 'a') as csvfile:  
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields2)

    
    
    while(True):
        bodemVochtigHeid = requestAdc(PI_NODE)
        print(bodemVochtigHeid)
        
        time.sleep(1)


    
def requestAdc(node):
    
    msg = bytearray(1)
    msg[0] = node
    sPort.write(msg)
    time.sleep(0.001)
    
    serialData = sPort.readline()
    serialData = codecs.decode(serialData).split(",")
    
    res = 0
    id = int(serialData[0])
    value = int(serialData[1])
    
    if(value > ADC_THRESHOLD):
        res = 1
    
    return res
    
    
    
    



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.output(relayPin, GPIO.LOW)
        sPort.close()
        sys.exit(0)
