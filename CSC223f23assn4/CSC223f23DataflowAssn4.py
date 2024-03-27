# Filename: CSC223f23DataflowAssn4.py
# ************************************************************
# Author:     Dr. Parson
# Student coauthor: Ryan Livinghouse
# Major:      CS&IT professor
# Creation Date: 11/20/2023
# Due Date: Sunday 12/10/2023
# Must be in before I go over the solution Tuesday, Dec. 12, 2023 2-4 p.m.,
#   else 0%.
# Course:     CSC223 Fall 2023
# Professor Name: D. Parson
# Assignment: #4
# Input: First command line arg is a pseudo-random number seed, mandatory.
# Input: 2nd, mandatory command line arg for output CSV file name.
# Output: Named file per Input with an 10-column CSV output file, heading:
#
#   Distribution, Param1, Param2, Count, Mean, Median, Mode, Pstdev, Min, Max
#
#   Count is an int and Mean, Median, Mode, Pstdev must be rounded
#       to 6 places.
#
#   Distribution is one of 'uniform', 'normal', or 'exponential'.
#   Param1 is Low for uniform, Loc (mean) for normal,
#       scale (halfway point in distribution) for exponential.
#   Param2 is high for uniform, scale (standard deviation) for normal,
#       None (not used) for exponential.
#   Count is size for uniform, normal, and exponential.
#   Mean is stats.mean for the generated data in that distribution.
#       (sum of values / number of values).
#   Median is stats.median for the generated data in that distribution.
#       (central value in the distribution)
#   Mode is stats.mode for the generated data in that distribution.
#       (most frequently occurring value)
#       If stats.mode throws stats.StatisticsError, set this value to None.
#       Some library versions throw stats.StatisticsError when there is
#       no unqiue mode (most frequent value).
#   Pstdev is stats.pstdev, population standard deviation.
#       help(stats.pstdev)
#       Help on function pstdev in module statistics:
#       pstdev(data, mu=None)
#           Return the square root of the population variance.
#           See ``pvariance`` for arguments and other details.
#   Min and Max are the built-in Python min() and max() results.
# https://numpy.org/doc/stable/reference/random/generator.html
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.uniform.html
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.normal.html
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.exponential.html
# ************************************************************

import sys          # Used for argv command line arguments
import statistics as stats # (mean, median, mode, pstdev).
# ^^^ multimode not available in earlier libraries, mode throws a
# StatisticsError on multiple modes; pstdev is *population* standard deviation.
#   min() and max() are builtins
import numpy as np  # numpy.random.default_rng(seed=?) for distributions.
import csv

# DR. PARSON SUPPLIES makeUniform closure to bind generator parameters.
# STUDENTS must do the same for makeNormal and makeExponential.
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.uniform.html
def makeUniform(Low, high, size, seed):
    mygenerator =  np.random.default_rng(seed=seed)
    def returnUniform():
        return(('uniform', Low, high, size,
            mygenerator.uniform(Low, high, size)))
        # returns a 5-tuple with the name of the distribution
        # ('uniform', 'normal', or 'exponential'), the Param1, Param2,
        # and Count of the distribution, and a Count-size
        # np.ndarray of float values.
    return returnUniform

# STUDENT 1: 20% Write makeNormal(Loc, scale, size, seed)
#   similar to makeUniform, that returns a closure-function
#   that returns a 5-tuple per the specification comments at the
#   top of this file and the example of makeUniform.
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.normal.html
def makeNormal(Loc, scale, size, seed):
    mygenerator = np.random.default_rng(seed=seed)
    def returnNormal():
        return ('normal', Loc, scale, size,
                mygenerator.normal(Loc, scale, size))
    return returnNormal

#    pass    # Your code goes here.

# STUDENT 2: 20% Write makeExponential(scale, size, seed)
#   similar to makeUniform, that returns a closure-function
#   that returns a 5-tuple per the specification comments at the
#   top of this file and the example of makeUniform. Field [2] in
#   the returned 5-tuple is None becausr Param2 is not used by exponential.
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.exponential.html
def makeExponential(scale, size, seed):
    mygenerator = np.random.default_rng(seed=seed)
    def returnExponential():
        return ('exponential', scale, None, size,
                mygenerator.exponential(scale, size))
    return returnExponential

#    pass    # Your code goes here.

# STUDENT 3: 20% Write generator generateDistribution() with these parameters
# that YIELDS the return value from calling distributionClosure with no
# arguments, doing that howManyTimesToYield times in a loop,
# then YIELDS None as sentinel value, then falls out the bottom
# (default return with no "return" statement is also None).
# See genASCII in DataflowGeneratorsOnePath.py for an example
# of yielding values.
# The yield of sentinel value None at the end is new for this assignment.
def generateDistribution(distributionClosure, howManyTimesToYield):
    for _ in range(howManyTimesToYield):
        yield distributionClosure()
    yield None

#    pass    # Your code goes here.

# STUDENT 4: 20% Write generator generateStatisticalAnalysis that iterates
# over its predecessor generator until the predecessor YIELDS None as a
# sentinel value. Otherwise, create and YIELD a 10-tuple that consists
# of the first 4 fields of the incoming 5-tuple from the predecessor
# (Distribution, Param1, Param2, Count, ndarray), followed by the mean,
# median, mode, pstdev, min, & max of the incoming ndarray,
#   called from the stats module (min & max are builtins). YIELDS the 10-tuple:
# (Distribution, Param1, Param2, Count, Mean, Median, Mode, Pstdev, Min, Max)
# To compute mode do this:
#       try:
#           mode = round(stats.mode(tuple5[4]),6)
#       except stats.StatisticsError:
#           mode = None
# because stats.mode() raises StatisticsError when there is no unique mode.
# When predecessor YIELDS a value of None, break out of your loop,
# YIELD None (as a sentinel value), and fall out the bottom.
# ROUND each of the Mean through Max values to 0 places, e.g. round(value,0)
# We are doing that to try to get a mode value.
# See genASCII2Count in DataflowGeneratorsOnePath.py for an example
# of iterating over a predecessor generator and yielding values.
# The yield of sentinel value None at the end is new for this assignment.
def generateStatisticalAnalysis(predecessor):
    for data in predecessor:
        if data is None:
            yield None
            break
        
        distribution, param1, param2, count, ndarray = data  # Unpack the tuple
        
        # compute now
        mean = round(stats.mean(ndarray), 0)
        median = round(stats.median(ndarray), 0)
        
        try:
            mode_result = stats.mode(ndarray)
            mode = round(mode_result.mode[0], 0)
        except (stats.StatisticsError, AttributeError):
            mode = None  # quick error check
        
        pstdev = round(stats.pstdev(ndarray), 0)
        min_val = round(min(ndarray), 0)
        max_val = round(max(ndarray), 0)
        
        yield (distribution, param1, param2, count, mean, median, mode, pstdev, min_val, max_val)

    # Distribution, Param1, Param2, Count, Mean, Median, Mode, Pstdev, Min, Max
    # Distribution, Param1, Param2, Count come in from predecessor.
    # See DataflowGeneratorsOnePath.py's genASCII2Count
#    pass    # Your code goes here.

# STUDENT 5: 20% Write saveStatisticalAnalysisCSV that tests
# if writeHeader, and if "if writeHeader" succeeds, calls csvWriter.writerow
# with a CSV header row containing the following strings
# ['Distribution', 'Param1', 'Param2', 'Count', 'Mean', 'Median', 'Mode',
#   'Pstdev', 'Min', 'Max']
# Then, iterate over its predecessor and writerow the incoming 10-tuple
#   to csvWriter and then YIELD that 10-tuple. HOWEVER, when the incoming
#   value from predecessor is None, YIELD None (as a sentinel value),
#   and fall out the bottom.
# See sinkOutput2File in DataflowGeneratorsOnePath.py for an example
# of iterating over a predecessor generator and writing and yielding values.
# The yield of sentinel value None at the end is new for this assignment.
def saveStatisticalAnalysisCSV(predecessor, csvWriter, writeHeader):
    if writeHeader:
        header = ['Distribution', 'Param1', 'Param2', 'Count', 'Mean', 'Median', 'Mode', 'Pstdev', 'Min', 'Max']
        csvWriter.writerow(header)
    for data in predecessor:
        if data is None:
            yield None
            break
        csvWriter.writerow(data)
        yield data

#    pass    # Your code goes here.

__usage__ =                 \
    'USAGE: python CSC223f23DataflowAssn4.py SEED OUTFILE.csv'
# Symbol names with __underline__ should be private to their context.
if __name__ == '__main__':      # Entry code outside of any function.
    if len(sys.argv) != 3:
        # argv[0] is CSC223f23DataflowAssn4.py
        raise ValueError(__usage__)
        # https://docs.python.org/3.7/library/exceptions.html
    try:
        seed = int(sys.argv[1])
    except ValueError as badint:
        raise ValueError('Invalid, non-integer SEED on command line: '
            + sys.argv[1] + '\n' + __usage__)
    outcsvname = sys.argv[2]
    if not outcsvname.endswith('.csv'):
        raise ValueError('ERROR, OUTFILE must end in ".csv: "'
                + sys.argv[2] + '\n' + __usage__)
    outfile = open(outcsvname, 'w', newline='')
    outcsv = csv.writer(outfile)
    writeCSVheader = True
    howManyTimesToYield = 10
    howManyTimesYielded = 0
    samplesPerDistribution = 10000
    for distributor in (makeUniform(0, 100, samplesPerDistribution, seed),
            makeNormal(50, 15, samplesPerDistribution, seed+1),
            makeExponential(10, samplesPerDistribution, seed+17)):
        howManyTimesYielded += 1
        if howManyTimesYielded > howManyTimesToYield:
            raise RuntimeError('ERROR, Missing "yield None" as a '
                + 'sentinel value in the pipeline?')
        # Create and run 3 distinct PULL pipelines.
        stage1 = generateDistribution(distributor, howManyTimesToYield)
        stage2 = generateStatisticalAnalysis(stage1)
        stage3 = saveStatisticalAnalysisCSV(stage2, outcsv, writeCSVheader)
        writeCSVheader = False
        for generatedValue in stage3:
            if generatedValue == None:  # sentinel value, next distributor
                break   # out of inner for loop
    outfile.close()

