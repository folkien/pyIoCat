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

semaphoreStartSynchro = threading.Semaphore()

# Read input file size
inputSize = os.stat(args.inputFile).st_size

# Serial port read
portHandle = serial.Serial(
    port=args.device,
    baudrate=115200,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)
if portHandle.isOpen(): 
    portHandle.close()
portHandle.open()
print "Port ",args.device," opened."

# Reading thread
def read():
    print "Output to ",args.outputFile,"."
    outFile = open(args.outputFile,'w')
    readedBytes=0;
    maxNoDataTime=5 #[s]
    lastDataTime=time.time()
    semaphoreStartSynchro.release()
    while ((readedBytes != inputSize) and ((time.time() - lastDataTime) < maxNoDataTime)):
        data = portHandle.read(100);
        if len(data) > 0:
            outFile.write(data)
            readedBytes+=len(data)
            lastDataTime=time.time()
            print "Readed ",readedBytes,"/",inputSize,"."
        else:
            print "No data time",(time.time() - lastDataTime),"s."
    outFile.close()

# Writing thread
def main():
    # Read thread creation
    semaphoreStartSynchro.acquire()
    tRead = threading.Thread(target=read, args=())
    tRead.start()

    # Wait on start synchronization semaphore
    semaphoreStartSynchro.acquire()

    # Open write file and send lines 
    print "Input from ",args.inputFile,"."
    print "InputSize : ",inputSize,"Bytes."
    inFile = open(args.inputFile,'r')
    for line in inFile:
        portHandle.write(line)

    # Wait on reading thread and close port
    tRead.join()
    print "Port ",args.device," closed."
    portHandle.close()

# Call main
main()
