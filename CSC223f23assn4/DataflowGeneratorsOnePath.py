# DataflowGeneratorsOnePath.py D. Parson Fall 2023
# demonstrate a non-preemptive dataflow using Python generators.
# Compare to DataflowGeneratorsDAG.py that uses coroutines
# in support of diverging & converging forks in the dataflow DAG.
import sys
import string   # to get character types
# https://docs.python.org/3/library/string.html
import random
import tempfile
# https://docs.python.org/3/library/tempfile.html
import time
from functools import reduce
# https://docs.python.org/3.0/library/functools.html

def genASCII(ID, maxStringLength, stringsPerPacket,
        totalCountOfDataPackets, TraceFile, seed=220223523):
    '''
    generate totalCountOfDataPackets of strings from length 1 to
    maxStringLength, create a temporary file for each packet
    containing stringsPerPacket strings, one per line, and yield
    the handle to the temporary file which the receiver must close.
    There will be totalCountOfDataPackets files created. This
    is inefficient and is being used for demo purposes.

    ID is a unique int per generator to aid debugging.

    TraceFile is an open file handle for writing debug information.
    '''
    rgen = random.Random(seed)
    universe = string.ascii_letters + string.digits + string.punctuation    \
        + '     ' # allow for multiple spaces and tabs between words.
    # https://docs.python.org/3/library/string.html
    # universe does not include tabs, newlines, carriage returns, form feeds
    for packet in range(0, totalCountOfDataPackets):
        tmpfile = tempfile.TemporaryFile(mode='w+', newline='',
            dir='.', suffix='.tmp') # useful for debugging
        # w+ makes it writable, and readable further down in the dataflow
        # https://docs.python.org/3/library/tempfile.html#tempfile-examples
        for scount in range(0, stringsPerPacket):
            slen = rgen.randint(1,maxStringLength)
            s = ''
            for sstep in range(0,slen):
                s += universe[rgen.randint(0,len(universe)-1)]
            TraceFile.write('DEBUG s: ' + str(s) + '\n')
            tmpfile.write(s + '\n')
        tmpfile.flush()
        # tmpfile.seek(0) # read pointer at start for next dataflow stage
        # ^^^ NO! When there is > 1 receiver, they need to do the seek(0)!
        yield(tmpfile)

def genASCII2Count(ID, predecessor, charFilter, TraceFile):
    '''
    predecessor is a genASCII generator in this demo. genASCII2Count
    needs access to read generator data incrementally using data PULL
    on the pipeline. charFilter is a Python filter function used to
    pass only certain characters.
    genASCII2Count's yield returns a 3-tuple:
        (linecount, wordcount, charcount)
    as in the Unix "wc" utility. The counts are after applying charFilter.

    ID is a unique int per generator to aid debugging.

    TraceFile is an open file handle for writing debug information.
    '''
    for f in predecessor:
        f.seek(0)
        lines = []
        for line in f.readlines():
            line = line.strip()
            if line:        # Not Blank.
                l = ''.join(filter(charFilter, line))
                # filter returns a sequence of single chars,
                # and ''.join joins them into a string
                if l:   # filter may have created an empty string
                    lines.append(l)
                    TraceFile.write('DEBUG genASCII2Count: ' + str(l) + '\n')
        linecount = len(lines)
        wordcount = 0
        charcount = 0
        for l in lines:
            charcount += len(l)
            words = l.split(' ')
            for w in words:
                if w:   # don't count empty strings which are adjacent spaces
                    wordcount += 1
        yield ((linecount, wordcount, charcount))

def sinkOutput2File(ID, predecessor, outputFileHandle):
    '''
    predecessor is a genASCII2Count generator in this demo. genASCII2Count
    needs access to read generator data incrementally using data PULL
    on the pipeline.
    sinkOutput2File writes output from predecessor into outputFileHandle
        and also yields it, both after converting to str().
    sinkOutput2File does not close outputFileHandle at the end.

    ID is a unique int per generator to aid debugging.

    TraceFile is an open file handle for writing debug information.
    '''
    for data in predecessor:
        mydata = str(data)
        outputFileHandle.write(mydata + '\n')
        yield(mydata)

if __name__ == '__main__':
    tracefile = open(sys.argv[1], 'w', newline='')
    gen1 = genASCII(1, 15, 10, 5, tracefile)
    gen2 = genASCII2Count(2, gen1,lambda x : True, tracefile) # no filtering
    gen3 = sinkOutput2File(3, gen2, tracefile)
    for ignore in gen3:
        # This is a PULL pipeline.
        # Each generator pulls data from its predecessor.
        # tracefile.write(str(t) + '\n')
        pass    # gen3 writes to the output file.
    tracefile.close()
