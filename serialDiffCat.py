#!/usr/bin/python2.7
import argparse, os, sys
import threading
import time
import serial
import math

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", type=str, required=True, help="input file")
parser.add_argument("-o", "--outputFile", type=str, required=True, help="output file")
parser.add_argument("-d", "--device", type=str, required=True, help="tty Device")
parser.add_argument("-B", "--baudrate", type=int, required=False, help="")
parser.add_argument("-P", "--parity", type=str, required=False, help="")
parser.add_argument("-t", "--transmitSize", type=int, required=False, help="Size of transmited frame")
parser.add_argument("-g", "--graph", action='store_true', required=False, help="Transfer graph plot")
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

#Config check
if (not args.baudrate):
    defaultBaudrate=115200
else:
    defaultBaudrate=args.baudrate

#Config check
if (not args.parity):
    defaultParity=serial.PARITY_EVEN
else:
    if args.parity == "even":
        defaultParity=serial.PARITY_EVEN
    elif args.parity == "odd":
        defaultParity=serial.PARITY_ODD
    else:
        defaultParity=serial.PARITY_NONE

#Config check
if (not args.transmitSize):
    defaultTransmitSize=1024
else:
    defaultTransmitSize=args.transmitSize

#Config check
if (args.graph):
    import matplotlib.pyplot as plt
    plot_time = []
    plot_RxData = []
    plot_TxData = []

semaphoreStartSynchro = threading.Semaphore()

# Read input file size
inputSize = os.stat(args.inputFile).st_size

# Serial port read
portHandle = serial.Serial(
    port=args.device,
    baudrate=defaultBaudrate,
    rtscts=True,
    parity=defaultParity,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=3,
    write_timeout=10
)
if portHandle.isOpen():
    portHandle.close()
portHandle.open()
print "Port ",args.device," opened."

# Variable with state of Rx Thread
TxTransmitted=0

# Writing thread
def main():
    global RxThreadRunning
    global TxTransmitted
    isError=0

    # Open write file and send lines
    print "Input from ",args.inputFile,"."
    print "Input size : ",inputSize,"Bytes."
    print "Chunk size : ",defaultTransmitSize,"."
    inFile = open(args.inputFile,'r')
    # Inifinite loop through file
    while (isError == 0) :
        for chunk in iter(lambda: inFile.read(defaultTransmitSize), ''):
            writeSize       = portHandle.write(chunk)
            readedChunk     = portHandle.read(defaultTransmitSize);
            # Check data was read
            if len(readedChunk) == 0:
                isError = 1
                print "Timeout error!"
                break;
            # Compare data
            if (chunk != readedChunk):
                isError = 1
                print "Verify error!"
                break;

            TxTransmitted   += writeSize
            # Print trace info
            sys.stdout.write("\rTransmitted %dB" % (TxTransmitted))
            sys.stdout.flush()
        inFile.seek(0)


    print "Port ",args.device," closed."
    portHandle.close()

# Call main
main()
