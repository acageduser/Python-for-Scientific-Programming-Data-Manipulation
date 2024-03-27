# diffcsv.py, Fall 2023 D. Parson
# takes into account minor decimal differences in CSV
# numeric fields due to Python's tendency to take repeating fractions
# out to the end. Derived from diffarff.py, D. Parson, October 2020.
# diffcsv.py does an attribute-by-attribute and value-by-value comparison
# based on string and "almost-equals" numeric comparisons, rather than the
# character-based comparisons of the Unix "diff" utility.
from arfflib_3_3 import readCSV # Like CSV reader but does numeric inference
# readCSV Return value is a 6-tuple (attrmap, dataset, CSVheaderRow,
#       nameToCol, colToName, colToType),
from arfflib_3_3 import remapAttributes
import subprocess
import sys
from math import log10, floor, isclose       # for float almost-equals

__USAGE__ =                                                             \
'USAGE: python diffcsv.py leftfileCSVfile rightfileCSVfile '         \
    + '[ rel_tol=N.n, abs_tol=N.n ],\nwhere optional rel_tol is a '   \
    + 'fractional percentage such as .0001 for .01% tolerance,\n'     \
    + 'and abs_tol is a small-value absolute tolerance such as .000001' \
    + ' for 10**-6,\nfor floating point data comparisons.\n'
if __name__ == '__main__':
    iserror = False
    if len(sys.argv) != 3 and len(sys.argv) != 5:
        raise ValueError(__USAGE__)
    myrel_tol=0.0001
    myabs_tol=0.000001
    if len(sys.argv) == 5:
        if not (sys.argv[3].startswith('rel_tol=')
                and sys.argv[4].startswith('abs_tol=')):
            sys.stderr.write(__USAGE__)
            sys.exit(1)
        myrel_tol = float(sys.argv[3][8:])
        myabs_tol = float(sys.argv[4][8:])
    leftfile = sys.argv[1]
    rightfile = sys.argv[2]
    leftattrs, leftdata, CSVheaderRow, nameToCol, colToName, colToType  \
        = readCSV(leftfile)
    rightattrs, rightdata, CSVheaderRow, nameToCol, colToName, colToType  \
        = readCSV(rightfile)
    # rightattrs, rightdata = readCSV(rightfile)
    if len(leftattrs.keys()) != len(rightattrs.keys()):
        iserror = True
        sys.stderr.write('ERROR, file ' + leftfile + " has "
            + str(len(leftattrs.keys())) + " attributes, file " + rightfile
            + str(len(leftattrs.keys())) + " keys.\n")
    if len(leftdata) != len(rightdata):
        iserror = True
        sys.stderr.write('ERROR, file ' + leftfile + " has "
            + str(len(leftdata)) + " instances, file " + rightfile
            + str(len(rightdata)) + " instances.\n")
    leftremap = remapAttributes(leftattrs)
    rightremap = remapAttributes(rightattrs)
    for i in range(0, len(leftattrs.keys())):
        if leftremap[i][0] != rightremap[i][0]:
            iserror = True
            sys.stderr.write('ERROR, file ' + leftfile + " has attribute "
                + leftremap[i][0] + " at position " + str(i+1) + ", "
                + rightfile + " has attribute " + rightremap[i][0] + '\n')
        elif leftremap[i][1] != rightremap[i][1]:
            iserror = True
            sys.stderr.write('ERROR, file ' + leftfile + " has attribute "
                + leftremap[i][0] + " TYPE " + str(leftremap[i][1])
                + " at position " + str(i+1) + ", "
                + rightfile + " has TYPE " + str(rightremap[i][1]) + '\n')
    for instix in range(0, len(rightdata)):
        linst = leftdata[instix]
        rinst = rightdata[instix]
        if len(linst) != len(rinst):
            iserror = True
            sys.stderr.write('ERROR, file ' + leftfile + ", left instance "
                + str(instix+1) + " has " + str(len(linst)) + "columns, "
                + " file " + rightfile + " has " + str(len(rinst)) + "columns:"
                + '\n< ' + str(linst) + '\n> ' + str(rinst) + '\n')
        for fix in range(0, len(linst)):
            if (linst[fix] != rinst[fix]):
                if (leftremap[fix][1] != 'numeric'):
                    iserror = True
                    sys.stderr.write('ERROR, file ' + leftfile
                        + ", left instance "
                        + str(instix+1) +  " field " + str(fix+1) + " has "
                        + str(linst[fix])
                        + " file " + rightfile + " has " + str(rinst[fix])
                        + '\n< ' + str(linst) + '\n> ' + str(rinst) + '\n')
                    continue
                # intleft = floor(log10(abs(linst[fix]))) + 1
                # intright = floor(log10(abs(rinst[fix]))) + 1
                # normleft = round(linst[fix] * (10 ** intleft), 5)
                # normright = round(rinst[fix] * (10 ** intright), 5)
                # if (intleft != intright) or (normright != normright):
                # if abs(intleft-intright) > 1 or (normright != normright):
                # if round(linst[fix], 6) != round(rinst[fix], 6):
                # isclose(a, b, *, rel_tol=1e-09, abs_tol=0.0)
                # Determine whether two floating point numbers are close
                #   in value.
                # rel_tol
                #   maximum difference for being considered "close",
                #   relative to the magnitude of the input values
                # if not isclose(linst[fix], rinst[fix], rel_tol=1e-10):
                if not isclose(linst[fix], rinst[fix],
                        rel_tol=myrel_tol, abs_tol=myabs_tol):
                        # .01% difference is OK, abs diff <= 0.000001 OK
                    iserror = True
                    sys.stderr.write('ERROR, file ' + leftfile
                        + ", left instance "
                        + str(instix+1) +  " field " + str(fix+1) + " has "
                        + str(linst[fix])
                        + " file " + rightfile + " has " + str(rinst[fix])
                        + '\n< ' + str(linst) + '\n> ' + str(rinst) + '\n')
                    # print("DEBUG FGUARDS",intleft,intright,normright,normright)
                    # sys.exit(1)
    if iserror:
        diffname = leftfile.split('/')[-1].strip()
        diffstat = subprocess.call("/bin/diff "
            + leftfile + " " + rightfile + " > "  + diffname + '.dif',
                shell=True)
        sys.stderr.write("See ERROR DETAILS IN " + diffname + '.dif\n')
        sys.exit(1)
    sys.stderr.write("FILES " + leftfile + "," + rightfile + " OK.\n")
    sys.exit(0)
