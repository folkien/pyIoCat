# pyIoCat
This script takes serial port device, input file and output file as an arguments and then sent input file content to serial port and reads simultanously (Amount of bytes equal to input file size) to output file. If everything is readen or 5s of no data happend then script closes port and exits.

```shell
 usage: serialCat [-h] -i INPUTFILE -o OUTPUTFILE -d DEVICE [-B BAUDRATE]
                 [-P PARITY]

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
```
