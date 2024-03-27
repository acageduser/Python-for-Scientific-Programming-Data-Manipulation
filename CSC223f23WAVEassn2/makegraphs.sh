#!/bin/bash
#       makegraphs.sh for CSC223f23WAVEassn2 assignment 2 project
#       Dr. Dale Parson. Fall 2023
#       Bash shell script to generate png histograms from generated CSV files.
#       Any command line argument turns off PNG file construction.

mkdir $HOME/public_html # Needed for URL public access, OK if already exists.
unset DISPLAY   # Needed to avoid X11 environment problems with matplotlib.
STUDENT=`basename $HOME`
PYTHON="/usr/local/bin/python3.7"
export PYTHONPATH="/usr/local/lib/python3.7/site-packages:/usr/local/lib/python3.7:$PYTHONPATH"
# Previous line needed to avoid environment problems with matplotlib.
if [ $# -eq 0 ]
then
python plotcsv_1_3.py CSC223f23WAVEassn2.csv timestep -file:CSC223f23WAVEassn2.png \
    triangle sine cos square pulse risingsaw fallingsaw
else
python plotcsv_1_3.py CSC223f23WAVEassn2.csv timestep \
    triangle sine cos square pulse risingsaw fallingsaw
fi
chmod -R +r $HOME/public_html   # Make all files under ~/public_html readable.
