#!/bin/bash
# debug.sh is a shell script to debug RT_month_10_Derive.csv
# a column at a time, to find differences when a test fails
# CSC223, Fall 2023
PYTHON="/usr/local/bin/python3.7"
# set -x  # verbose output
exitStatus=0
for column in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
do
    cut -d, -f$column RT_month_10_Derive.csv > tmpout.csv
    cut -d, -f$column RT_month_10_Derive.ref > tmpref.csv
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
    diff --ignore-trailing-space --strip-trailing-cr RT_month_10_Derive.csv RT_month_10_Derive.ref > RT_month_10_Derive.dif
    echo "Check RT_month_10_Derive.dif as well."
fi
exit $exitStatus    # non-0 means error, kicks out makefile
