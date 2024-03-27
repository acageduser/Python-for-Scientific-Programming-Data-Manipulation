# plotcsv.py D. Parson April 2022, revised July 2022 for subplots,
# i.e., multiple attributes plotted to Y. Also 'norm" on command line
# causes normalization of all Y values. Added -file for PNG out 8/18/2022.

# plotcsv_1_2.py 9/15/2022 added NAME option to -file:NAME to plot
# to an explicit file. Started numbering plotcsv at 1_2.
# plotcsv_1_3 accepts .arff and arff.gz files as input.

import sys
import numpy as np
import matplotlib.pyplot as plt
import csv
import statistics as stats
from arfflib_3_3 import readCSV, readARFF, ARFFhdr2CSVhdr, CSVhdr2ARFFhdr
import copy
import math
import types
import subprocess   # For moving -file PNG to ~/public_html
import os           # likewise

color = ['red', 'blue', 'green', 'black', 'cyan', 'magenta']
style = ['solid', 'dashed', 'dashdot', 'dotted']

def __findSlope__(Ylist, xlength):
    # Compute the slope across midpoints of a line graph for plotting.
    result = [None for i in range(0, len(Ylist))]
    startix = 0
    while startix < len(Ylist) and Ylist[startix] == None:  # skip leading Nones
        startix += 1
    lastmeasure = []
    lastmid = None
    for startix in range(startix, len(Ylist)):
        # if lastmid != None:
        if len(lastmeasure) > 0 and Ylist[startix] != None:
            lastmeasure.insert(0, Ylist[startix])
            if len(lastmeasure) > xlength:
                lastmeasure = lastmeasure[0:xlength]
            lastmid = round(stats.mean(lastmeasure),6)
        elif Ylist[startix] != None:        # start lastmeasure at len==1
            lastmeasure.insert(0, Ylist[startix])
        result[startix] = lastmid   # Just use most recent midpoint
    # sys.stderr.write("DEBUG __findSlope__\n" + str(Ylist) + "\n" + str(result) + '\n')
    # sys.stderr.flush()
    return result

def __findSmooth__(Ylist, currentWeight):
    # A rolling average of current Y and previous average.
    result = [None for i in range(0, len(Ylist))]
    previousEstimate = None
    for index in range(0, len(Ylist)):
        yval = Ylist[index]
        if yval == None:
            # result[index] = None
            result[index] = previousEstimate
        elif previousEstimate == None:
            result[index] = yval
        else:
            result[index] = currentWeight * yval                    \
                + (1.0-currentWeight) * previousEstimate
        previousEstimate = result[index] 
    return result

__PLOTFILE__ = 'plotcsv.png'    # default, override -file:NAME
def saveFig(plotObject):    # plotObject is like plt or fig
    myDPI = 300
    # plotObject.figure(figsize=(int(1920/myDPI),int(1080/myDPI)), dpi=myDPI)
    plotObject.savefig(__PLOTFILE__, dpi=myDPI)
    HOME = os.environ['HOME']
    PUBHTML = HOME + '/public_html'
    if not os.path.lexists(PUBHTML):
        sys.stderr.write('ERROR, ~/public_html/ is missing, '
            + 'from your login directory do this: \n\t'
            + 'mkdir public_html && chmod +r+x public_html')
    cmdline = 'chmod +r ' + __PLOTFILE__ + ' && /bin/cp '   \
        + __PLOTFILE__ + ' ' + PUBHTML + '/' + __PLOTFILE__
    p = subprocess.Popen(cmdline, shell=True, stderr=sys.stderr)
    if p.wait() != 0:
        sys.stderr.write('ERROR in copying ' + __PLOTFILE__
            + ' to ~/public_html\n')
    else:
        who = os.environ['USER']
        print('BROWSE https://acad.kutztown.edu/~' + who + '/'
            + __PLOTFILE__)

__usage__ =                                 \
    'USAGE: python plotcsv.py CSVorARFF (XCOL "norm?-nolines"? -file[:NAME]? YCOL...1to7) | YHIST\n' \
    + '\tOPTIONAL slope_N smooth_.N log_N pow_N lambda after any YCOL name\n'  \
    + '\twhere Y is X columns to average and N is a log base or pow power.'
if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write(__usage__ + '\n')
        sys.exit(1)
    arffdict, table, CSVheader, nameToCol, colToName, colToType = 	\
	    [None, None, None, None, None, None]
    infname = sys.argv[1].strip()
    if infname.endswith('.arff') or infname.endswith('.arff.gz'):
        arffdict, table = readARFF(infname)
        copy1dict = {}
        # Added error check logic for ARFFhdr2CSVhdr, CSVhdr2ARFFhdr as
        # added to arfflib 4/30/2022
        for nm in arffdict.keys():
            # CSV doesn't do nominals or datetime.
            t2 = arffdict[nm]
            typetag = t2[1]
            if (isinstance(typetag, tuple) and len(typetag) > 0
                            and (typetag[0] == 'nominal'
                                or typetag[0] == 'date')):
                copy1dict[nm] = (t2[0], 'string')
            else:
                copy1dict[nm] = t2
        arffdict= copy1dict
        CSVheader, nameToCol, colToName, colToType = ARFFhdr2CSVhdr(arffdict)
        # Test new April 30, 2022 CSV/ARFF header conversion functions.
        copy2dict = CSVhdr2ARFFhdr(CSVheader, nameToCol, colToName, colToType)
        if copy1dict != copy2dict:
            raise ValueError('ERROR, bug in ARFFhdr2CSVhdr or CSVhdr2ARFFhdr\n'
                + '\t' + str(copy1dict) + '\n\t' + str(copy2dict))
    else:
        arffdict, table, CSVheader, nameToCol, colToName, colToType = readCSV(
            infname, isUsingNan=True)
    if (sys.argv[2].startswith('(') and sys.argv[2].endswith(')')
            and ',' in sys.argv[2]):
        # composite sort key as tuple added 7/12/2022
        attrlist = sys.argv[2][1:-1].strip().split(',')
        attrlist = [e.strip() for e in attrlist if len(e.strip()) > 0]
        memberCols = []
        for a in attrlist:
            try:
                xcol = int(a)
            except ValueError:
                xcol = nameToCol[a]
            memberCols.append(xcol)
        attrname = sys.argv[2][1:-1].strip().replace(' ','')
        lastcol = len(nameToCol.keys())
        arffdict[attrname] = (lastcol, 'string')
        CSVheader.append(attrname)
        nameToCol[attrname] = lastcol
        colToName[lastcol] = attrname
        colToType[lastcol] = str
        # Two passes over the instances, one to sort, one to turn tuples to str.
        for row in table:
            t = []
            for m in memberCols:
                t.append(row[m])
            row.append(tuple(t))
        def keyt(row): return row[lastcol]
        table.sort(key=keyt)
        for row in table:
            row[lastcol] = str(row[lastcol])
        x = [row[lastcol] for row in table]
        xcol = lastcol
    else:   # scalar X column key
        try:
            xcol = int(sys.argv[2])
        except ValueError:
            xcol = nameToCol[sys.argv[2]]
        for row in table:
            for colix in range(0, len(row)):
                if isinstance(row[colix], tuple):
                    row[colix] = row[colix][0]      # get string
        def InputSortKey(row): return row[xcol][1]                  \
            if isinstance(row[xcol], tuple)  \
                else (row[xcol] if (isinstance(row[xcol],int)
                    or isinstance(row[xcol],str)
                    or (isinstance(row[xcol],float)
                and not np.isnan(row[xcol]))) else None)
        table.sort(key=InputSortKey)
        x = [row[xcol] for row in table]
    xsmall = []
    for v in x:
        if isinstance(v, str) and (" 00:00:00" in v):
            space = v.rindex(' ')
            if v[0].isdigit():
                v = v[0:space]
            else:
                v = v[1:space]
            xsmall.append(v)
            # print("CHOPPED", xsmall[-1])
        elif v == None:
            xsmall.append(None)
        else:
            # print("FAIL v", v)
            break
    if len(xsmall) == len(x):
        x = xsmall
    print("DEBUG X TYPE", type(x[0]), x[0])
    genFile = False
    if len(sys.argv) >= 4:	# Use a single column for histogram later.
        def bailout(yindex):
            sys.stderr.write(
                'ERROR, insufficient cmd line data after '
                    + str(sys.argv[yindex-1:]) + '\n')
            sys.stderr.write(__usage__ + '\n')
            sys.exit(1)
        normalizing = False
        nolines = False
        ##? try:
            ##? xcol = int(sys.argv[2])
        ##? except ValueError:
            ##? xcol = nameToCol[sys.argv[2]]
        ##? x = [row[xcol] for row in table]
        yindex = 3
        if 'nolines' in sys.argv[yindex]:
            nolines = True
            if not 'norm' in sys.argv[yindex]:
                yindex += 1
                if yindex == len(sys.argv):
                    bailout(yindex)
        if 'norm' in sys.argv[yindex]:
            normalizing = True
            yindex += 1
            if yindex == len(sys.argv):
                bailout(yindex)
        if sys.argv[yindex].startswith('-file'):
            print("DEBUG FLIPPED genFile True")
            genFile = True
            if ':' in sys.argv[yindex]:
                colonix = sys.argv[yindex].index(':')
                __PLOTFILE__ = sys.argv[yindex][colonix+1:]
            yindex += 1
            if yindex == len(sys.argv):
                bailout(yindex)
        ylines = []
        ylabels = []
        yUpperMost = None
        yLowerMost = None
        isYslope = []     # For displaying long-term slopes when requested.
        yPredecessor = False
        while yindex < len(sys.argv):
            # slope_N option added 7/5/2022, changed to averages midpoints 7/12
            if sys.argv[yindex].startswith('slope_'):
                if not yPredecessor:
                    sys.stderr.write('ERROR: ' + sys.argv[yindex]
                        + ' cmd line arg without preceding attribute name'
                        + 'ignored.\n')
                    yindex += 1
                    continue
                try:
                    slopeLength = int(sys.argv[yindex][len('slope_'):])
                except ValueError:
                    slopeLength = -1
                if slopeLength < 2:
                    sys.stderr.write('ERROR: ' + sys.argv[yindex]
                        + ' invalid slope_VALUE must be int >= 2, ignored.\n')
                    yindex += 1
                    continue
                y = __findSlope__(ylines[-1], slopeLength)
                ylines.append(y)
                isYslope.append(True)
                ylabels.append(sys.argv[yindex-1] + ' ' + sys.argv[yindex])
                yPredecessor = False
                yindex += 1
                continue
            # smooth_ option added 7/5/2022
            if sys.argv[yindex].startswith('smooth_'):
                if not yPredecessor:
                    sys.stderr.write('ERROR: ' + sys.argv[yindex]
                        + ' cmd line arg without preceding attribute name'
                        + 'ignored.\n')
                    yindex += 1
                    continue
                try:
                    smoothFraction = float(sys.argv[yindex][len('smooth_'):])
                except ValueError:
                    smoothFraction = -1
                if smoothFraction < 0.0 or smoothFraction > 1.0:
                    sys.stderr.write('ERROR: ' + sys.argv[yindex]
                        + ' invalid smooth_VALUE must be float >= 0.0 and <= '
                        + ' 1.0 , ignored.\n')
                    yindex += 1
                    continue
                y = __findSmooth__(ylines[-1], smoothFraction)
                ylines.append(y)
                isYslope.append(True)
                ylabels.append(sys.argv[yindex-1] + ' ' + sys.argv[yindex])
                yPredecessor = False
                yindex += 1
                continue
            # log_N option added 7/5/2022, it modifies the preceding line with its log
            if sys.argv[yindex].startswith('log_'):
                if not yPredecessor:
                    sys.stderr.write('ERROR: ' + sys.argv[yindex]
                        + ' cmd line arg without preceding attribute name'
                        + 'ignored.\n')
                    yindex += 1
                    continue
                try:
                    logBase = float(sys.argv[yindex][len('log_'):])
                except ValueError:
                    logBase = -1
                if logBase <= 0:
                    sys.stderr.write('ERROR: ' + sys.argv[yindex]
                        + ' invalid log_VALUE must be float > 0.0, ignored.\n')
                    yindex += 1
                    continue
                for yix in range(0, len(ylines[-1])):
                    try:
                        ylines[-1][yix] = math.log(ylines[-1][yix], logBase)
                    except Exception as oops:
                         print("DEBUG LOG", oops)
                         ylines[-1][yix] = None
                ylabels[-1] = ylabels[-1] + ' ' + sys.argv[yindex]
                # yPredecessor = False
                yindex += 1
                continue
            # pow_N option added 7/5/2022, it modifies the preceding line with its pow
            if sys.argv[yindex].startswith('pow_'):
                if not yPredecessor:
                    sys.stderr.write('ERROR: ' + sys.argv[yindex]
                        + ' cmd line arg without preceding attribute name'
                        + 'ignored.\n')
                    yindex += 1
                    continue
                try:
                    powBase = float(sys.argv[yindex][len('pow_'):])
                except ValueError:
                    sys.stderr.write('ERROR: ' + sys.argv[yindex]
                        + ' invalid pow_VALUE must be float, ignored: '
                        + '"' + sys.argv[yindex][len('pow_'):] + '"\n')
                    yindex += 1
                    continue
                for yix in range(0, len(ylines[-1])):
                    try:
                        ylines[-1][yix] = math.pow(ylines[-1][yix], powBase)
                    except Exception as oops:
                         # print("DEBUG POW", oops)
                         ylines[-1][yix] = None
                ylabels[-1] = ylabels[-1] + ' ' + sys.argv[yindex]
                # yPredecessor = False
                yindex += 1
                continue
            # lambda added 7/5/2022, modifies preceding line with lambda application
            if sys.argv[yindex].startswith('lambda'):
                if not yPredecessor:
                    sys.stderr.write('ERROR: ' + sys.argv[yindex]
                        + ' cmd line arg without preceding attribute name'
                        + 'ignored.\n')
                    yindex += 1
                    continue
                func = eval(sys.argv[yindex])
                if not isinstance(func,types.FunctionType):
                    sys.stderr.write('ERROR: ' + sys.argv[yindex]
                        + ' cmd line lambda arg is not a function'
                        + ', ignored.\n')
                    sys.stderr.flush()
                    yindex += 1
                    continue
                for yix in range(0, len(ylines[-1])):
                    try:
                        ylines[-1][yix] = func(ylines[-1][yix])
                    except Exception as oops:
                         print("DEBUG LAMBDA", oops)
                         ylines[-1][yix] = None
                ylabels[-1] = ylabels[-1] + ' ' + sys.argv[yindex]
                # yPredecessor = False
                yindex += 1
                continue
            try:
                ycol = int(sys.argv[yindex])
            except ValueError:
                ycol = nameToCol[sys.argv[yindex]]
            y = [row[ycol] for row in table]
            # filter messes up X to Y pairing; plt shows blank for None
            # However, filter needed for min & max when normalizing!!!
            yfilt = list(filter((lambda n : isinstance(n,int)
                    or (isinstance(n,float)) and not np.isnan(n)), y))
            ymax = max(yfilt)
            ymin = min(yfilt)
            # Adding log_N and pow_N transforms requires waiting for these:
            # if yUpperMost == None or ymax > yUpperMost:
                # yUpperMost = ymax
            # if yLowerMost == None or ymin < yLowerMost:
                # yLowerMost = ymin
            if normalizing:
                ynorm = [(None if (yval == None)
                    else (0 if (ymin == ymax)
                    else (round((yval-ymin)/(ymax-ymin),6))))
                    for yval in y]
                y = ynorm
                # yUpperMost = 1.0
                # yLowerMost = 0.0
                padsize = (len(sys.argv[yindex]) % 4) + 1
                padstr = ''
                for i in range(0, padsize):
                    padstr = padstr + ' '
                ylabels.append(sys.argv[yindex] + padstr + 'normalized ['
                    + str(round(ymin,4)) + ' , ' + str(round(ymax,4)) + '] ')
            else:
                ylabels.append(sys.argv[yindex])
            ylines.append(y)
            isYslope.append(False)
            yPredecessor = True
            yindex += 1
        print('X is',colToName[xcol],'Type is',colToType[xcol])
        titl = ''
        if colToType[xcol] == float:
            safex = list(filter(
                lambda n : isinstance(n,int) or (isinstance(n,float))
                    and not np.isnan(n), x))
            titl = ("MEAN " + str(stats.mean(safex)) + "     MEDIAN "
                + str(+ stats.median(safex)) + "     PSTDEV "
                + str(stats.pstdev(safex))
                + "     MIN " + str(min(safex)) + "     MAX " + str(max(safex)))
            print('\t', titl)
        print('Y is',colToName[ycol],'Type is',colToType[ycol])
        titl = ''
#       if colToType[ycol] == float:
#           safey = list(filter(
#               (lambda n : isinstance(n,int) or (isinstance(n,float))
#                   and not np.isnan(n)), y))
#           # STATS functions do not like filter's iterator!
#           # print("DEBUG safey", safey)
#           titl = ("MEAN " + str(stats.mean(safey)) + "     MEDIAN "
#               + str(stats.median(safey)) + "     PSTDEV "
#               + str(stats.pstdev(safey))
#               + "     MIN " + str(min(safey)) + "     MAX " + str(max(safey)))
#           print('\t', titl)
#           plt.title(titl)
        # plt.plot(x,y)
        fig, ax = plt.subplots()
        colix = 0
        styleix = 0
        yLowerMost = None
        yUpperMost = None
        for yindex in range(0, len(ylines)):
            yln = ylines[yindex]
            ylbl = ylabels[yindex]
            if isYslope[yindex]:
                ax.plot(yln, color=color[colix], label=ylbl,
                    linewidth=3, linestyle='dashed')
            else:
                ax.plot(yln, color=color[colix], label=ylbl,
                    linestyle=style[styleix])
            colix = colix+1 % len(color)
            if colix >= len(color):
                colix = 0
                styleix = (styleix+1) % len(style)
            # Now compute yLowerMost, yUpperMost for vertical lines
            yfilt = list(filter((lambda n : isinstance(n,int)
                    or (isinstance(n,float)) and not np.isnan(n)), yln))
            if len(yfilt) > 0:
                filtmin = min(yfilt)
                filtmax = max(yfilt)
                if yLowerMost == None or yLowerMost > filtmin:
                    yLowerMost = filtmin
                if yUpperMost == None or yUpperMost < filtmax:
                    yUpperMost = filtmax
        leg = ax.legend()
        # x labels are too dense, chop down to 10ish spaced by number of labels
        # plt.xticks([i for i in range(0, len(x), int(len(x)/10))])
        # plt.xticks([i for i in range(0, len(x), 1)],
            # labels=[((round(x[i]),6) if ((isinstance(x[i],float)
                # and not np.isnan(x[i])) or isinstance(x[i], int)) else 'None')
                    # for i in range(0, len(x), 1)],rotation=90)
        lfix = [str(round(x[i],6) if isinstance(x[i],float) else x[i])
            for i in range(0, len(x), 5)]  # AUG CHG 1 to 10 DEBUG
        # plt.xticks([i for i in range(0, len(x), 1)],
            # labels=[str(x[i]) for i in range(0, len(x), 1)],rotation=90)
        plt.xticks([i for i in range(0, len(x), 5)],   # AUG CHG 1 to 10 DEBUG
            labels=lfix,rotation=90)
        plt.xlabel(colToName[xcol]
            if (not normalizing) else (colToName[xcol] + ' (normalized Y)'))
        # plt.ylabel(colToName[ycol])
        xverticals = [xindex for xindex in range(0, len(x), 1)]
        if not nolines:
            ax.vlines(xverticals, yLowerMost, yUpperMost, linestyles='dotted',
                colors='gray')
        # yhorizontals = [xindex for xindex in range(0, len(ylines[0]), 1)]
        # ax.hlines(yhorizontals, x[0], x[-1], linestyles='dotted',
            # colors='gray')
        print("DEBUG OUTPUT genFile is",genFile) ; sys.stdout.flush()
        if genFile:
            saveFig(plt)
        else:
            plt.show()
    elif len(sys.argv) == 3:	# histogram
        print("DEBUG x", x)
        try:
            ycol = int(sys.argv[2])
        except ValueError:
            ycol = nameToCol[sys.argv[2]]
        y = [row[ycol] for row in table]
        safey = list(filter(
            (lambda n : isinstance(n,int) or (isinstance(n,float)
                and not np.isnan(n))), y))
            # STATS functions do not like filter's iterator!
        print('Y is',colToName[ycol],'Type is',colToType[ycol])
        if colToType[ycol] == float:
            titl = ("MEAN " + str(stats.mean(safey)) + "     MEDIAN "
                + str(+ stats.median(safey)) + "     PSTDEV "
                + str(stats.pstdev(safey))
                + "     MIN " + str(min(safey)) + "     MAX " + str(max(safey)))
            print('\t', titl)
            plt.title(titl)
        plt.hist(safey)
        plt.xlabel(colToName[ycol])
        # plt.xticks([i for i in range(0, len(x))],
            # labels=[str(x[i]) for i in range(0, len(x))])
        # plt.xlabel(colToName[xcol])
        # plt.ylabel(colToName[ycol])
        if genFile:
            saveFig(plt)
        else:
            plt.show()
