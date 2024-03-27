# partialBindings.py D. Parson, Fall 2023
# Demo three ways to create partial bindings for function parameters:
# We want to add cell at 'hdr0' and 'hdr1' for each row.
# Attributes 'hdr0' and 'hdr1' are not at [0] and [1] in rows of data,
# they are at some unknown index into each row. We want to avoid mapping
# 'hdr0' and 'hdr1' to their columns repeatedly for each row.
# Method 1: Use an object whose constructor
#   binds hdr column names to column numbers.
# Method 2: Use a closure whose outer function
#   binds hdr column names to column numbers.
# Method 3: Use an partial function whose call to partial()
#   binds hdr column names to column numbers.
from random import Random
from functools import partial
from sklearn.utils import shuffle
import pprint
import sys
import time

rgen = Random(12345)    # random number generator

if __name__ == '__main__':
    # Create an in-core CSV-like table with a header.
    hdr = ['hdr' + str(i) for i in range(0, 10)] # next move the names around
    hdr = shuffle(hdr, random_state=42)  # seed it for fixed shuffling
    print('hdr:', hdr)
    table = [hdr]
    for rowix in range(0,15):   # 15 rows of data
        row = []
        for colix in range(0, len(hdr)):
            row.append(rgen.randint(0,20))
        table.append(row)
    pprint.pprint(table)
    # We want to add cell at 'hdr0' and 'hdr1' for each row.
    # We want to avoid mapping 'hdr0' and 'hdr1' to their columns repeatedly.
    def applicationFunction(columnNumberList, datarow):
        # application function with unbound parameters.
        # If our Methods were in a reusable library, we'd pass
        # applicationFunction to do the specific work, so we
        # could use this approach with differing applicationFunctions.
        # This does cost a function call instead of hard coding
        # an arithmetic expression like datarow[h0col] + datarow[h1col].
        # We need to accommodate applicationFunction with varying
        # number of parameters. We do that with a list of values.
        # If we were building more than 1 derived attribute, the
        # return would be a list of those scalars, not a single sum.
        return sum([datarow[col] for col in columnNumberList])

    # Method 1: Use an object.
    # The constructor binds the column numbers to avoid repeatedly
    # mapping the hdr column names to their positions for each row.
    class VisitorClass(object):
        # __init__ is the constructor. self is the "this object" pointer.
        def __init__(self, headerList, colNameList, appFunc):
            self.columnList = [headerList.index(cname)
                for cname in colNameList]
            self.appFunc = appFunc
        def visit(self, row): # so-called 'visitor' object-oriented pattern
            return self.appFunc(self.columnList, row)

    # This is not part of the class:
    rvobj = VisitorClass(table[0], ['hdr0', 'hdr1'], applicationFunction)
        # header & names of columns & applicationFunction
    sumA = [rvobj.visit(row) for row in table[1:]]
    print('rvobj sumA:')
    pprint.pprint(sumA, indent=4)

    # Method 2: Use a closure.
    # The closure binds the column numbers to avoid repeatedly
    # mapping the hdr column names to their positions for each row.
    def visitorClosure(headerList, colNameList, applicationFunction):
        columnList = [headerList.index(cname) for cname in colNameList]
        def visit(row):
            # Function visit() retains access to values of h0col and h1col
            # even after visitorClosure returns that visit function.
            return applicationFunction(columnList, row)
        return visit

    # This is not part of the closure:
    rvclosure = visitorClosure(table[0], ['hdr0', 'hdr1'], applicationFunction)
    sumB = [rvclosure(row) for row in table[1:]]
    print('rvclosure sumB:')
    pprint.pprint(sumB, indent=4)

    # Method 3: Use a partial function.
    # The partial function binds the column numbers to avoid repeatedly
    # mapping the hdr column names to their positions for each row.
    partialFunc = partial(applicationFunction, columnNumberList=
        [table[0].index(cname) for cname in ['hdr0', 'hdr1']])
    # Apply the partial function with the 3rd param datarow bound to data.
    sumC = [partialFunc(datarow=row) for row in table[1:]]
    print('partial sumC:')
    pprint.pprint(sumC, indent=4)

    # Above are the functional tests. Speed tests added 9/11/2023
    __usage__ = 'python partialBindings.py ITERATIONS object|closure|partial'
    if len(sys.argv) >= 3:
        iterations = int(sys.argv[1])
        if iterations < 1:
            raise ValueError('INVALID NEGATIVE ITERATIONS: '
                + __usage__)
        if not sys.argv[2] in ('object', 'closure', 'partial'):
            raise ValueError('INVALID APPROACH: '
                + sys.argv[2] + ',' +  __usage__)
        # Don't bother storing a massive table for timing. Just use table[1].
        starttime = time.time()
        startcpu = time.process_time()
        if sys.argv[2] == 'object': # Keep this if out of the loop being timed.
            for i in range(0,iterations):
                sumA = rvobj.visit(table[1])
        elif sys.argv[2] == 'closure':
            for i in range(0,iterations):
                sumB = rvclosure(table[1])
        else:
            for i in range(0,iterations):
                sumC = partialFunc(datarow=table[1])
        cputime = time.process_time() - startcpu
        walltime = time.time() - starttime
        print(sys.argv[2],'CPU time =',round(cputime,6),
            'elapsed =',round(walltime,6), 'seconds')
