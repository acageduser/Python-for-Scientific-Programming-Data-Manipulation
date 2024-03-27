# CSC223f23DeriveAssn3.py D. Parson, Fall 2023
# Filename: CSC223f23DeriveAssn3.py
# ************************************************************
# Author:     D. Parson
# Student coauthor: Ryan Livinghouse
# Major: Information Technology     
# Creation Date: 10/31/2023
# Due Date:      Thursday 11/20/2023
# Course:     CSC223 Fall 2023
# Professor Name: D. Parson
# Assignment: #3
'''
STUDENT 1: Tested WORKING with the following commandline: python .\CSC223f23DeriveAssn3.py RT_month_10.csv HMtempC_mean WindSpd_mean wnd_WNW_NW "-exp.5" "-avg5" "-delta1"

Description:
STUDENT 2: VisitorClass Implementation
In this section, the task was to implement the VisitorClass. The class is designed to calculate the 
moving average of a data series. It involves writing a constructor that takes a string parameter, 
converts it to an integer, and uses it to maintain a history of the last 'N' data points. The visit 
method, a key part of the class, adds each new data point to this history and calculates the average 
of these points.

STUDENT 3: Delta Closure Implementation
For this section, the task was to complete the definition of the delta function. This function creates 
a closure that computes the difference between a current value and a previous value 'N' steps back in a 
sequence. This involves setting up an outer function to initialize and store the value of 'N' and creating 
a nested function, deltaClosure, that calculates the required difference. The closure maintains a history of 
data points and ensures that the length of this history aligns with 'N'. This feature is critical in 
identifying trends or changes over specified intervals in the data, enhancing the script's analytical capabilities.

STUDENT 4: File Reading and Sorting
In this section, I had to read and process data from the input CSV file. The task involved opening the 
file, reading its contents using the CSV module, and storing the data in appropriate variables (inheader 
for column headers and indataset for the data rows). I also also needed to implement sorting functionality 
based on 'year' and 'month' columns to organize the data chronologically.

STUDENT 5: Writing Output to File
This final section was for writing the processed data back to a CSV file. The task was to open the output 
file in write mode, create a CSV writer, and use it to write both the header and the processed data rows to 
the file.
'''
# STUDENT 1: 4% Complete documentation at top of CSC223f23DeriveAssn3.py.
# Fill in the blank fields in the above header and replace the
# above blank line with a 1-paragraph description of your work in this
# assignment file.
# Input: A climate -> raptor count .csv file specified as the first
#       command line argument with the target species in the first
#       characters of the file name up to _, e.g. RT_month_10.csv
#       for the test case.
#   Command line arguments are names of attributes to derive, e.g.:
#       HMtempC_mean WindSpd_mean wnd_WNW_NW for the test case.
#       These must NOT start with '-' in the name.
#   One or more of the following command line arguments:
#		-exp.N means exponential smoothing with a fractional alpha of .N
#		-avgN means average the current value and the previous N-1 cells
#		-deltaN means compute difference between previous cell N steps
#           back and the current cell
# Output: CSV file with "_Derive" appended to input file name before ".csv".
# In this student assignment:
#   "-exp" will use Dr. Parson's partial function similar to "Method 3"
#       in partialBindings.py example code.
#   "-avg" will use a Python class VisitorClass object with a
#       visit(cell) method similar to Method 1 in partialBindings.py.
#   "-deltaN" will use a Python closure similar to Method 2 in
#       partialBindings.py example code.
#   STUDENTS will complete the last 2 (VisitorClass and closure) as
#       started in the handout code below.

from functools import partial
import pprint
import sys
import csv
import statistics as stats

# Method 3 for -exp: Use a partial function to compute exponential smoothing.
def exp(alphaString):   # Returns the partial function to compute -exp.N.
    alpha = float(alphaString)
    lastvalue = None    # multiply by (1.0-alpha)
    if alpha < 0.0 or alpha > 1.0:
        raise ValueError('Invalid alpha value to exp: ' + str(alphaString))
    def smoothingCalculator(cell, alph):
        nonlocal lastvalue  # We need to update state of surrounding exp().
        result = (((alph*cell)+((1.0-alph)*lastvalue)) if (lastvalue != None)
            else cell)
        lastvalue = result
        return round(result,2)
    partialFunc = partial(smoothingCalculator, alph=alpha)
    return partialFunc  # Requires current cell only.

# Method 1 for -avg: visit() method takes row. visit() grows a list up
#   N long, where N is supplied to the constructor as a string.
# STUDENT 2: 24% Write class VisitorClass. See class in example
# partialBindings.py in this project folder to get the syntax
# of a class definition.
class VisitorClass(object):
    """
    VisitorClass calculates a moving average. It takes 'N' recent numbers and averages them.
    
        N (int): Number of items to average.
        history (list): Stores the last 'N' numbers.

        __init__(self, Nstring): Sets up the class. Converts 'Nstring' to an integer for 'N'. 
            Initializes 'history' as an empty list. If 'N' is less than 2, raises an error.
        visit(self, cell): Adds a new number ('cell') to 'history', keeps only the last 'N' items,
            then returns their average, rounded to two decimal places.
    """

    def __init__(self, Nstring):
        self.N = int(Nstring)
        if self.N < 2:
            raise ValueError('Invalid N value to avg: ' + str(Nstring))
        self.history = []

    def visit(self, cell):
        self.history.append(cell)
        while len(self.history) > self.N:
            self.history.pop(0)
        return round(stats.mean(self.history), 2)

#    pass
        # STUDENT 2: The constructor takes string parameter Nstring
        # and converts it to an int() and stores it as
        # field N inside this object. If that int N is < 2, do this:
        #   raise ValueError('Invalid N value to avg: ' + str(Nstring))
        # Then store an initially empty list in object field called  history.
    # Next define a method (a.k.a member function) called visit that
        # takes a parameter called cell.
        # append the cell argument into the object's history list.
        # Then, while the length of the history list is > N stored
        # by the constructor, run pop(0) on the history list.
        # Finally run stats.mean on the history list, round that mean
        # to 2 decimal places, and return that rounded value.
        # Handout function exp(alphaString) shows how to round.

# Method 2: Use a closure for -delta between previous cell and this one.
# STUDENT 3: 24% Complete the definition of closure-forming delta(Nstring)
# See closure function visitorClosure and nested function visit in
# partialBindings.py for the syntax including placement of return statements.
def delta(Nstring):
    """
    Creates a closure function that calculates the difference between the current value and the
    value 'N' steps back in a sequence of data.

    The function 'delta' takes a string 'Nstring', converts it to an integer 'N', and then 
    creates and returns a nested function 'deltaClosure'. If 'N' is less than 1, it raises 
    a ValueError, as a difference operation requires at least one preceding value.

    The closure 'deltaClosure' maintains a history of the last 'N' data points. When called 
    with a new data point ('cell'), it keeps the history list size up to 'N' by removing 
    the oldest entry. It then calculates the difference between the current 'cell' and the 
    oldest data point in 'history' if the list is 'N' elements long. The result is rounded 
    to two decimal places. If the history is not yet 'N' elements long, the result is set 
    to an empty string.

    This setup allows 'deltaClosure' to remember the state of 'history' between calls, 
    making it suitable for processing streams of data where you need to compare each new 
    value with one 'N' steps prior.
    """

    N = int(Nstring)
    if N < 1:
        raise ValueError('Invalid N value to delta: ' + str(Nstring))
    history = []

    def deltaClosure(cell):
        nonlocal history
        while len(history) > N:
            history.pop(0)
        result = ''
        if len(history) == N:
            result = round(cell - history[0], 2)
        else:
            result = ''
        history.append(cell)
        return result
    
    return deltaClosure

#    pass
    # In the outer function delta(Nstring):
    # convert Nstring to an int() and store it as variable N.
    # If that int N is < 1, do this:
    #   raise ValueError('Invalid N value to delta: ' + str(Nstring))
    # Set variable history to the empty list [].
    # Next, define nested function deltaClosure(cell):
    # In the nested function deltaClosure(cell)
        # 3: Declare outer variable history as nonlocal
        # Initialize variable result = ''
        # While the length of the history list is > N stored in delta(Nstring)
        #   run pop(0) on the history list.
        # If the length of the history list == N
        #       set the result to (cell - history[0]) rounded to 2 places.
        # Else
        #       set result to ''
        # append cell onto the tail end of the history list.
        # return the result
    # return deltaClosure

__usage__ =     \
'python CSC223f23DeriveAssn3.py raptor.csv attributes... -exp.N -avgN -delta'

AttributeNamesToDerive = []     # populated in __main__
AttributeColumnsToDerive = []   # initially input attr columns, later output
AttributeDerivation = {}
# AttributeDerivation maps an int in order of derivator func,
#   where func takes a (cell), to  ->
#       (func, underivedColumnForAttr)

if __name__ == '__main__':  # Called from command line
    if len(sys.argv) < 3:
        raise ValueError('Invalid command line: ' + sys.argv
            + '\n\t Usage: ' + __usage__)
    infilename = sys.argv[1]    # read file name from command line argument
    # STUDENT 4: 24% MAKE SURE TO NAME VARIABLES inheader and indataset
    # where specified because they are used further down below:
    # 4a. Open infilename in READ mode.
    # 4b. Construct a csv.reader object around this open file.
    # 4c. Assign __next__() from this csv.reader INTO VARIABLE inheader.
    # 4d. Assign all subsequent rows of data from this csv.reader into
    #     variable indataset,
    #     where each row is a list of cells returned by the csv.reader.
    #     CSC223f23WAVEassn2.py from assignment 2 uses a csv.reader.
    # 4e. Close the file opened in step 3a.
    # 4f. Find the year column by calling index('year') on inheader
    #     and find the month column by calling index('month') on inheader.
    #     There are other calls to STRING.index(SUBSTRING) below.
    # 4g. Call sort on indataset, supplying key= a function that takes
    #    a parameter called row and returns the 2-tuple
    #    (row[yearcol], row[monthcol]). The key= function returns a sort
    #    key, in this case that tuple, for sorting the list.
    # Here is an example of sort a list with a key= function:
    #   In [1]: rows = [('a', 100), ('z', 2), ('k', -50)]
    #   In [2]: rows
    #   Out[2]: [('a', 100), ('z', 2), ('k', -50)]
    #   In [3]: def getkey(row): return row[1] # return the numeric element
    #   In [4]: rows.sort(key=getkey)
    #   In [6]: rows
    #   Out[6]: [('k', -50), ('z', 2), ('a', 100)]
    # 4a, 4b, 4c, 4d
    """
    Opens the input file and reads the data using Python's CSV module.

    The data from the file is read into two main variables:
    - 'inheader': stores the first row of the CSV file, typically containing column headers.
    - 'indataset': stores all subsequent rows, where each row is a list of values corresponding to the columns.

    After reading the file, two key columns, 'year' and 'month', are identified by their positions in 'inheader'.
    These columns are crucial for sorting the dataset.

    The entire dataset ('indataset') is then sorted based on the 'year' and 'month' columns. This is done using
    Python's lambda function to specify a custom sorting key. The lambda function create    s a tuple (year, month) 
    for each row, and the dataset is sorted based on these tuples. This ensures that the data is organized in 
    chronological order.
    """

    with open(infilename, 'r') as infile:
        reader = csv.reader(infile)
        inheader = next(reader)
        indataset = list(reader)

    yearcol = inheader.index('year')
    monthcol = inheader.index('month')

    indataset.sort(key=lambda row: (row[yearcol], row[monthcol]))
    
    # No need to close the file. 'with open' is a better way to open/close it automatically. Even
    # if there is a error after opening the file but before the close line, it will close.

#    pass
    
    raptorend = sys.argv[1].index('_')
    if not inheader[-1].startswith(sys.argv[1][0:raptorend]):
        raise ValueError('Invalid non-raptor attribute name: '
            + inheader[-1] + ' in last column of file '
            + sys.argv[1])
    targetAttributeName = inheader[-1]
    targetAttributeInColumn = len(inheader) - 1
    targetValueList = []
    nextargindex = 0
    funcCount = 0
    for argindex in range(2, len(sys.argv)):
        if not sys.argv[argindex].startswith('-'):
            column = inheader.index(sys.argv[argindex]) # attribute
            if ((column != targetAttributeInColumn
                    and column != yearcol and column != monthcol)
                    and not (column in AttributeColumnsToDerive)):
                AttributeNamesToDerive.append(sys.argv[argindex])
                AttributeColumnsToDerive.append(column)
        else:
            nextargindex = argindex # derivers start here
            break
    if len(AttributeNamesToDerive) == 0:
        raise ValueError('Invalid command line, no attributes: '
            + sys.argv + '\n\t Usage: ' + __usage__)
    elif nextargindex >= len(sys.argv):
        raise ValueError('Invalid command line, no derivers: '
            + sys.argv + '\n\t Usage: ' + __usage__)

    outdataset = []
    for row in indataset:
        if len(row) != len(inheader):   # ignore \r from Windows
            continue
        try:
            targetValueList.append(float(row[-1]))  # join to data later
        except Exception as oops:
            raise ValueError('non-numeric cell ' + row[-1]
                        + ' in ' + str(row) + ', file ' + sys.argv[1])
        outrow = [int(row[yearcol]), int(row[monthcol])] # at [0] and [1]
        for column in range(0, len(row)):
            if column in AttributeColumnsToDerive:
                try:
                    cell = float(row[column])
                    outrow.append(cell)
                except Exception as oops:
                    raise ValueError('non-numeric cell ' + row[column]
                        + ' in ' + str(row) + ', file ' + sys.argv[1])
        outdataset.append(outrow)
    AttributeColumnsToDerive = [(i+2) for i in
        range(0, len(AttributeNamesToDerive))]
    # AttributeColumnsToDerive now has output data column numbers
    # after year[0] and month[1]
    outheader = ['year', 'month'] + AttributeNamesToDerive
    newcolumn = len(outheader)
    mycase = None
    for argindex in range(nextargindex, len(sys.argv)):
        if sys.argv[argindex].startswith('-exp'):
            Nstring = sys.argv[argindex][4:]  # .N string
            # func = exp(Nstring)   # Each derived attr needs its own func.
            mycase = 1
        elif sys.argv[argindex].startswith('-avg'):
            Nstring = sys.argv[argindex][4:]  # N string
            obj = VisitorClass(Nstring)
            # func = obj.visit (Must do this per each derived attr column.)
            mycase = 2
        elif sys.argv[argindex].startswith('-delta'):
            Nstring = sys.argv[argindex][6:]  # N string
            # func = delta(Nstring) (Must do this per each derived attr column.)
            mycase= 3
        else:
            raise ValueError('Invalid command line: argument '
                + sys.argv[argindex]
                + '\n\t Usage: ' + __usage__)
        cmdlinearg = sys.argv[argindex]
        funcstring = cmdlinearg.replace('.','_').replace('-','')
        for index in range(0, len(AttributeNamesToDerive)):
            # Each derived attribute column needs its own stateful func.
            if mycase == 1:
                func = exp(Nstring)
            elif mycase == 2:
                obj = VisitorClass(Nstring)
                func = obj.visit
            else:   # only other case
                func = delta(Nstring)
            newattrname = AttributeNamesToDerive[index] + '_' + funcstring
            AttributeDerivation[newcolumn] = (func,
                AttributeColumnsToDerive[index])
            newcolumn += 1
            outheader.append(newattrname)
        # AttributeDerivation maps an int in order of derivator func,
        #   where func takes a (cell), to  ->
        #       (func, underivedColumnForAttr)
    outkeys = sorted(AttributeDerivation.keys()) # int positions
    for rowix in range(0,len(outdataset)):
        row = outdataset[rowix]
        rowtail = []
        for outcolumn in outkeys:
            func, sourcecolumn = AttributeDerivation[outcolumn]
            cell = func(row[sourcecolumn])
            rowtail.append(cell)
        row.extend(rowtail)
        row.append(targetValueList[rowix])
        
    outdataset.sort(key=lambda row : (row[0], row[1])) # year, month
    outfilename = sys.argv[1].replace('.csv', '_Derive.csv')
    outheader.append(inheader[-1])
    # STUDENT 5: 24% Complete the following output code:
    # 5a. open outfilename in write mode with newline=''
    # 5b. construct a csv.writer around the open file handle
    # 5c. writerow the outheader
    # 5d. writerows the outdataset
    # 5e. close the output open file handle
    # 5a, 5b, 5c, 5d
    with open(outfilename, 'w', newline='') as outfile:
        """
        Writes the processed data to an output CSV file.

        This block of code opens the output file (specified by 'outfilename') in write mode. 
        It ensures that no additional newline characters are inserted into the output file 
        (hence 'newline=''').

        A CSV writer object ('writer') is then created for the output file. This writer is used 
        to write rows into the file in CSV format. First, the header row ('outheader') is written, 
        which contains the names of the columns. Following the header, all rows of processed data 
        ('outdataset') are written to the file. Each row in 'outdataset' represents a row in the 
        final output CSV file.

        This ensures that the output file contains both the headers and the corresponding data, 
        formatted correctly as a CSV file. Once all data is written, the file is automatically 
        closed upon exiting the 'with' block, ensuring that no data is left unwritten due to 
        an unclosed file handle.
        """
        writer = csv.writer(outfile)
        writer.writerow(outheader)
        writer.writerows(outdataset)
