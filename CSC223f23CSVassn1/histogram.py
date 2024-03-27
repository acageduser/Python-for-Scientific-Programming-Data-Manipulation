# histogram.py D. Parson July 2023 migrated / simplified from plotcsv.py
# variants to plot only histograms.
import sys
import numpy as np  # Used during development but not production in assn1.
import matplotlib.pyplot as plt
import csv # csv.reader used to read csv file to plot.

def plotHistogram(incsvname, columnname, pngoutname, who=None):
    '''
    Plot an interactive histogram to the current display if pngoutname==None,
    else plot it to the PNG file named by pngoutname.
    Parameter incsvname is the .csv file to read.
    Parameter columnname is the column name from the first row of the
    CSV file to select for plotting.
    Return value is None.
    '''
    infile = open(incsvname, 'r')
    incsv = csv.reader(infile)
    headings = incsv.__next__() # Read 1st line of csv file which is header.
    # print('DEBUG headings', headings)
    if not columnname in headings:
        raise ValueError('ERROR, column name ' + columnname
            + ' is not in heading initial row:\n    ' + str(headings))
    colnumber = headings.index(columnname)
    try :
        coldata = [int(row[colnumber]) for row in incsv]
        # They come in as strings.
    except ValueError:  # May be a float for log.
        coldata = [float(row[colnumber]) for row in incsv]
        # They come in as strings.
    infile.close()  # ALWAYS! close files when done with them.
    # print('DEBUG coldata', coldata[0:10], type(min(coldata)), min(coldata), type(max(coldata)), max(coldata))
    # bins = [v for v in range(min(coldata), max(coldata), 1)]
    bins = max(coldata) + 1 - min(coldata)  # Bins to plot in output PNG
    fig, ax = plt.subplots()
    if who:
        ax.set_title('Author: ' + who)
    else:
        ax.set_title('Author unknown')
    ax.set_xlabel(incsvname + ' ' + columnname + ' value being counted')
    ax.set_ylabel('count')
    try:
        xticks = list(range(min(coldata), max(coldata)+2,
            (max(coldata)+1-min(coldata)) // 10))
        plt.xticks(xticks)
        # plt.hist(coldata, bins=bins)
        plt.hist(coldata, bins=1000)
    except TypeError:
        plt.hist(coldata, bins=1000)
        pass
#       xticks = []     # logs are floats
#       ix = min(coldata)
#       diffticks = max(coldata) - min(coldata)
#       stepticks = diffticks /10.0
#       while ix <= max(coldata)+2:
#           xticks.append(str(ix))
#           ix += stepticks
    # plt.hist(coldata, bins=list(range(min(coldata), max(coldata)+1, 1)))
    # plt.hist(coldata, bins=np.arange(min(coldata), max(coldata)+1, 1))
    # plt.hist(coldata, bins=bins)
    if pngoutname:
        myDPI = 300
        # plt.figure(figsize=(int(1920/myDPI),int(1080/myDPI)), dpi=myDPI)
        plt.savefig(pngoutname, dpi=myDPI)
    else:
        plt.show()  # Display on local terminal.

if __name__ == '__main__':
    pngoutname = None
    whoname = None
    usage = \
    'python histogram.py INPUT.csv COLUMNtoPLOT [ file@PNGNAME ] [ who@USERID ]'
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        raise ValueError(usage)
    elif len(sys.argv) > 3 and not (sys.argv[-1].startswith('file@')
            or sys.argv[-1].startswith('who@')):
        raise ValueError(usage)
    if len(sys.argv) > 3:
        if sys.argv[3].startswith('file@'):
            pngoutname = sys.argv[3][5:]
        elif sys.argv[3].startswith('who@'):
            whoname = sys.argv[3][4:]
        else:
            raise ValueError('ERROR, Invalid keyword argument: '
                + sys.argv[3] + '\n    ' + usage)
        if len(sys.argv) == 5:
            if sys.argv[4].startswith('file@'):
                if pngoutname:
                    raise ValueError('ERROR, Repeated file@ keyword argument: '
                        '\n    ' + usage)
                pngoutname = sys.argv[4][5:]
            elif sys.argv[4].startswith('who@'):
                if whoname:
                    raise ValueError('ERROR, Repeated who@ keyword argument: '
                        '\n    ' + usage)
                whoname = sys.argv[4][4:]
            else:
                raise ValueError('ERROR, Invalid keyword argument: '
                    + sys.argv[4] + '\n    ' + usage)
    incsvname = sys.argv[1]
    columnname = sys.argv[2]
    plotHistogram(incsvname, columnname, pngoutname, who=whoname)
