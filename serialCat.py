#!/usr/bin/python2.7
import argparse, os, sys
import threading
import time
import serial

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", type=str, required=True, help="input file")
parser.add_argument("-o", "--outputFile", type=str, required=True, help="output file")
parser.add_argument("-d", "--device", type=str, required=True, help="tty Device")
parser.add_argument("-B", "--baudrate", type=int, required=False, help="")
parser.add_argument("-P", "--parity", type=str, required=False, help="")
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
    timeout=1,
    write_timeout=3
)
if portHandle.isOpen():
    portHandle.close()
portHandle.open()
print "Port ",args.device," opened."

# Variable with state of Rx Thread
global RxThreadRunning
RxThreadRunning=0

# Reading thread
def read():
    print "Output to ",args.outputFile,"."
    outFile = open(args.outputFile,'w')
    readedBytes=0;
    maxNoDataTime=5 #[s]
    readStartTime=time.time()
    lastDataTime=time.time()
    RxThreadRunning=1
    semaphoreStartSynchro.release()
    while ((readedBytes != inputSize) and ((time.time() - lastDataTime) < maxNoDataTime)):
        data = portHandle.read(256);
        if len(data) > 0:
            outFile.write(data)
            readedBytes+=len(data)
            lastDataTime=time.time()
            sys.stdout.write("\rReaded %d/%dB." % (readedBytes,inputSize))
            sys.stdout.flush()
        else:
            print "\nNo data time",(time.time() - lastDataTime),"s."
    outFile.close()
    print "\nWhole read transfer time:",(time.time()-readStartTime),"s."
    RxThreadRunning=0

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
        try:
            portHandle.write(line)
        except portHandle.SerialTimeoutException as e:
            print "Write Timeout!"
            break;
        if (RxThreadRunning == 0):
            break;


    # Wait on reading thread and close port
    tRead.join()
    print "Port ",args.device," closed."
    portHandle.close()

# Call main
main()
