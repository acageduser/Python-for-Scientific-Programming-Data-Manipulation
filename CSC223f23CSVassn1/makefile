#       makefile for CSC223f23CSVassn1 assignment 1 project
#       Dr. Dale Parson. Fall 2023

all:		test

TARGET = CSC223f23CSVassn1
include ./makelib
DPOS := $(DPARSON)
PARSONFILES := $(DPOS)/Scripting
REFFILES := $(PARSONFILES)/csc223assn1reffiles
PARSONTMP := $(DPOS)/tmp
# FOLLOWING SET floating point comparison tolerance in diffcsv.py
# REL_TOL Relative tolerance of .01%, ABS_TOL Absolute tolerance of 10**-6.
REL_TOL = 0.0001
ABS_TOL = 0.000001

build:	test

test:	clean CSC223f23CSVpre1.csv CSC223f23CSVassn1.csv

CSC223f23CSVassn1.csv:	CSC223f23CSVassn1.py
		/bin/rm -f ./CSC223f23CSVassn1.csv ./CSC223f23CSVassn1.txt
		$(PYTHON) CSC223f23CSVassn1.py 220223523 $(PARSONTMP)/$(STUDENT)_CSC223f23CSVassn1.csv 
		ln -s $(PARSONTMP)/$(STUDENT)_CSC223f23CSVassn1.csv ./CSC223f23CSVassn1.csv
		ln -s $(PARSONTMP)/$(STUDENT)_CSC223f23CSVassn1.txt ./CSC223f23CSVassn1.txt
		diff --ignore-trailing-space --strip-trailing-cr CSC223f23CSVassn1.txt $(REFFILES)/CSC223f23CSVassn1.txt > CSC223f23CSVassn1.txt.dif
		$(PYTHON) diffcsv.py CSC223f23CSVassn1.csv  $(REFFILES)/CSC223f23CSVassn1.csv

CSC223f23CSVpre1.csv:	CSC223f23CSVpre1.py
		/bin/rm -f ./CSC223f23CSVpre1.csv ./CSC223f23CSVpre1.txt
		$(PYTHON) CSC223f23CSVpre1.py 220223523 $(PARSONTMP)/$(STUDENT)_CSC223f23CSVpre1.csv 
		ln -s $(PARSONTMP)/$(STUDENT)_CSC223f23CSVpre1.csv CSC223f23CSVpre1.csv
		ln -s $(PARSONTMP)/$(STUDENT)_CSC223f23CSVpre1.txt CSC223f23CSVpre1.txt
		diff --ignore-trailing-space --strip-trailing-cr CSC223f23CSVpre1.txt $(REFFILES)/CSC223f23CSVpre1.txt > CSC223f23CSVpre1.txt.dif
		$(PYTHON) diffcsv.py CSC223f23CSVpre1.csv  $(REFFILES)/CSC223f23CSVpre1.csv

clean:	subclean
	/bin/rm -f junk* *.pyc *.png *.csv CSC223f23CSVpre1.txt
	/bin/rm -f *.tmp *.o *.dif *.out __pycache__/* CSC223f23CSVassn1.txt
	/bin/rm -f $(PARSONTMP)/$(STUDENT)*.csv CSC223f23CSVpre1.csv CSC223f23CSVassn1.csv
	/bin/rm -f $(PARSONTMP)/$(STUDENT)*.txt CSC223f23CSVpre1.txt CSC223f23CSVassn1.txt

# In case student needs space.
clobber:	clean
	/bin/rm -f $$HOME/public_html/CSC223f23*.png

graphs:		CSC223f23CSVpre1.csv
			bash ./makegraphs.sh

STUDENT:
	grep 'STUDENT [0-9].*%' CSC223f23CSVassn1.py
