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
parser.add_argument("-f", "--frameSize", type=int, required=False, help="Size of transmited frame")
parser.add_argument("-t", "--transmitSize", type=int, required=False, help="Size of transmitted total data")
parser.add_argument("-r", "--receiveSize", type=int, required=False, help="Size of received total data")
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
if (not args.frameSize):
    defaultFrameSize=1024
else:
    defaultFrameSize=args.frameSize

#Config check
if (args.graph):
    import matplotlib.pyplot as plt
    plot_time = []
    plot_RxData = []
    plot_TxData = []

# Read input file size
inputSize = os.stat(args.inputFile).st_size
if (args.transmitSize):
    inputSize=args.transmitSize

#Config check
if (not args.receiveSize):
    receiveSize=inputSize
else:
    receiveSize=args.receiveSize

semaphoreStartSynchro = threading.Semaphore()

# Serial port read
portHandle = serial.Serial(
    port=args.device,
    baudrate=defaultBaudrate,
    rtscts=True,
    parity=defaultParity,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
    write_timeout=10
)
if portHandle.isOpen():
    portHandle.close()
portHandle.open()
print "Port ",args.device," opened."

# Variable with state of Rx Thread
RxThreadRunning=0
TxTransmitted=0

# Reading thread
def read():
    global RxThreadRunning
    global TxTransmitted
    global receiveSize
    #Declare globals for plot
    if (args.graph):
        global plot_time
        global plot_RxData
        global plot_TxData
    print "Output to ",args.outputFile,"."
    outFile = open(args.outputFile,'w')
    readedBytes=0;
    maxNoDataTime=5 #[s]
    readStartTime=time.time()
    lastDataTime=time.time()
    RxThreadRunning=1
    semaphoreStartSynchro.release()
    while ((readedBytes < receiveSize) and ((time.time() - lastDataTime) < maxNoDataTime)):
        data = portHandle.read(256);
        # Store data for graphical plot.
        if (args.graph):
            timeStamp=time.time()
            plot_time.append(timeStamp)
            plot_RxData.append(readedBytes)
            plot_TxData.append(TxTransmitted)
        # Print Delta only when RxSize is not specified
        if (inputSize == receiveSize):
            sys.stdout.write("\rTransmitted %d/%dB. Readed %d/%dB. Delta = %dB.  " % (TxTransmitted,inputSize,readedBytes,receiveSize,TxTransmitted-readedBytes))
        else:
            sys.stdout.write("\rTransmitted %d/%dB. Readed %d/%dB." % (TxTransmitted,inputSize,readedBytes,receiveSize))
        sys.stdout.flush()
        if len(data) > 0:
            outFile.write(data)
            readedBytes+=len(data)
            lastDataTime=time.time()
        else:
            print "\nNo data time",(time.time() - lastDataTime),"s."

    stopTime=time.time()
    durationTime=stopTime-readStartTime
    outFile.close()
    # Print Delta only when RxSize is not specified
    if (inputSize == receiveSize):
        sys.stdout.write("\rTransmitted %d/%dB. Readed %d/%dB. Delta = %dB.  " % (TxTransmitted,inputSize,readedBytes,receiveSize,TxTransmitted-readedBytes))
    else:
        sys.stdout.write("\rTransmitted %d/%dB. Readed %d/%dB." % (TxTransmitted,inputSize,readedBytes,receiveSize))
    # Print minutes if time > 60s.
    if (durationTime>60):
        print "\nWhole read transfer time:",str(round(durationTime/60,0)),"m ",str(round(math.fmod(durationTime,60),2)),"s."
    else:
        print "\nWhole read transfer time:",str(round(durationTime,2)),"s."
    print "Transfer speed:",str(round((readedBytes/durationTime)/1024,2)),"kB/s."
    print "Baudrate theoreticaly transfer speed:",str(round((defaultBaudrate/11)/1024, 2)),"kB/s."
    RxThreadRunning=0

# Writing thread
def main():
    global RxThreadRunning
    global TxTransmitted
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
    for chunk in iter(lambda: inFile.read(defaultFrameSize), ''):
        writeSize       = portHandle.write(chunk)
        TxTransmitted   += writeSize
        if (RxThreadRunning == 0):
            break;


    # Wait on reading thread and close port
    tRead.join()
    print "Port ",args.device," closed."
    portHandle.close()

    #Plot graph if needed
    if (args.graph):
        plt.plot(plot_time,plot_TxData,label="TxData")
        plt.plot(plot_time,plot_RxData,label="RxData")
        plt.show()

# Call main
main()
