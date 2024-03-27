# Filename: CSC223f23CSVpre1.py
# ************************************************************
# Author:     D. Parson
# Student coauthor: None
# Major:      CS&IT professor
# Creation Date: 7/25/2023
# Due Date: This is handout code not a STUDENT part of the assignment.
# Course:     CSC223 Fall 2023
# Professor Name: D. Parson
# Assignment: #1
# Input: First command line arg is a pseudo-random number seed, mandatory.
# Input: 2nd, optional command line arg for output file name,
#       default to CSC223f23CSVpre1.csv
# Output: Named file per Input with a single column of statistical data.
# This script outputs using file low-level writing to write a CSV
# (Command Separated Value data file) with a single *uniform* statistical
# distribution from Python modules random and / or numpy.random.Generator.
# Student updates to CSC223f23CSVstudent1.py will use the Python csv module
# for I/O and also generate data for other distributions.
# ************************************************************

import sys          # Used for argv command line arguments
import random       # For its statistical distribution generators.
import numpy as np  # For its statistical distribution generators.
from statistics import mean, median, mode, pstdev
# ^^^ multimode not available in earlier libraries, mode throws a
# StatisticsError on multiple modes; pstdev is *population* standard deviation.
from histogram import plotHistogram # initial testing, not used in production.

def generateDistributionTable(seed, statsfilename, numberOfRows=1024):
    '''
    Generate a table of pseudo-random statistical distributions,
    one per column, with the actual distributions hard coded into
    generateDistributionTable. Currently it generates random.uniform
    in column 0 and numpy.random.Generator.uniform in column 1,
    in the range [0, 100] for random.uniform and [0, 100) for
    numpy.random.Generator.uniform.
    Input seed is the pseudo-random seed value for the generators.
    Input statsfilename is the name of a text file for reporting
    statistics count, min, max, mean, median, mode, and pstdev to 2 places.
    Input numberOfRows is the number of rows of output data, i.e.,
    number of values from each generator, defaulting to 1024.
    Output return value is the resulting table consisting of an outer list
    of rows, where each row is one sample from each distribution generator.
    '''
    def getstats(dataname, datalist, statsfilehndl):
        '''
        Helper function to format and write stats for multiple data lists.
        dataname is name of generator, datalist is the list of numeric
        data, and statsfilehndl is the open file handle for sys.write.
        '''
        minstr = str(round(min(datalist),2))
        maxstr = str(round(max(datalist),2))
        meanstr = str(round(mean(datalist),2))
        medianstr = str(round(median(datalist),2))
        try:
            modestr = str(round(mode(datalist),2))
        except StatisticsError as oops:
            modestr = 'None'
        pstdevstr = str(round(pstdev(datalist),2))
        countstr = str(len(datalist))
        statsfilehndl.write(dataname + ' statistics:\n')
        statsfilehndl.write('    count = ' + countstr + '\n')
        statsfilehndl.write('    min = ' + minstr + '\n')
        statsfilehndl.write('    max = ' + maxstr + '\n')
        statsfilehndl.write('    mean = ' + meanstr + '\n')
        statsfilehndl.write('    median = ' + medianstr + '\n')
        statsfilehndl.write('    mode = ' + modestr + '\n')
        statsfilehndl.write('    pstdev = ' + pstdevstr + '\n')
    statsfileh = open(statsfilename, 'w')
    generatorA = random.Random(seed)    # constructs a Random generator object
    # https://docs.python.org/3.7/library/random.html
    generatorB = np.random.default_rng(seed=seed) # factory for Generator
    # https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.Generator
    # generatorB.uniform allows you to get the entire list in one call,
    # but there is no parameter for rounding. We can use the anonymous
    # function or a named function -- here the anonymous lambda expression
    # to round(value, 2) to two decimal places; I settled on int(value)
    # to discard the fraction and construct an int object for cleaner
    # visualization as a histogram of integer counts. The map() function
    # returns a generator that iterates over generatorB.uniform's returned
    # sequence of generated values; wrapping list() around the Map() call
    # converts the map generator's results to a Python list.
    listA = [int(generatorA.uniform(0, 100))
        for i in range(0,numberOfRows)]
    getstats('RndUniform, seed = ' + str(seed),
        listA, statsfileh)
    # Above LIST COMPREHENSION IS EQUIVALENT TO THIS for loop:
    # listA = []
    # for i in range(0,numberOfRows):
    #   listA.append(int(generatorA.uniform(0, 100)))
    listB = list(map(lambda value : int(value),
        generatorB.uniform(0, 100, numberOfRows)))
    # print('DEBUG listA', listA[0:10])
    # print('DEBUG listB', listB[0:10])
    getstats('NPUniform, seed = ' + str(seed),
        listB, statsfileh)
    statsfileh.close()
    result = list(zip(listA, listB))    # zip also returns a generator
    result.insert(0, ('RndUniform', 'NPUniform')) # headings for the columns
    # print('DEBUG table', result[0:10])
    return result

__usage__ = 'USAGE: python CSC223f23CSVpre1.py SEED [ OUTFILE.csv ]'
# Symbol names with __underline__ should be private to their context.
if __name__ == '__main__':      # Entry code outside of any function.
    if len(sys.argv) < 2 or len(sys.argv) > 3: # argv[0] is CSC223f23CSVpre1.py
        raise ValueError(__usage__)
        # https://docs.python.org/3.7/library/exceptions.html
    try:
        seed = int(sys.argv[1])
    except ValueError as badint:
        raise ValueError('Invalid, non-integer SEED on command line: '
            + sys.argv[1] + '\n' + __usage__)
    if len(sys.argv) == 3:
        outcsvname = sys.argv[2]
        if not outcsvname.endswith('.csv'):
            raise ValueError('ERROR, OUTFILE must end in ".csv: "'
                + sys.argv[2] + '\n' + __usage__)
    else:
        outcsvname = 'CSC223f23CSVpre1.csv'
    outcsvfile = open(outcsvname, 'w')
    statsfilename = outcsvname.replace('.csv', '.txt')
    table = generateDistributionTable(seed, statsfilename, 100000)
    # START OF WHAT PYTHON'S CSV MODULE WILL MAKE SIMPLER.
    for row in table:
        for cell in row[0:len(row)-1]: # Append ',' to all but the last col.
            outcsvfile.write(str(cell) + ',')   # Must convert to string
        outcsvfile.write(str(row[-1]) + '\n')   # [-1] is last element
    outcsvfile.close()  # always do this to ensure final writes get flushed
    # Do following in makegraphs.sh, done here for initial testing only.
    # for colname in table[0]:
        # plotHistogram(outcsvname, colname, outcsvname.replace('.csv','.png'), who='Whoever')
    sys.exit(0)         # 0 means NO ERROR in Unix & related environments
