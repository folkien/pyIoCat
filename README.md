# pyIoCat
This script takes serial port device, input file and output file as an arguments and then sent input file content to serial port and reads simultanously (Amount of bytes equal to input file size) to output file. If everything is readen or 5s of no data happend then script closes port and exits.

```shell
usage: serialCat.py [-h] -i INPUTFILE -o OUTPUTFILE -d DEVICE [-B BAUDRATE]
                    [-P PARITY] [-f FRAMESIZE] [-fd FRAMEDELAY]
                    [-rd RECEIVEDELAY] [-t TRANSMITSIZE] [-r RECEIVESIZE] [-g]
                    [-p]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        input file
  -o OUTPUTFILE, --outputFile OUTPUTFILE
                        output file
  -d DEVICE, --device DEVICE
                        tty Device
  -B BAUDRATE, --baudrate BAUDRATE
  -P PARITY, --parity PARITY
  -f FRAMESIZE, --frameSize FRAMESIZE
                        Size of transmited frame
  -fd FRAMEDELAY, --frameDelay FRAMEDELAY
                        Delay of transmited frame in seconds (float)
  -rd RECEIVEDELAY, --receiveDelay RECEIVEDELAY
                        Extra receive delay of transmited frame in seconds
                        (float)
  -t TRANSMITSIZE, --transmitSize TRANSMITSIZE
                        Size of transmitted total data
  -r RECEIVESIZE, --receiveSize RECEIVESIZE
                        Size of received total data
  -g, --graph           Transfer graph plot
  -p, --preview         Preview data
```
