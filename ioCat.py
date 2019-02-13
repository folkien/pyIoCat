#!/usr/bin/python2.7
import argparse, os, sys
import threading
import time
import serial

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", type=str, required=True, help="input file")
parser.add_argument("-o", "--outputFile", type=str, required=True, help="output file")
parser.add_argument("-d", "--device", type=str, required=True, help="tty Device")
args = parser.parse_args()

#Assert
if (not args.inputFile):
    print "No input"
    sys.exit(1)

#Assert
if (not args.outputFile):
    print "No output"
    sys.exit(1)

#Assert
if (not args.device):
    print "No device"
    sys.exit(1)

sys.exit(1)
# Read input file size
inputSize = os.stat(args.inputFile).st_size
print "InputSize : ",inputSize,"Bytes."

# Serial port read
portHandle = serial.Serial(
    port=args.device,
    baudrate=115200,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

# Reading thread
def read():
    readedBytes=0;
    # Open write file and send lines 
    outFile = open(args.outputFile,'w')
    while (readedBytes != inputSize):
        data = portHandle.read(1000);
        if len(data) > 0:
            outFile.write(data)
            readedBytes+=len(data)
    outFile.close()

# Writing thread
def main():
    if portHandle.isOpen(): portHandle.close()
    portHandle.open()
    # Read thread creation
    t1 = threading.Thread(target=read, args=())
    # Open write file and send lines 
    inFile = open(args.inputFile,'r')
    for line in inFile:
        portHandle.write(line)
    portHandle.close()
