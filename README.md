# pyIoCat
This script takes serial port device, input file and output file as an arguments and then sent input file content to serial port and reads simultanously (Amount of bytes equal to input file size) to output file. If everything is readen or 5s of no data happend then script closes port and exits.

```shell
usage: serialCat [-h] [-i INPUTFILE] [-o OUTPUTFILE] [-a] -d DEVICE
                 [-B BAUDRATE] [-P PARITY] [-F FLOWCONTROL] [-f FRAMESIZE]
                 [-fd FRAMEDELAY] [-rd RECEIVEDELAY] [-t TRANSMITSIZE]
                 [-r RECEIVESIZE] [-c] [-g] [-p] [-pdp PROCESSDATAPATH]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        Input file to sent
  -o OUTPUTFILE, --outputFile OUTPUTFILE
                        Output file where received data is stored
  -a, --appendOutputFile
                        Append output file instead of create and write
  -d DEVICE, --device DEVICE
                        Path of tty device
  -B BAUDRATE, --baudrate BAUDRATE
                        Int value of baudrate
  -P PARITY, --parity PARITY
                        Parity <none | even | odd>
  -F FLOWCONTROL, --flowcontrol FLOWCONTROL
                        Flowcontrol <none | rtscts >
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
  -c, --check           Checks if input file is equal to output file.
  -g, --graph           Transfer graph plot
  -p, --preview         Preview data
  -pdp PROCESSDATAPATH, --processDataPath PROCESSDATAPATH
                        Path to module called ProcessData.py
```

# Examples

Transfer file `a.txt` and receive identicall amount of bytes to file `b.txt` through `/dev/ttyACM0`.

```shell
serialCat -d /dev/ttyACM0 -i a.txt  -o b.txt
```

Do this same but also compare output and input MD5 sums and throw -1 exit code if diffrent.

```shell
serialCat -d /dev/ttyACM0 -i a.txt  -o b.txt -c
```

Transfer only `a.txt` file in parts max 100 bytes with in between time delay 100ms

```shell
serialCat -d /dev/ttyACM0 -i a.txt -f 100 -fd 0.1
```

Read only 10000 Bytes from serial port to file and plot speed graph.

```shell
serialCat -d /dev/ttyACM0 -o b.txt -r 10000 -g
```

