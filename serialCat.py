#!/usr/bin/python2.7
import argparse, os, sys
import threading
import time
import serial
import math
import hashlib

# Program result return at then end of main
result=0

parser = argparse.ArgumentParser()
# File options
parser.add_argument("-i", "--inputFile", type=str, required=False, help="Input file to sent")
parser.add_argument("-o", "--outputFile", type=str, required=False, help="Output file where received data is stored")
parser.add_argument("-a", "--appendOutputFile", action='store_true', required=False, help="Append output file instead of create and write")
# Serial communication options
parser.add_argument("-d", "--device", type=str, required=True, help="Path of tty device")
parser.add_argument("-B", "--baudrate", type=int, required=False, help="Int value of baudrate")
parser.add_argument("-P", "--parity", type=str, required=False, help="Parity <none | even | odd>")
parser.add_argument("-F", "--flowcontrol", type=str, required=False, help="Flowcontrol <none | rtscts >")
# General communication options
parser.add_argument("-f", "--frameSize", type=int, required=False, help="Size of transmited frame")
parser.add_argument("-fd", "--frameDelay", type=float, required=False, help="Delay of transmited frame in seconds (float)")
parser.add_argument("-rd", "--receiveDelay", type=float, required=False, help="Extra receive delay of transmited frame in seconds (float)")
parser.add_argument("-t", "--transmitSize", type=int, required=False, help="Size of transmitted total data")
parser.add_argument("-r", "--receiveSize", type=int, required=False, help="Size of received total data")
# Extra options
parser.add_argument("-c", "--check", action='store_true', required=False, help="Checks if input file is equal to output file.")
parser.add_argument("-g", "--graph", action='store_true', required=False, help="Transfer graph plot")
parser.add_argument("-p", "--preview", action='store_true', required=False, help="Preview data")
parser.add_argument("-pdp", "--processDataPath", type=str, required=False, help="Path to module called ProcessData.py")
args = parser.parse_args()

#Assert
if (not args.device):
    print "No device"
    sys.exit(1)

# Add the directory and module
if (args.processDataPath is not None):
    sys.path.append(os.path.abspath(args.processDataPath))
    from ProcessData import processData

#Config check
defaultBaudrate=115200
if (args.baudrate is not None):
    defaultBaudrate=args.baudrate

#Config check
defaultParity=serial.PARITY_EVEN
if (args.parity is not None):
    if args.parity == "even":
        defaultParity=serial.PARITY_EVEN
    elif args.parity == "odd":
        defaultParity=serial.PARITY_ODD
    else:
        defaultParity=serial.PARITY_NONE

#Config check
confRtsCts=True
if (args.flowcontrol is not None):
    if args.flowcontrol == "rtscts":
        confRtsCts=True
    else:
        confRtsCts=False

#Config check
defaultFrameSize=1024
if (args.frameSize is not None):
    defaultFrameSize=args.frameSize

#Config check
if (args.graph):
    import matplotlib.pyplot as plt
    plot_time = []
    plot_RxData = []
    plot_TxData = []

# Read input file size
inputSize=0
if (args.inputFile is not None):
    inputSize = os.stat(args.inputFile).st_size
if (args.transmitSize is not None):
    inputSize=args.transmitSize

#Config check
if (not args.receiveSize is not None):
    receiveSize=inputSize
else:
    receiveSize=args.receiveSize

semaphoreStartSynchro = threading.Semaphore()

# Serial port read
portHandle = serial.Serial(
    port=args.device,
    baudrate=defaultBaudrate,
    rtscts=confRtsCts,
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

# MD5 of file ( only path given as argument )
def FileMD5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Reading thread
def read():
    global result
    global RxThreadRunning
    global TxTransmitted
    global receiveSize

    #Declare globals for plot
    if (args.graph):
        global plot_time
        global plot_RxData
        global plot_TxData

    # If output file not defined then release semaphore and return
    if (args.outputFile is None):
        semaphoreStartSynchro.release()
        return

    # Open output file to append or write clear
    print "Output to ",args.outputFile,"."
    if (args.appendOutputFile):
        outFile = open(args.outputFile,'a+')
    else:
        outFile = open(args.outputFile,'w')

    readedBytes=0;
    maxNoDataTime=5 #[s]
    lastDataTime=readStartTime=time.time()
    RxThreadRunning=1
    semaphoreStartSynchro.release()
    while ( (args.receiveDelay is None) and ((readedBytes < receiveSize) and ((time.time() - lastDataTime) < maxNoDataTime)) or
           (args.receiveDelay is not None) and ((time.time() - lastDataTime) < args.receiveDelay)):
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
            readedBytes+=len(data)
            lastDataTime=time.time()
            # Added possiblity to process data before write to file
            if (args.processDataPath is not None):
                data = processData(data)
            outFile.write(data)
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
    global result
    global RxThreadRunning
    global TxTransmitted
    # Read thread creation
    semaphoreStartSynchro.acquire()
    tRead = threading.Thread(target=read, args=())
    tRead.start()

    # Wait on start synchronization semaphore
    semaphoreStartSynchro.acquire()

    # If input file defined
    if (args.inputFile is not None):
        # Open write file and send lines
        print "Input from ",args.inputFile,"(",inputSize,"Bytes)."
        inFile = open(args.inputFile,'r')
        for chunk in iter(lambda: inFile.read(min(defaultFrameSize,inputSize-TxTransmitted)), ''):
            writeSize       = portHandle.write(chunk)
            TxTransmitted   += writeSize
            # Transmitted data preview if set
            if (args.preview):
                sys.stdout.write("Tx:%s\n" % (chunk))
            # Wait frame delay if set
            if (args.frameDelay is not None):
                time.sleep(args.frameDelay)
            if (RxThreadRunning == 0):
                break;
        time.sleep(0.005)


    # Wait on reading thread and close port
    tRead.join()
    print "Port ",args.device," closed."
    portHandle.close()

    # Check files md5 sums if enabled
    if ((args.check) and (args.inputFile is not None) and (args.outputFile is not None)):
        sumInput=FileMD5(args.inputFile)
        sumOutput=FileMD5(args.outputFile)
        sys.stdout.write("Input file MD5 %s\n" % sumInput)
        sys.stdout.write("Output file MD5 %s\n" % sumOutput)
        if (sumInput != sumOutput):
            sys.stdout.write("Checksum error!\n")
            result=-1

    #Plot graph if needed
    if (args.graph):
        plt.plot(plot_time,plot_TxData,label="Tx")
        plt.plot(plot_time,plot_RxData,label="Rx")
        plt.title("Transmission graph (Bytes/Time)")
        plt.xlabel("Time [s]")
        plt.ylabel("Data sent/received [B]")
        plt.legend(loc="upper left")
        plt.grid(True)
        plt.show()

# Call main
main()
sys.exit(result)
