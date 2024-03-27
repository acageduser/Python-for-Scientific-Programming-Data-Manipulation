#!/bin/bash
#       makegraphs.sh for CSC223f23CSVassn1 assignment 1 project
#       Dr. Dale Parson. Fall 2023
#       Bash shell script to generate png histograms from generated CSV files.
#       Any command line args triggers display to screen instead of file.

# echo "NUM $#"
mkdir $HOME/public_html # Needed for URL public access, OK if already exists.
unset DISPLAY   # Needed to avoid X11 environment problems with matplotlib.
STUDENT=`basename $HOME`
PYTHON="/usr/local/bin/python3.7"
export PYTHONPATH="/usr/local/lib/python3.7/site-packages:/usr/local/lib/python3.7:$PYTHONPATH"
# Previous line needed to avoid environment problems with matplotlib.
CSVFILES=`ls *csv`
for csvf in $CSVFILES
do
    csvhead=`echo $csvf | sed -e 's/\.csv$//'`
    for attribute in `head -1 $csvf | sed -e 's/[ 	]//g' -e 's/,/ /g'`
    do
        PNGF="${csvhead}_${attribute}.png"
        echo "Extracting $csvf $csvhead $attribute $PNGF"
        if [ $# -gt 0 ]
        then
            $PYTHON histogram.py $csvf $attribute "who@${STUDENT}"
        else
            $PYTHON histogram.py $csvf $attribute "file@${PNGF}" "who@${STUDENT}"
		    echo "https://acad.kutztown.edu/~${STUDENT}/${PNGF}"
            /bin/cp -p $PNGF $HOME/public_html/$PNGF
        fi
    done
done
chmod -R +r $HOME/public_html   # Make all files under ~/public_html readable.



#		bash -c "unset DISPLAY && PYTHONPATH=$(PYTHONPATH) python histogram.py CSC223f23CSVpre1.csv NPUniform file@CSC223f23CSVpre1NPUni.png who@$(STUDENT)"
#		-mkdir $$HOME/public_html
#		cp -p *png $$HOME/public_html
#		-chmod -R +r+X $$HOME/public_html
#		@echo "https://acad.kutztown.edu/~$(STUDENT)/CSC223f23CSVpre1RndUni.png"
#		@echo "https://acad.kutztown.edu/~$(STUDENT)/CSC223f23CSVpre1NPUni.png"
