#!/bin/bash
# debug.sh is a shell script to debug CSC223f23WAVEassn2.csv,
# a column at a time, to find differences when a test fails
# timestep,triangle,sine,cos,square,pulse,risingsaw,fallingsaw
PYTHON="/usr/local/bin/python3.7"
# set -x  # verbose output
exitStatus=0
for column in 1 2 3 4 5 6 7 8
do
    cut -d, -f$column CSC223f23WAVEassn2.csv > tmpout.csv
    cut -d, -f$column reffiles/CSC223f23WAVEassn2.csv > tmpref.csv
    name=`head -1 tmpout.csv | sed -e 's///g'`
    # if $PYTHON diffcsv.py tmpout.csv tmpref.csv
    if diff --ignore-trailing-space --strip-trailing-cr --ignore-all-space tmpout.csv tmpref.csv > $name.dif
    then
        echo "column ${name} is OK"
    else
        exitStatus=1
        echo "column ${name} has PROBLEMS"
        ls -l $name.dif
    fi
done
if [ $exitStatus -ne 0 ]
then
    diff --ignore-trailing-space --strip-trailing-cr CSC223f23WAVEassn2.txt reffiles/CSC223f23WAVEassn2.txt > CSC223f23WAVEassn2.txt.dif
    echo "Check CSC223f23WAVEassn2.txt.dif as well."
fi
exit $exitStatus    # non-0 means error, kicks out makefile
