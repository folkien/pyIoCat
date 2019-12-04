# ProcessData example file which can be given as an argument of serialCat to process data before file save.
import sys

#define function to process data
def processData(inputData):
    sys.stdout.write("Chunk %s." % (inputData))
    return "0"
