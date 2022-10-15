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

initialTime = time.time()

sPort = serial.Serial('/dev/ttyACM0', 115200, timeout=0.2)

PI_NODE =   1
NODE_1  =   2

ADC_THRESHOLD = 850


#def readSerial():
ON = 1
OFF = 0
HOOG = 1
LAAG = 0

pompStartTijd = 0
pompLooptijd = 3
pompState = OFF

bodemVochtigheid = LAAG
vochtigheidOpvragenLang = 3#60*60*6
tijdVorigeOpvraging = 0


def pompAan(CT): 
    global pompStartTijd
    global pompState
    pompStartTijd = CT
    pompState = ON
    GPIO.output(relayPin, GPIO.HIGH)

def pompUit():
    global pompState
    pompState = OFF
    print("Pomp gestopt")
    GPIO.output(relayPin, GPIO.LOW)

def controleerTijd(CT):
    res = False
    global pompStartTijd
    if(CT - pompStartTijd >= pompLooptijd):
        res = True
    
    return res

def vraagBodemVochtigheid(CT):
    global bodemVochtigheid
    global tijdVorigeOpvraging
    global vraagBodemVochtigheid
    if(CT - tijdVorigeOpvraging >= vochtigheidOpvragenLang):
        bodemVochtigheid = requestAdc(PI_NODE)  
        tijdVorigeOpvraging = CT      


    
def requestAdc(node):
    
    msg = bytearray(1)
    msg[0] = node
    sPort.write(msg)
    time.sleep(0.001)
    
    serialData = sPort.readline()
    serialData = codecs.decode(serialData).split(",")
    
    with open(filename, 'a') as csvfile:  
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(serialData)
        
    res = LAAG
    id = int(serialData[0])
    value = int(serialData[1])
    print("adc = {}".format(value))
    
    if(node == PI_NODE):
        if(value < ADC_THRESHOLD):
            res = HOOG
    
    
    print("res = {}".format(res))
    return res
    
    
    

def main():

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(relayPin, GPIO.OUT)
    GPIO.output(relayPin, GPIO.LOW)

    
    with open(filename, 'w') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(fields)
        
    global bodemVochtigheid
    global tijdVorigeOpvraging

    while(1):
        currentTime = time.time()
        if(bodemVochtigheid == LAAG and pompState == OFF):
            print("Pompen")
            pompAan(currentTime)
        elif(pompState == ON and controleerTijd(currentTime) == True):
            print("pomp tijd verstreken")
            bodemVochtigheid = requestAdc(PI_NODE)
            if(bodemVochtigheid == HOOG):
                print("bodem vochtig")
                pompUit()
                tijdVorigeOpvraging = currentTime
            else: 
                print("bodem droog")
                pompAan(currentTime)
        elif(pompState == OFF):
            vraagBodemVochtigheid(currentTime)
        time.sleep(1)



        


#    currentTime = time.time()
#    pompAan(currentTime)
#    print("Seconds since epoch =", seconds)	



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.output(relayPin, GPIO.LOW)
        sPort.close()
        sys.exit(0)
