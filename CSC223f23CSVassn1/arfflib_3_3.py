'''
Upgrade to arfflib_3_3.py in September 2022:
    A. Avoid divide-by-0 in wekaCorrelationCoefficent.
    B. Support read .arff.gz and .csv.gz files in readARFF() and readCSV
        and writeARFF.
Upgrade to arfflib_3_2.py in April 2022:
    A. Add relationstring parameter to writeARFF to avoid sys.argv use. Apr 18
    B. writeARFF Numeric stored as numpy.nan converted to unknown (None). Apr 18
    C. Added readCSV that returns csv file in both ARFF and CSV data formats.
       This required importing csv library module.
    D. projectARFF's 'useless' filter now projects useless columns as
       single-valued columns (same as arfflib_3_1) OR single-valued columns
       containing None (unknown) values mixed in.
    E. Added functions CSVhdr2ARFFhdr and ARFFhdr2CSVhdr tested in plotcsv.py.
Upgrade to arfflib_3_1.py 10/25/2020.
arfflib_3_0.py for upcoming enhancements for Fall 2020 CSC523, Dale E. Parson,
3 as in Python 3 (not testing Python 2 -- unsupported), and
.0 is initial release September 14, 2020. Edits in .0:
  .0 EDIT 1: Removed mean, median, stddev, and minmax functions;
     import the statistics package to get these. Changed mode to
     multimode, which reports multiple "peak' values when there are multiples.
  .0 EDIT 2: Added functions projectARFF, joinARFF, ARFFtoCSV, deriveARFF,
      discretizeARFF, StringToNominal and Normalize from arffedit.py,
      kappa function that also returns correct/incorrect instances.
      Modified readARFF & writeARFF and internal DATA representation of
      'nominal' types to be strings, which cuts down overhead going to sklearn,
      and these strings were being stored identically & redundantly, anyway.
      The attribute type entry is still
      ('nominal', {NOMINAL_LIST_IN_STRING_FORM}, PYTHON_LIST_OF_NOMINAL_SYMBOLS)
      because the sorted PYTHON_LIST_OF_NOMINAL_SYMBOLS is still useful as 
      confusion matrix labels and elsewhere when nominals are in a sorted order,
      e.g., from discretizeARFF.
      Added media back in as stringNumMedian, which works with an even number
      of string-valued lists; it just returns the one to the left of center;
      statistics.median works with odd-size string lists but not even.
      Added sortARFF for sorting instances, imputeARFF for replacing unknowns.
  .2 EDIT 1: Added functions projectARFF, joinARFF, ARFFtoCSV, deriveARFF,

#
POST-.0 EDITS:
#
PRE-.0 EDITS:
arfflib.py, Dale E. Parson, January 2018, adapted from:
bayescalc.py, Dale E. Parson, Summer 2013
This module is for reading & writing ARFF
files (attribute Relation File Format) used by Weka.
main is a test driver
September 2019: Ported to work with Python 2.x and 3.x,

readARFF and writeARFF are the original library functions of
use in this module. The non-private functions (__functions__() are private)
are useful as well. The __main__ code is a test driver.

mergeARFFinto added September 2019 to merge ARFF files with same attributes.
Note also mean, stddev (population standard deviation), median, and
mode functions, where mode and median can deal with non-numeric elements.

quoteStringIfNeeded made public March 2020 for new filters that need to
wrap strings in extra quoting.
'''

import sys
import re
import copy
import math
import numpy
import os.path
import datetime
import types
import random
import csv
import gzip
import statistics as stats
from statistics import mean, median

# __attr_re__ = re.compile(r'^\s*@attribute\s+(\S+)\s+(\S+)')
# __date_re__ parenthesizes name and date-format
__date_re__ = re.compile(r'^\s*@attribute\s+(\S+)\s+date\s+(\S+.*)$')
# __attr_re__ parenthesizes name and type
__attr_re__ = re.compile(r'^\s*@attribute\s+(\S+)\s+(\S+.*)$')
# __data_re__ is the @data card
__data_re__ = re.compile(r'^\s*@data.*$')

def __getAttrIndices__(af):
    '''
    Returns a map from attribute name to (offset, type) pair,
    where offset is attribute position, starting at 0, and type is
    described in the readARFF function documentation.
    Parameter af is the already-open ARFF file handle.
    Return value is the in-core map "result[aname] = (attrindex, atype)",
    where aname is the attribute name, attrindex is its index starting at 0,
    and atype is per the readARFF comments.
    '''
    result = {}
    attrCount = 0
    line = af.readline()
    while line:
        sline = line.strip()
        dm = __date_re__.match(sline)
        am = __attr_re__.match(sline)
        if dm:
            aname = dm.group(1)
            wformat = dm.group(2).strip()
            # wformat is Weka format, see
            # https://www.cs.waikato.ac.nz/ml/weka/arff.html
            # Appears to be based on Java format in java.text.SimpleDateFormat
            # https://docs.oracle.com/javase/8/docs/api/index.html
            # Internal we must use Python's datetime strptime() format:
            # https://docs.python.org/2/library/time.html#time.strptime
            # https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
            # This section converts Weka's format string wformat to
            # Python's pformat, and stores the type as a
            # ('date', wformat, pformat) 3-tuple.
            pformat = ''
            wremains = wformat
            while wremains:
                if wremains.startswith('yyyy') or wremains.startswith('YYYY'):
                    pformat = pformat + "%Y"
                    wremains = wremains[4:]
                elif wremains.startswith('yy') or wremains.startswith('YY'):
                    pformat = pformat + "%y"
                    wremains = wremains[2:]
                elif wremains.startswith('MM'):
                    pformat = pformat + "%m"
                    wremains = wremains[2:]
                elif wremains.startswith('M'):
                    pformat = pformat + "%m"
                    wremains = wremains[1:]
                elif wremains.startswith('dd'):
                    pformat = pformat + "%d"
                    wremains = wremains[2:]
                elif wremains.startswith('HH'):
                    pformat = pformat + "%H"
                    wremains = wremains[2:]
                elif wremains.startswith('mm'):
                    pformat = pformat + "%M"
                    wremains = wremains[2:]
                elif wremains.startswith('ss'):
                    pformat = pformat + "%S"
                    wremains = wremains[2:]
                elif (wremains.startswith('z') or wremains.startswith('Z')
                        or wremains.startswith('X')):
                    pformat = pformat + "%Z"
                    wremains = wremains[1:]
                else:
                    pformat = pformat + wremains[0]
                    wremains = wremains[1:]
            result[aname] = (attrCount, ('date', wformat, pformat))
            attrCount += 1
            # print("DEBUG mapped", aname, "TO", result[aname])
        elif am:
            aname = am.group(1)
            atype = am.group(2).strip()
            if atype.startswith('{') and atype.endswith('}'):
                nlist = atype[1:-1].strip().split(',')
                for i in range(0,len(nlist)):
                    nlist[i] = nlist[i].strip();
                realtype = ('nominal', atype, nlist)
            else:
                realtype = atype
            result[aname] = (attrCount, realtype)
            attrCount += 1
            # print("DEBUG mapped", aname, "TO", result[aname])
        elif __data_re__.match(sline):
            break
        line = af.readline()
    return result

def __getDataset__(af, amap):
    # Start helper function __mergeInstanceStrings__.
    def __mergeInstanceStrings__(instlist):
        # We have split along ','; fix cases here ',' is in a quoted string.
        # WHEN A STRING CONTAINS A "," MERGE WITH ITS PARTNER
        result = []
        ix = 0
        while ix < len(instlist):
            field = instlist[ix]
            if (field.startswith("'") or field.startswith('"')):
                terminator = field[0]
                fld = field
                if fld.endswith(terminator):
                    result.append(fld)
                    ix += 1
                else:
                    ix += 1
                    while ix < len(instlist):
                        f = instlist[ix]
                        # Re-insert the commas as part of the quoted string.
                        if (f.endswith(terminator)):
                            fld = fld + ',' + f
                            ix += 1
                            break
                        else:
                            fld = fld + ',' + f
                            ix += 1
                    result.append(fld)
            else:
                result.append(field)
                ix += 1
        return result
    # End helper function __mergeInstanceStrings__.
    result = []
    line = af.readline()
    while line:
        sline = line.strip()
        if sline[0:1] == '%':       # Comment line
            line = af.readline()
            continue
        instance = sline.split(',')
        # WHEN A STRING CONTAINS A "," MERGE WITH ITS PARTNER
        instance = __mergeInstanceStrings__(instance)
        for a in amap.keys():
            pos, t = amap[a]
            # print("DEBUG dataset", a, pos, t, instance[pos], instance)
            if pos >= len(instance):
                sys.stderr.write("ERROR, attribute " + str(a)
                    + "maps to position, type " + str(pos) + "," + str(t)
                    + ", instance has length " + str(len(instance))
                    + ":\n\t" + str(instance) + "\n")
                sys.stderr.flush()
            if instance[pos] == '?':
                instance[pos] = None
            elif t == 'numeric':
#               sys.stderr.write("DEBUG instance[pos]: "
#                   + str(instance[pos]) + '\n')
                vf = float(instance[pos])
                vi = int(vf)
                v = vi if (vi == vf and not '.' in instance[pos]) else vf
                instance[pos] = v
            elif t == 'string' and instance[pos].startswith("'"):
                instance[pos] = instance[pos][1:-1]
            elif isinstance(t, tuple) and len(t) == 3 and t[0] == 'date':
                # No need to strip anything.
                instance[pos] = (instance[pos],
                    datetime.datetime.strptime(instance[pos], t[2]))
            elif isinstance(t, tuple) and len(t) == 3 and t[0] == 'nominal':
                if instance[pos].startswith("'"):
                    instance[pos] = instance[pos][1:-1]
                # instance[pos] = (instance[pos], instance[pos])
                # pass        # store same as before 9/20/2020, but not twice
                # if instance[pos].startswith("'"):
                    # instance[pos] = instance[pos][1:-1] # data now stored like a string
        result.append(instance)
        # print("DEBUG instance", instance)
        line = af.readline()
    return result

def readARFF(fname):
    '''
    Reads ARFF file named fname and returns (attrmap, dataset), where
    attrmap is the map from attrname -> (offset, type) returned by
    __getAttrIndices__, and dataset is a 2D list indexed on [row][offset]
    that holds actual data instances.
    This offset is attribute position, starting at 0, and type is
    one of a date-3-tuple, 'numeric', 'string', a nominal set in {} delimiters,
    or a ARFF datetime value. A nominal type field is a 3-tuple of
    ('nominal', {NOMINAL_LIST_IN_STRING_FORM}, PYTHON_LIST_OF_NOMINAL_SYMBOLS),
    and a datetime (Weka date) is a 3-tuple consisting of
    ('date', Weka-format-string, Python-datetime-strptime-format-string).

    A nominal attribute-value in the dataset is a simple string as read from an ARFF
    file, and a date attribute-value is a 2-tuple
    (STRING_VALUE, Python datetime.datetime object).
    Updated 9/25/2022 if fname ends with '.gz' open using
    gzip.open().
    '''
    if fname.endswith('.gz'):
        af = gzip.open(fname, mode='rt')
    else:
        af = open(fname, 'r')
    amap = __getAttrIndices__(af)
    dataset = __getDataset__(af, amap)
    af.close()
    return((amap, dataset))

def readCSV(fname, isUsingNan=False):
    '''
    Reads CSV file named fname and attempts to infer numeric columns from
    values, where fname names a CSV file with a single header row of strings
    followed by one or more data rows with the same number of columns as
    the header. The file must have valid characters for csv.reader.
    Parameter isUsingNan if True uses numpy.nan (not a number)
    for blank numbers else uses None in the returned dataset.
    Return value is a 6-tuple (attrmap, dataset, CSVheaderRow,
        nameToCol, colToName, colToType),
    where attrmap and dataset are same as return values from readARFF and
    ARFFtoCSV (these are ARFF types and rows of data respectively),
    CSVheaderRow is the row of CSV header names without any type info,
    nameToCol is a dict mapping header name to column number,
    colToName is a dict mapping column number to header name,
    and colToType maps column number to either str or float as Python data
    types for that column in the data. Only strings, floats, and
    (None or numpy.nan) appear in the returned dataset.
    See readARFF and ARFFtoCSV documentation comments.
    Updated 9/25/2022 if fname ends with '.gz' open using
    gzip.open().
    '''
    if fname.endswith('.gz'):
        inf = gzip.open(fname, mode='rt')
    else:
        inf = open(fname, 'r')
    rdr = csv.reader(inf, delimiter=',', quotechar='"', dialect='excel')
    table = []
    row = list(rdr.__next__())
    linenum = 1
    while row != None:
    # Unterminated quote " in an incoming data file was causing
    # "for row in rdr:" to terminate prematurely with a cryptic error
    # message. Processing each row using __next__() to get better insight.
    # for row in rdr:
        if len(row) > 0:
            # Empty final row appeared when reading .csv with no such entry.
            table.append(row)
        linenum += 1
        try:
            row = list(rdr.__next__())
        except StopIteration:
            row = None
            break
        except Exception as errmsg:
            sys.stderr.write("WARNING readCSV read error at line "
                + str(linenum) + ": " + str(errmsg) + '\n')
            row = []
            # continue
    inf.close()
    nameToCol = {}
    colToName = {}
    colToType = {}
    for index in range(0,len(table[0])):
        nameToCol[table[0][index]] = index
        colToName[index] = table[0][index]
        colToType[index] = float                # assume float until disproved
    for row in table[1:]:                       # skip header row
        for colix in range(0, len(row)):
            strv = row[colix].strip()
            if strv != '':                      # treat as nan
                try:
                    value = float(strv)
                except ValueError:
                    colToType[colix] = str
    for row in table[1:]:                       # skip header row
        for colix in range(0, len(row)):
            if colToType[colix] == float:
                strv = row[colix].strip()
                if strv != '':
                    row[colix] = float(strv)
                else:
                    row[colix] = numpy.nan if isUsingNan else None
    attrmap = {}
    for col in sorted(colToName.keys()):
        nm = colToName[col]
        if colToType[col] == float:
            arfftype = 'numeric'
        else:
            arfftype = 'string'
        attrmap[nm] = (col, arfftype)
    return (attrmap, table[1:], table[0], nameToCol, colToName, colToType)

def CSVhdr2ARFFhdr(CSVheaderRow, nameToCol, colToName, colToType):
    '''
    Convert CSV header data as returned by readCSV to ARFF attribute
    mappings as returned by readARFF and and readCSV.
    Return value is attrmap as documented for readARFF. Parameter
    CSVheaderRow is the row of CSV header names without any type info,
    nameToCol is a dict mapping header name to column number,
    colToName is a dict mapping column number to header name,
    and colToType maps column number to either datetime.datetime,
    str or float as Python data types for that column in the data.
    The datetime.datetime formats used are ('date', 'yyyy-MM-dd HH:mm:ss',
    '%Y-%m-%d %H:%M:%S') as documented at
    https://docs.python.org/3/library/datetime.html#datetime-objects
    and https://www.cs.waikato.ac.nz/ml/weka/arff.html.
    Other colToType map as strings; nominal (set) values not supported.
    See readARFF and ARFFtoCSV and readCSV documentation comments.
    '''
    attrmap = {}
    badargs = False
    if (len(CSVheaderRow) != len(colToName.keys())
            or len(nameToCol.values()) != len(colToName.keys())
            or len(colToName.keys()) != len(colToType.keys())):
        badargs = True
    else:
        hnames = set(CSVheaderRow)
        ntcnames = set(nameToCol.keys())
        ctnnames = set(colToName.values())
        hcols = set(range(0, len(CSVheaderRow)))
        ntccols = set(nameToCol.values())
        ctncols = set(colToName.keys())
        cttcols = set(colToType.keys())
        if (hnames != ntcnames or ntcnames != ctnnames
                or hcols != ntccols or ntccols != ctncols
                or ctncols != cttcols):
            badargs = True
    if badargs:
        raise ValueError("ERROR, Inconsistent parameters to CSVhdr2ARFFhdr")
    for col in colToName.keys():
        nm = colToName[col]
        tp = colToType[col]
        twotuple = None
        if (tp == float or tp == int):
            twotuple = (col, 'numeric')
        elif tp == datetime.datetime:
            twotuple = (col, ('date', 'yyyy-MM-dd HH:mm:ss',
                '%Y-%m-%d %H:%M:%S'))
        else:
            twotuple = (col, 'string')
        attrmap[nm] = twotuple
    return attrmap

def ARFFhdr2CSVhdr(attrmap):
    '''
    Convert ARFF attrmap (typed header) data as returned by readARFF &
    readCSV to CSV (CSVheaderRow, nameToCol, colToName, colToType)
    4-tuple as returned by and documented for readCSV.
    See readARFF and readCSV documentation comments.
    '''
    attrmapIXs = set([])
    CSVheaderRow = []
    nameToCol = {}
    colToName = {}
    colToType = {}
    for nm in attrmap.keys():
        typetagpair = attrmap[nm]
        ix = typetagpair[0]
        typetag = typetagpair[1]
        nameToCol[nm] = ix
        colToName[ix] = nm
        if typetag == 'numeric':
            colToType[ix] = float
        elif (isinstance(typetag, tuple) and len(typetag) > 0
                and typetag[0] == 'date'):
            colToType[ix] = datetime.datetime
        else:
            colToType[ix] = 'string'
        attrmapIXs.add(ix)
    if attrmapIXs != set(range(0, len(attrmap.keys()))):
        raise ValueError("ERROR, Inconsistent parameters to ARFFhdr2CSVhdr")
    for ix in range(0, len(colToName)):
        CSVheaderRow.append(colToName[ix])
    return ((CSVheaderRow, nameToCol, colToName, colToType))

def quoteStringIfNeeded(string):
    '''
    Fix string attributes that need to be wrapped in quotes.
    string parameter is a string that may contain spaces quotes tabs.
    Return a newly constructed string with quoting if needed.
    Just returns the input argument if it is not a string.
    '''
    # Fix strings attributes that need to be wrapped in quotes.
    # print("DEBUG string 1 ",string)
    if (type(string) == str and (
            (" " in string) or ("," in string) or ("'" in string)
                or ('"' in string) or ('\t' in string) or ('\f' in string))):
        # print("DEBUG string 2 ",string)
        if ((string.startswith("'") and string.endswith("'"))
                or (string.startswith('"') and string.endswith('"'))):
            pass # It already is delimited.
        elif "'" in string:
            string = '"' + string + '"'
        else:
            string = "'" + string + "'"
    return string

def writeARFF(fname, relationstring, attrmap, dataset, isDebugMode=False,
        clobber=False):
    '''
    Writes ARFF file named fname with data in attrmap and dataset, where
    attrmap is the map from attrname -> (offset, type) returned by
    __getAttrIndices__, and dataset is a 2D list indexed on [row][offset]
    that holds actual data instances. Set isDebugMode to True
    (default is False) for debugging output to sys.stderr.
    Set clobber to True (default is False) to over-write output fname
    without warning, added 11/24/2019. New param relationstring added
    after fname on 4/18/2022.
    Updated 9/25/2022 if fname ends with '.gz' open using
    gzip.open().
    '''
    if os.path.lexists(fname) and not clobber:
        msg = 'ERROR, Please remove output file: ' + fname + '\n'
        sys.stderr.write(msg + '\n')
        raise RuntimeError(msg)
    if fname.endswith('.gz'):
        fout = gzip.open(fname, mode='wt')
    else:
        fout = open(fname, 'w')
    # REPLACED WITH PARAM IN 3_2 relationstring = sys.argv[0]
    # REPLACED WITH PARAM IN 3_2 for arg in sys.argv[1:]:
        # relationstring = relationstring + " " + arg
    # relationstring = relationstring + " @ " + str(datetime.datetime.now())
    if "'" in relationstring:
        relationstring = '"' + relationstring + '"'
    else:
        relationstring = "'" + relationstring + "'"
    # fout.write('@relation tmprelation\n')
    fout.write('@relation ' + relationstring + '\n')
    fout.write('% ARFF file generated @ ' + str(datetime.datetime.now()) + '\n')
    newmap = remapAttributes(attrmap)
    newkeys = list(newmap.keys())
    newkeys.sort()
    for k in newkeys:
        fout.write('@attribute ' + newmap[k][0] + ' '
            + ('numeric' if (newmap[k][1] == 'float' or newmap[k][1] == 'int')
                else ('date ' + newmap[k][1][1])
                    if (isinstance(newmap[k][1],tuple)
                        and newmap[k][1][0] == 'date')
                else (newmap[k][1][1])
                    if (isinstance(newmap[k][1],tuple)
                        and newmap[k][1][0] == 'nominal')
                else newmap[k][1]) + '\n')
    fout.write('@data\n')
    for rix in range(0, len(dataset)):  # Iterate over rows in relation.
        row = dataset[rix]
        datum = row[0]
        sdatum = str(datum).strip()
        if sdatum == '' or sdatum == 'nan' or sdatum == 'None':
            datum = '?'
        if (isinstance(datum,tuple) and len(datum) == 2):
            # nominal or date, use the string form
            # 9/20/2020, ONLY DATE NOW, use the string form
            datum = datum[0]
        elif ((isinstance(datum, float) or isinstance(datum, int))
                and (numpy.isnan(datum) or (str(datum).strip() == 'nan'))):
            datum = None
        datum = quoteStringIfNeeded(str(datum) if (not datum is None) else '?')
        fout.write(str(datum))
        for colix in range(1, len(row)):
            datum = row[colix]
            sdatum = str(datum).strip()
            if sdatum == '' or sdatum == 'nan' or sdatum == 'None':
                datum = '?'
            if (isinstance(datum,tuple) and len(datum) == 2):
                # nominal or date, use the string form
                # date only as of 9/20/2020, nominal data value is now just a string
                datum = datum[0]
            elif ((isinstance(datum, float) or isinstance(datum, int))
                    and (numpy.isnan(datum) or (str(datum).strip() == 'nan'))):
                datum = None
            datum = quoteStringIfNeeded(str(datum) if (not datum is None) else '?')
            fout.write("," + str(datum))
            if isDebugMode:
                # Test whether reading a test arff file's datetime
                # field into a Python datetime works correctly.
                if (isinstance(newmap[colix][1],tuple)
                        and len(newmap[colix][1]) == 3
                        and newmap[colix][1][0] == 'date'):
                    dt = row[colix][1]
                    sys.stderr.write("DEBUG PYTHON DATETIME FIELD "
                        + newmap[colix][0] + ": " + str(dt) + '\n')
        fout.write('\n')
    fout.close()

def mergeARFFinto(relation1, relation2):
    '''
    Merge the data records in relation2[1] into relation1[1],
    i.f.f. their attribute declarations in relation1[0] and
    relation2[0] are ==. The return value is None, with relation1
    mutated to hold the appended records. Both parameters have the same format
    as the value returned by readARFF. Mutation is used to avoid
    overhead of repeated copying of relations when merging many
    relations. An application can use copy.deepcopy() on the
    original relation1 if it wishes to save an original copy.
    '''
    if relation1[0] != relation2[0]:
        raise ValueError(
            "mergeARFFinto applied against differing attribute types")
    for element in relation2[1]:
        relation1[1].append(element)
    return None

def remapAttributes(attrmap):
    '''
    attrmap is a map from "attrname -> (offset, type)", and
    remapAttributes returns a map "offset -> (attrname, type)"
    '''
    newmap = {}
    for attrname in attrmap.keys():
        newmap[attrmap[attrname][0]] = (attrname, attrmap[attrname][1])
    return newmap

__projectionTypes__ = set(['numeric', 'string', 'nominal', 'date'])
def projectARFF(attrmap, dataset, attributesToProject, isKeepingAttributes):
    '''
    Return new ARFF data that is a projection of a copy of attrmap, dataset,
    where attrmap is the map from attrname -> (offset, type) returned by
    __getAttrIndices__ as in readARFF & writeARFF, dataset is a 2D list
    indexed on [row][offset] that holds actual data instances,
    attributesToProject is a list of attributes to keep or remove,
    and isKeepingAttributes is True if attributesToProject should be KEPT
    in the return value, False if attributesToProject should be DISCARDED
    in the return value. The attributesToProject can include int attribute
    offsets, str attribute names, and/or 1-tuples containing
    ('numeric',), ('string',), ('nominal',), ('date',), and/or ('useless',),
    where ('useless',) matches all single-value columns in the data.
    The return value is a new (attrmap, dataset) pair as in readARFF's
    return value. added 09/13/2020
    '''
    # print("DEBUG ENTER PJ len(dataset)", len(dataset), "attributesToProject", attributesToProject) ; sys.stdout.flush()
    # sys.stderr.write("DEBUG ENTER PJ len(dataset) " + str(len(dataset)) + " attributesToProject " + str(attributesToProject) + '\n'); sys.stderr.flush()
    wildcardsSeen = set([])
    keepIndices = set([])
    for atr in attributesToProject:
        if isinstance(atr, int):
            if atr >= len(attrmap) or atr < 0:
                raise ValueError("INVALID NUMERIC INDEX: "
                    + str(atr) + " in call to projectARFF")
            keepIndices.add(atr)
        elif isinstance(atr, str):
            if not atr in attrmap.keys():
                raise ValueError("INVALID ATTRIBUTE NAME INDEX: "
                    + str(atr) + " in call to projectARFF")
            keepIndices.add(attrmap[atr][0])
        elif isinstance(atr, tuple) and len(atr) == 1:
            typequery = atr[0]
            if typequery in wildcardsSeen:
                continue
            if typequery in __projectionTypes__:
                for indexTypePair in attrmap.values():
                    if isinstance(indexTypePair[1], tuple):
                        typetag = indexTypePair[1][0]
                        # nominal or date
                    else:
                        typetag = indexTypePair[1]
                        # numeric or string
                    if typetag == typequery:
                        keepIndices.add(indexTypePair[0])
            elif typequery != 'useless':
                raise ValueError("INVALID ATTRIBUTE INDEX: "
                    + str(atr) + " in call to projectARFF")
            else:
                for aix in range(0, len(attrmap)):
                    if aix in keepIndices:
                        continue
                    firstval = dataset[0][aix]
                    isuseless = True
                    for instix in range(1, len(dataset)):
                        if (dataset[instix][aix] != firstval and
                                dataset[instix][aix] != None):
                            isuseless = False
                            break
                    if isuseless:
                        keepIndices.add(aix)
            wildcardsSeen.add(typequery)
        else:
            raise ValueError("INVALID ATTRIBUTE INDEX: "
                + str(atr) + " in call to projectARFF")
    # set keepIndices now holds the attributes to keep or delete,
    # depending on isKeepingAttributes.
    keepList = sorted(keepIndices)
    loseList = []
    for atrbix in range(0, len(attrmap)):
        if not atrbix in keepIndices:
            loseList.append(atrbix)
    loseIndices = set(loseList)
    if not isKeepingAttributes:
        tmp = keepList
        keepList = loseList
        loseList = tmp
        tmp = keepIndices
        keepIndices = loseIndices
        loseIndices = tmp
    newdataset = [[] for ii in range(0, len(dataset))]
    for instix in range(0, len(dataset)):
        for atrbix in keepList:
            # sys.stderr.write('DEBUG PA ' + str(instix) + ' from ' + str(len(dataset)) + ' attrix ' + str(atrbix) + '\n'); sys.stderr.flush();
            newdataset[instix].append(dataset[instix][atrbix])
    # data are updated, now update the type map indices
    newmap = copy.deepcopy(attrmap)
    for ky in attrmap.keys():
        kyix = attrmap[ky][0]   # The index of this attribute
        if kyix in loseIndices:
            del newmap[ky]
        else:
            newkeyix = kyix
            for atrbix in loseList:
                if kyix > atrbix:
                    newkeyix -= 1
                else:
                    break   # atrbix keeps going up; kyix is smaller
            newmap[ky] = (newkeyix, attrmap[ky][1])
    return (newmap, newdataset)

def joinARFF(attrmap, dataset, nameTypePairs, rowsOfNewColumns):
    '''
    Return new ARFF data that is a join of a copy of attrmap, dataset,
    where attrmap is the map from attrname -> (offset, type) returned by
    __getAttrIndices__ as in readARFF & writeARFF, dataset is a 2D list
    indexed on [row][offset] that holds actual data instances,
    nameTypePairs is an ordered list of (NAME, TYPE) attribute columns
    to concatenate with the data rows in dataset, and rowsOfNewColumns are
    the actual rows of data to concatenate with the number of columns and
    the current types given in nameTypePairs. In nameTypePairs, NAME
    must be the string name of an attribute not already in attrmap, and
    TYPE must be the string 'string' or 'numeric'; 'numeric' columns
    must be cast-able to float, and they are cast to float within
    rowsOfNewColumns. Weka nominal and date types are not supported
    in the added columns. The input attrmap and dataset are not mutated.
    joinARFF returns a newattrmap, newdataset pair.
    '''
    if len(dataset) != len(rowsOfNewColumns):
        raise ValueError("UNEQUAL NUMBER OF DATA INSTANCES "
            + str(len(dataset)) + " versus " + str(len(rowsOfNewColumns))
            + " in call to joinARFF")
    newColumnsIndex = len(attrmap)
    nattrmap = copy.deepcopy(attrmap)
    ninstances = []
    nix = -1
    for NAME, TYPE in nameTypePairs:
        nix += 1
        if (NAME in attrmap.keys()) or (NAME in nattrmap.keys()):
            # Watch out for duplicates within nameTypePairs.
            raise ValueError("DUPLICATE ATTRIBUTE NAME: "
                + NAME + " in call to joinARFF")
        elif TYPE == 'numeric':
            try:
                for inst in rowsOfNewColumns:
                    # print("DEBUG inst[nix]", type(inst[nix]), inst[nix], "AT", nix)
                    # sys.stdout.flush()
                    inst[nix] = float(inst[nix]) \
                        if (inst[nix] != None) else None
            except (ValueError, TypeError) as oops:
                raise ValueError("INVALID NUMERIC ATTRIBUTE: "
                    + NAME + ", value = '" + str(rowsOfNewColumns[nix])
                    + " in call to joinARFF: " + str(oops))
        elif TYPE == 'string':
            for inst in rowsOfNewColumns:
                inst[nix] = str(inst[nix])  \
                    if (inst[nix] != None) else None
        else:
            raise ValueError("INVALID ATTRIBUTE TYPE: '"
                + TYPE + "' in call to joinARFF")
        nattrmap[NAME] = (newColumnsIndex, TYPE)
        newColumnsIndex += 1
    for ixx in range(0, len(dataset)):
        ninstances.append(dataset[ixx] + rowsOfNewColumns[ixx])
    return (nattrmap, ninstances)

def deriveARFF(attrmap, dataset, nameTypeFunctionTriplets):
    '''
    Return new ARFF data that is an edit of a copy of attrmap, dataset,
    where attrmap is the map from attrname -> (offset, type) returned by
    __getAttrIndices__ as in readARFF & writeARFF, dataset is a 2D list
    indexed on [row][offset] that holds actual data instances,
    nameTypeFunctionTriplets is an ordered list of (NAME, TYPE, FUNC)
    attribute columns to mutate OR to concatenate with the data rows in
    dataset. In nameTypeFunctionTriplets, NAME may be the string name
    of an attribute that is already in attrmap, in which case the copy
    of (attrmap, dataset) is mutated, or NAME is a new attribute name to
    be joined to the copy of (attrmap, dataset). The result TYPE must be either
    'string' or 'numeric'. FUNC is a function that takes 1 argument,
    the instance (as a tuple) to be read by FUNC. FUNC should not hard-code
    attribute offsets into its data instances; instead, pass FUNC as a closure
    that has already captured its attribute indices to read. FUNC returns
    a value that deriveARFF either substitutes into the resulting
    NAMEd instance for mutation, or appends to a list of instance fields
    to be joined per joinARFF. Weka nominal and date types are not supported
    in the mutated/or/added columns. The input attrmap and dataset are not
    mutated. deriveARFF returns a newattrmap, newdataset pair. The order
    of evaluation of FUNC is left-to-right in nameTypeFunctionTriplets.

    UPDATE 1 October 2020: New attribute NAMEs in nameTypeFunctionTriplets
    are added to the copy of attrmap to be returned BEFORE applying their
    FUNCs in left-to-right order of declaration in nameTypeFunctionTriplets.
    Their offset columns are incremented starting at the original number
    of attributes, for example, if there are 3 original attributes at columns
    0, 1, and 2 in the dataset, then two new ones would be added at columns
    3 and 4, yielding 5 attributes total, with their columns initialized
    to None in the dataset copy BEFORE iterating over the FUNCs. That way,
    new derived attribute FUNCs can refer to other new attribute values
    in columns to their left. FUNCs apply left-to-right in a given instance
    before going on to the next instance.
    '''
    newattrmap = copy.deepcopy(attrmap)
    newdataset = copy.deepcopy(dataset)
    # NewNameTypePairs = []
    nameTypeFunctionOffsetQuads = []
    ocolumnsCount = len(newattrmap.keys())
    ncolumnsCount = 0
    for NAME, TYPE, FUNC in nameTypeFunctionTriplets:
        if TYPE != 'string' and TYPE != 'numeric':
            raise ValueError("INVALID ATTRIBUTE TYPE: " + TYPE
                + " in call to deriveARFF, must be 'string' or 'numeric'")
        if NAME in newattrmap.keys():
            if newattrmap[NAME][1] != TYPE:
                newattrmap[NAME] = (newattrmap[NAME][0], TYPE)
            nameTypeFunctionOffsetQuads.append(
                (NAME, TYPE, FUNC, newattrmap[NAME][0]))
        else:
            # NewNameTypePairs.append((NAME, TYPE))
            # nameTypeFunctionOffsetQuads.append((NAME, TYPE, FUNC, -1))
            # ADD IT NOW, 10/1/2020
            newattrmap[NAME] = (ocolumnsCount+ncolumnsCount, TYPE)
            nameTypeFunctionOffsetQuads.append(
                (NAME, TYPE, FUNC, newattrmap[NAME][0]))
            ncolumnsCount += 1
    for inst in newdataset:
        if ncolumnsCount > 0:
            # Mutate inst, do not construct a new one.
            for i in range(0, ncolumnsCount):
                inst.append(None)
        safeinst = tuple(inst)
        for NAME, TYPE, FUNC, OFFSET in nameTypeFunctionOffsetQuads:
            result = FUNC(safeinst)
            if TYPE == 'string':
                result = str(result)
            elif not(isinstance(result, int) or isinstance(result, float)):
                result = float(result)  # Force the type test.
            inst[OFFSET] = result
            if OFFSET >= ocolumnsCount:     # Just got changed from None
                safeinst = tuple(inst)
    return (newattrmap, newdataset)

def discretizeARFF(attrmap, dataset, attrname, bins,
        attrtype, useEqualFrequency):
    '''
    Return new ARFF data that is an edit of a copy of attrmap, dataset,
    where attrmap is the map from attrname -> (offset, type) returned by
    __getAttrIndices__ as in readARFF & writeARFF, dataset is a 2D list
    indexed on [row][offset] that holds actual data instances,
    attrname is the name of the numeric attribute to discretize,
    bins gives how many bins to split it into > 1, attrtype is either
    'string' or 'nominal', the latter for a sorted nominal set definition,
    and useEqualFrequency is False to split onto bins based on numeric range,
    True to try to make each bin the same size. The derived attribute is a
    string or nominal per attrtype.
    The returned (attrmap, dataset) is a mutated copy of the original.
    '''
    attrix = attrmap[attrname][0]
    oattrtype = attrmap[attrname][1]
    if oattrtype != 'numeric':
        raise ValueError("INVALID PREVIOUS ATTRIBUTE TYPE: " + str(oattrtype)
            + " for attribute " + attrname + " in discretizeARFF")
    if attrtype != 'string' and attrtype != 'nominal':
        raise ValueError("INVALID PROPOSED ATTRIBUTE TYPE: " + str(attrtype)
            + " for attribute " + attrname + " in discretizeARFF")
    nattrmap = copy.deepcopy(attrmap)
    values = sorted([dataset[ix][attrix] for ix in range(0, len(dataset))])
    bounds = []
    if useEqualFrequency:
        binsize = round(len(values) / bins)
        bstart = 0
        bend = min(bstart + binsize, len(values)-1)
        while bstart < len(values)-1:
            while bend < (len(values)-1) and values[bend+1] == values[bend]:
                bend += 1
            bounds.append((values[bstart], values[bend]))
            bstart = bend 
            bend = min(bstart + binsize, len(values)-1)
        # Sometimes this code gives ampty bins, delete them:
        fixbounds = []
        for bix in range(0, len(bounds)-1):
            lower, upper = bounds[bix]
            if not (lower == upper and bounds[bix+1][0] == upper):
                fixbounds.append(bounds[bix])
        finallower, finalupper = bounds[-1]
        if not (finallower == finalupper and finallower == upper):
            fixbounds.append(bounds[-1]) # append the top
        bounds = fixbounds
    else:
        binlen = (values[-1] - values[0]) / bins
        binfrom = values[0]
        while binfrom <= values[-1]:
            binto = binfrom + binlen
            bounds.append((binfrom, binto))
            binfrom += binlen
        if len(bounds) > bins:
            bounds[bins-1] = (bounds[bins-1][0], bounds[-1][1])
            # Just use topmost bound
            bounds = bounds[0:bins]
    sbounds = [str(bpair) for bpair in bounds]
    ndataset = copy.deepcopy(dataset)
    for inst in ndataset:
        v = inst[attrix]
        if v != None:
            vo = None
            for i in range(0, len(bounds)):
                if v >= bounds[i][0] and v < bounds[i][1]:
                    vo = sbounds[i]
                    break
            if vo == None:
                vo = sbounds[-1]
            inst[attrix] = vo
    if attrtype == 'string':
        nattrmap[attrname] = (attrix, 'string')
    else:
        # nominal
        atype = "{'" + sbounds[0] + "'"
        for nix in range(1, len(sbounds)):
            atype = atype + ",'" + sbounds[nix] + "'"
        atype = atype + '}'
        nattrmap[attrname] = (attrix, ('nominal', atype, sbounds))
    return (nattrmap, ndataset)

def sortARFF(attrmap, dataset, attributeKeys, sreverse=False):
    '''
    Sort a copy of the dataset list of instances without mutating
    the original, returning only the sorted result list,
    where attrmap is the map from attrname -> (offset, type) returned by
    __getAttrIndices__ as in readARFF & writeARFF, dataset is a 2D list
    indexed on [row][offset] that holds actual data instances,
    attributeKeys is a sequence of attribute offsets to be used as keys
    in the sort, with most significant attribute coming first, least
    significant last, and sreverse as in Python's sort()'s reverse argument.
    attributeKeys can contain either numeric indicies or string names
    of attribute indicies. Returns a sorted copy of dataset
    '''
    akeys = list(attributeKeys)
    for kix in range(0, len(attributeKeys)):
        k = attributeKeys[kix]
        if isinstance(k, str):
            if not k in attrmap.keys():
                raise ValueError("INVALID ATTRIBUTE Name: " + k
                    + " in sortARFF")
            akeys[kix] = attrmap[k][0]
        elif (not isinstance(k, int)) or k < 0 or k >= len(attrmap.keys()):
            raise ValueError("INVALID INTEGER ATTRIBUTE Index: " + str(k)
                + " in sortARFF")
        # else it is already a valid int
    ndata = copy.deepcopy(dataset)
    def keyextract(inst):
        keys = []
        for i in akeys:
            keys.append(inst[i])
        return keys
    ndata.sort(key=keyextract, reverse=sreverse)
    return ndata

def imputeARFF(attrmap, dataset, attributeKeys, replacement, seed=None):
    '''
    Replace unknown (None) attribute-values in a copy of the dataset list
    of instances without mutating the original, returning only the imputed
    result list, where attrmap is the map from attrname -> (offset, type)
    returned by __getAttrIndices__ as in readARFF & writeARFF,
    dataset is a 2D list indexed on [row][offset] that holds actual
    data instances, attributeKeys is a sequence of attribute offsets to be
    imputed, where attributeKeys=None means all attributes with unknown
    (None) values, and attributeKeys can contain either numeric indicies
    or string names of attribute indicies. Parameter replacement can
    be one of 'mean' (works with numerics), 'mode' or 'median' --
    works with sortables, using multimode() in this module to pick
    the median most-frequent-value when there are more than one,
    unlike statistics.mode that chokes on that condition; median
    picks the central value in a sorted list, picking the one to the
    left in even-size non-numeric lists -- 'min' or 'max for sortable
    attributes, 'random' for a uniform float value between the min and the
    max of a numeric attribute, or a function supplied by the caller.
    When replacement is a function supplied by the caller, that function
    must take 3 arguments: The index i into the copy ndataset to be
    mutated for the current instance undergoing mutation, the index j
    of the attribute to be mutated within ndataset[i], and a reference
    to the entire copy of ndataset being mutated. A functional
    replacement is useful for deriving non-None values from other
    instance-attrubute-values in the dataset. imputeARFF does not
    sort dataset; call sortARFF before calling imputeARFF for a
    sorted dataset. For example, deriving time series attribute-values
    is possible by joining a None column onto a sorted-on-time dataset,
    and then imputing values into that None column.
    A functional replacement is called only when ndataset[i][j] is None,
    and should mutate only that ndataset[i][j] value; the replacement
    function's return value is not used.
    The seed parameter, when non-None, is for seeding 'random' replacement.
    imputeARFF's return value is a mutated copy of the incoming dataset;
    incoming dataset is not mutated.
    The return value of imputeARFF is the potentially mutated copy of dataset.
    '''
    # See also https://scikit-learn.org/stable/modules/classes.html#module-sklearn.impute
    if attributeKeys == None:
        akeys = list(range(0, len(attrmap.keys())))
    else:
        akeys = list(attributeKeys)
        for kix in range(0, len(attributeKeys)):
            k = attributeKeys[kix]
            if isinstance(k, str):
                if not k in attrmap.keys():
                    raise ValueError("INVALID ATTRIBUTE Name: " + k
                        + " in imputeARFF")
                akeys[kix] = attrmap[k][0]
            elif (not isinstance(k, int)) or k < 0 or k >= len(attrmap.keys()):
                raise ValueError("INVALID INTEGER ATTRIBUTE Index: " + str(k)
                    + " in imputeARFF")
            # else it is already a valid int
    ndata = copy.deepcopy(dataset)
    if isinstance(replacement, types.FunctionType) or           \
            isinstance(replacement, types.LambdaType):
        for instix in range(0, len(ndata)):
            for attrix in range(0, len(akeys)):
               if ndata[instix][akeys[attrix]] == None:
                   replacement(instix, akeys[attrix], ndata)
    elif not replacement in {'mean', 'median', 'mode', 'min', 'max', 'random'}:
        raise ValueError("INVALID replacement ARGUMENT: " + str(replacement)
            + " in imputeARFF")
    else:
        columns = [[] for i in range(0, len(akeys))]
        for inst in ndata:
            for attrix in range(0, len(akeys)):
                if inst[akeys[attrix]] != None:
                    columns[attrix].append(inst[akeys[attrix]])
        for cix in range(0, len(columns)):
            if len(columns[cix]) == 0:
                remp = remapAttributes(attrmap)
                dud = remp[columns[cix]][0]
                raise ValueError("INVALID ALL-UNKOWN ATTRIBUTE: "
                    + dud + " in imputeARFF")
        subvals = [None for i in range(0, len(columns))]
        randomgen = None
        if replacement == 'random':
            randomgen = random.Random()
            randomgen.seed(seed)
        for attrix in range(0, len(columns)):
            if replacement == 'mean':
                subvals[attrix] = mean(columns[attrix])
            elif replacement == 'median':
                subvals[attrix] = stringNumMedian(columns[attrix])
            elif replacement == 'mode':
                modeset = multimode(columns[attrix])
                subvals[attrix] = modeset[int(len(modeset)/2)]
            elif replacement == 'min':
                subvals[attrix] = min(columns[attrix])
            elif replacement == 'max':
                subvals[attrix] = max(columns[attrix])
            elif replacement == 'random':
                # Two-tuple for random range.
                subvals[attrix] = (min(columns[attrix]), max(columns[attrix]))
        for inst in ndata:
            for rix in range(0, len(akeys)):
                attrix = akeys[rix]
                if inst[attrix] == None:
                    sub = subvals[rix]
                    if isinstance(sub, tuple):
                        # print("DEBUG randrange", akeys[rix], sub[0], sub[1])
                        # sys.stdout.flush()
                        sub = randomgen.uniform(sub[0], sub[1])
                    inst[attrix] = sub
    return ndata

def ARFFtoCSV(attrmap, dataset):
    '''
    Return new ARFF data that is a conversion of nominal and date
    entries in attrmap and dataset into string entries,
    where attrmap is the map from attrname -> (offset, type) returned by
    __getAttrIndices__ as in readARFF & writeARFF, dataset is a 2D list
    indexed on [row][offset] that holds actual data instances.
    Return value is a 3-tuple (newattrmap, newdataset, newheader),
    in which newattrmap is a copy of attrmap with string replacing 
    nominal and date type tags, newdataset is a copy of dataset with
    strings replacing nominal and date values, and newheader is a list
    of string names for attributes (columns) in their correct attribute
    positions corresponding to attribute-value positions in the newdataset,
    suitable for a CSV header row.
    '''
    newattrmap = copy.deepcopy(attrmap)
    newdataset = copy.deepcopy(dataset)
    newheader = []
    offsetTOnameType = remapAttributes(attrmap)
    convertIndices = []
    for ix in range(0,len(offsetTOnameType)):
        NAME, TYPE = offsetTOnameType[ix]
        newheader.append(NAME)
        if isinstance(TYPE,tuple):
            basetype = TYPE[0]
            if basetype == 'nominal' or basetype == 'date':
                newattrmap[NAME] = (ix, 'string')
                convertIndices.append(ix)
            else:
                raise ValueError("INVALID NON-ATOMIC TYPE TAG: '"
                    + str(basetype) + "' in call to ARFFtoCSV")
    for inst in newdataset:
        for fldix in convertIndices:
            inst[fldix] = inst[fldix][0] if (inst[fldix] != None) else None
            # Use the string representation
    return (newattrmap, newdataset, newheader)

def multimode(valueList):
    '''
    Return the tuple of modes of valueList, where a mode is the most
    frequently occuring value using exact == comparisons, and there
    may be > 1 mode; in that case the return tuple will have multiple
    mode values in sorted order, else only 1 mode value. Changed name from
    mode in deference to statistics.mode.
    '''
    if not valueList:
        return []
    result = []
    counters = {}
    for v in valueList:
        if v in counters.keys():
            counters[v] = counters[v] + 1
        else:
            counters[v] = 1
    pairsToSort = []
    for k in counters.keys():
        t = (counters[k], k)    # We sort on the count as primary sort key.
        pairsToSort.append(t)
    pairsToSort.sort(reverse=True)
    # print("DEBUG pairsToSort", pairsToSort)
    max = pairsToSort[0][0]     # the max count
    for count, value in pairsToSort:
        if count == max:
            result.append(value)
        else:
            break
    result.sort()   # Ascending, non-reversed order.
    return tuple(result)

def stringNumMedian(valueList, mkey=None, mreverse=False):
    '''
    Return the median of valueList, where median is the center value
    after sorting a copy of valueList. If there are an even number of
    numeric elements, stringNumMedian returns the mean of the two central
    elements. Otherwise, any element type amenable to a sort may be in the
    valueList, and for non-numeric types with an even number of values,
    the lower value is returned. Note statistics.median cannot deal with
    an even number of non-numeric types. The mkey parameter is the same as
    Python 3 sort()'s key, likewise mreverse for reverse.
    '''
    try:
        vl = copy.copy(valueList)
        vl.sort(key=mkey, reverse=mreverse)
        if ((len(vl) & 1) == 1):        # odd number of elements
            return vl[int(len(vl) / 2)]
        upper = int(len(vl) / 2)
        if vl[upper-1] == vl[upper]:
            return vl[upper]
        sum = vl[upper-1] + vl[upper]
        floater = sum / 2.0
        return floater
    except TypeError:
        # sys.stderr.write('TYPE WARNING, call to median for list: '
            # + str(v1) + ', returning lower element\n')
        return vl[int(len(vl) / 2)] # non-numeric, return the lower

def kappa(confusionMatrix): # 2D list of lists, each sublist is a row
    '''
    Compute the Kappa statistic of a confusion matrix.
    Param confusionMatrix is 2D list of lists, each sublist is a row
    Each row shows the actual class. Each column shows the predicted class.
    That row (actual), column (predicted is same as Weka. Also see
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html
    Return value is a 5-tuple:
        (kappa %correct numberCorrect %incorrect numberIncorrect)
    '''
    sumRows = [0.0 for i in range(0,len(confusionMatrix))]
    sumColumns = [0.0 for i in range(0,len(confusionMatrix))]
    sumOfWeights = 0.0
    numberCorrect = 0                   # added March 2020
    numberIncorrect = 0                 # added March 2020
    for i in range(0, len(confusionMatrix)):
        for j in range(0, len(confusionMatrix)):
            sumRows[i] += confusionMatrix[i][j]
            sumColumns[j] += confusionMatrix[i][j];
            sumOfWeights += confusionMatrix[i][j];
            if (i == j):
                numberCorrect += confusionMatrix[i][j]
            else:
                numberIncorrect += confusionMatrix[i][j]
    correct = 0.0
    chanceAgreement = 0.0
    # DEBUGchanceAgreement = 0.0 # Added by Parson for figuring this out.
    for i in range(0, len(confusionMatrix)):
        # sumRows[i] gives sum that should have been classified as class i
        # sumColumns[i] sum that were classified as i (maybe some wrong)
        # This squares the correct diagonal classification terms.
        # Other terms are sums of incorrectly swapped classes, e.g.,
        # (in class a but classified as b * in class b but classified as a)
        chanceAgreement += (sumRows[i] * sumColumns[i])
        correct += confusionMatrix[i][i] # predicted == correct on diagonal
        # if sumRows[i] > DEBUGchanceAgreement:
            # DEBUGchanceAgreement = sumRows[i]
    chanceAgreement /= (sumOfWeights * sumOfWeights)
    correct /= sumOfWeights
    # DEBUGchanceAgreement /= sumOfWeights
    # for row in confusionMatrix:
        # for datum in row:
            # sys.stdout.write(str(datum) + ",\t")
        # sys.stdout.write('\n')
    # print("chanceAgreement:",chanceAgreement,"ZeroR",DEBUGchanceAgreement)
    # print("correct: ", correct)
    kappaResult = 0.0
    if (chanceAgreement < 1):
        # This is the actual formula:
        # Kappa = (observed accuracy - expected accuracy)
            # / (1 - expected accuracy)
        kappaResult = (correct - chanceAgreement) / (1 - chanceAgreement)
    else:
        kappaResult = 1.0
    # Fractions require sumOfWeights being a float.
    return(kappaResult, numberCorrect/sumOfWeights, numberCorrect,
        numberIncorrect/sumOfWeights, numberIncorrect)

__mapStringTypeToPyType__ = {
    "string"        :   str,
    "numeric"       :   float,
    "nominal"       :   set
    # TODO: datetime
}
__mapPyTypeToStringType = {
    str             :   "string",
    float           :   "numeric",
    set             :   "nominal"
    # TODO: datetime
}

def __helpfilter__(inAttributes, inInstances, attributeListToFilter,
        fromTypeName, toTypeConverterFunction):
    # fromTypeName is like "string" "numeric" or "set"
    fromTypePy = __mapStringTypeToPyType__[fromTypeName]
    if not attributeListToFilter:
        attributeListToFilter = []  # must be a sequence
        myattrnames = list(inAttributes.keys())
    elif type(attributeListToFilter) == str:        # name of 1 attribute
        attributeListToFilter = [attributeListToFilter]
        myattrnames = attributeListToFilter
    else:
        myattrnames = attributeListToFilter
    outAttributes = copy.deepcopy(inAttributes)
    outInstances = list(copy.deepcopy(inInstances)) # must be mutable
    for aname in myattrnames:
        atype = outAttributes[aname]
        if atype[1] != fromTypeName:
            if aname in attributeListToFilter:
                raise TypeError("Invalid " + fromTypeName
                    + " filter attribute: " + aname + ": " + str(atype))
            continue
        # It is the correct type, so collect up the range of values.
        aindex = int(atype[0])
        values = []
        for inst in outInstances:
            values.append(inst[aindex])
        # Note iterated mutation of outAttributes & outInstances
        outAttributes, outInstances = toTypeConverterFunction(outAttributes,
            outInstances, aname, aindex, values)
    return (outAttributes, outInstances)

def StringToNominal(inAttributes, inInstances, attributeListToFilter=[]):
    '''
    StringToNominal accepts an attributes map "inAttributes" as returned
    by readARFF, and an instances sequence of sequences (lists or tuples,
    where each inner sequence is an instance of data values, 1 per element,
    as specified by inAttributes) as returned by readARFF, and returns
    a new, non-mutated (outAttributes, outInstances) dataset with the
    strings converted to nominals. Parameter attributeListToFilter when
    non-None and non-empty is a list or tuple of attribute names to
    convert; otherwise, StringToNominal runs on every string attribute.
    '''
    def __strToNomConverter__(outAttributes, outInstances,
            aname, aindex, values):
        # outAttributes is a deepcopy of inAttributes
        # outInstances is a deepcopy of Instances
        # aname is the attribute name for type declaration update
        # aindex is its index in each instance
        # values is the per-instance attribute-value list, in original order
        values = set(values)
        setstring = "{"
        liststring = []
        prefix = ''
        for v in values:        # nominal & string values in data look same
            # this loop is for the type decl.
            setstring += prefix + quoteStringIfNeeded(v)
            liststring.append(v)
            prefix = ','
        setstring += "}"
        outAttributes[aname] = (aindex, ('nominal', setstring, liststring))
        return (outAttributes, outInstances)
    outAttributes, outInstances = __helpfilter__(inAttributes, inInstances,
        attributeListToFilter, "string", __strToNomConverter__)
    return (outAttributes, outInstances)

def Normalize(inAttributes, inInstances, attributeListToFilter=[],
        multiplier=1.0):
    '''
    Normalize accepts an attributes map "inAttributes" as returned
    by readARFF, and an instances sequence of sequences (lists or tuples,
    where each inner sequence is an instance of data values, 1 per element,
    as specified by inAttributes) as returned by readARFF, and returns
    a new, non-mutated (outAttributes, outInstances) dataset with the
    numerics converted to normalized numerics in the range [0.0, 1.0].
    Parameter attributeListToFilter when non-None and non-empty is a list
    or tuple of attribute names to convert; otherwise, Normalize runs on
    every numeric attribute. multiplier != 0.0 added 10/4/2020, used
    to scale [0.0, 1.0] default range, defaults to 1.0.
    '''
    # print("DEBUG Normalize ats:", attributeListToFilter); sys.stdout.flush()
    # sys.stderr.write("DEBUG Normalize ats: " + str(attributeListToFilter) + '\n'); sys.stderr.flush()
    def __numericNormalizer__(outAttributes, outInstances,
            aname, aindex, values):
        # outAttributes is a deepcopy of inAttributes
        # outInstances is a deepcopy of Instances
        # aname is the attribute name for type declaration update
        # aindex is its index in each instance
        # values is the per-instance attribute-value list, in original order
        #print("DEBUG ENTER __numericNormalizer__ aname", aname, type(outInstances))
#       min = values[0]
#       max = values[0]
#       for v in values:
#           if v < min:
#               min = v
#           if v > max:
#               max = v
#       min = float(min)
#       max = float(max)
#       numrange = max-min
        # RECODED 7/21/2022 to pass over None values
        min = None
        max = None
        numrange = None
        vix = 0
        while vix < len(values):
            v = values[vix]
            if v != None and not (isinstance(v,float) and numpy.isnan(v)):
                if min == None or v < min:
                    min = v
                if max == None or v > max:
                     max = v
            vix += 1
        if min != None and max != None:
            min = float(min)
            max = float(max)
            numrange = max-min
        if min != None and numrange > 0.0:
            for instix in range(0, len(outInstances)):
                if outInstances[instix][aindex] != None:
                    outInstances[instix][aindex] = round(multiplier *
                        ((outInstances[instix][aindex] - min) / numrange),6)
        elif min != None:
            for instix in range(0, len(outInstances)):
                if outInstances[instix][aindex] != None:
                    outInstances[instix][aindex] = 0.0
        return (outAttributes, outInstances)

    if math.isclose(multiplier,0.0,rel_tol=0.0001, abs_tol=0.000001):
        raise ValueError(
            "Normalize requires numeric multiplier != 0: " + str(multiplier))
    outAttributes, outInstances = __helpfilter__(inAttributes, inInstances,
        attributeListToFilter, "numeric", __numericNormalizer__)
    # print("DEBUG NORMALIZE RETURNS LEN", len(outInstances))
    return (outAttributes, outInstances)

def wekaCorrelationCoefficent(numericList1, numericList2):
    '''
    PARSON NOTE http://faculty.kutztown.edu/parson/fall2017/WekaChapter5.pptx
    Slides on Minimum Description Length and Evaluating Numeric Prediction,
    for the week of November 6, 2019 in preparation for Assignment 3.
    Read Sections 5.8 and 5.9 in the 3rd Edition textbook, 5.9 and 5.10 in the
    4th Edition, on Evaluating Numeric Prediction and the Minimum Description
    Length principle.
    http://faculty.kutztown.edu/parson/fall2017/CSC458EvalNumericPrediction.ppt
    Following from slide 11, essentially same result as scipy.stats.pearsonr
    '''
    def sqr(v):
        return v * v
    if len(numericList1) != len(numericList1):
        raise ValueError("Mismatched wekaCorrelationCoefficent arg lengths: "
            + str(len(numericList1)) + "," + str(len(numericList2)))
    mean_numericList1 = numpy.mean(numericList1)
    mean_numericList2 = numpy.mean(numericList2)
    # print("DEBUG mean_numericList[12]", type(mean_numericList1), type(mean_numericList2))
    sumdiff_numericList1 = 0.0
    sumdiff_numericList2 = 0.0
    sumdiff_products = 0.0
    n = len(numericList1)
    for i in range(0, n):
        v1 = numericList1[i]
        v2 = numericList2[i]
        sumdiff_numericList1 += sqr(v1 - mean_numericList1)
        # if (not isinstance(sumdiff_numericList1, float)):
            # print("DEBUG CAUGHT",v1,type(v1),mean_numericList1, type(mean_numericList1))
            # sys.exit(0)
        sumdiff_numericList2 += sqr(v2 - mean_numericList2)
        sumdiff_products += (v1 - mean_numericList1) * (v2 - mean_numericList2)
    # print("DEBUG sumdiffs", type(sumdiff_numericList1), type(sumdiff_numericList2), type(sumdiff_products))
    avg_sumdiff_products = sumdiff_products / (n-1.0)
    avg_sumdiff_numericList1 = sumdiff_numericList1 / (n-1.0)
    avg_sumdiff_numericList2 = sumdiff_numericList2 / (n-1.0)
    divisor = math.sqrt(avg_sumdiff_numericList1 * avg_sumdiff_numericList2)
    if divisor == 0.0:
        CorrelationCoefficent = 0
    else:
        CorrelationCoefficent = avg_sumdiff_products / divisor
    # print("DEBUG wekaCorrelationCoefficent", CorrelationCoefficent, type(CorrelationCoefficent), type(avg_sumdiff_products), type(divisor))
    return CorrelationCoefficent


def DEBUGNonesARFF(attrmap, dataset, outfile=sys.stderr):
    '''
    Print to outfile statistics on number of unknown (None)
    attribute-values per attribute name,
    where attrmap is the map from attrname -> (offset, type)
    returned by __getAttrIndices__ as in readARFF & writeARFF, and
    dataset is a 2D list indexed on [row][offset] that holds actual
    data instances.
    '''
    for attrdebug in attrmap.keys():
        index = attrmap[attrdebug][0]
        count = 0
        for inst in dataset:
            if inst[index] == None:
                count += 1
        outfile.write("DEBUG OUT OF " + str(len(dataset))
            + " INSTANCES ATTRIBUTE " + attrdebug + " ATTRIX "
            + str(index) + " NONES= " + str(count) + '\n')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write("USAGE: python arfflib.py INARFFFILE OUTARFFFILE\n")
        sys.exit(1)
    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    if os.path.exists(outfilename):
        sys.stderr.write("ERROR, file " + outfilename + " currently exists.\n")
        sys.exit(2)
    attrmap, dataset = readARFF(infilename)
    writeARFF(outfilename, attrmap, dataset, isDebugMode=False)
