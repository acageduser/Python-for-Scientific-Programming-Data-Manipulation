#       makefile for CSC223f23WAVEassn2 assignment 2 project
#       Dr. Dale Parson. Fall 2023

all:		test

TARGET = CSC223f23WAVEassn2
include ./makelib
# FOLLOWING SET floating point comparison tolerance in diffcsv.py
# REL_TOL Relative tolerance of .01%, ABS_TOL Absolute tolerance of 10**-6.
REL_TOL = 0.0001
ABS_TOL = 0.000001

build:	test

test:	clean CSC223f23WAVEassn2.csv

CSC223f23WAVEassn2.csv:	CSC223f23WAVEassn2.py CSC223f23WaveParams.csv
		$(PYTHON) CSC223f23WAVEassn2.py
		# $(PYTHON) diffcsv.py CSC223f23WAVEassn2.csv  reffiles/CSC223f23WAVEassn2.csv
		# diff --ignore-trailing-space --strip-trailing-cr --ignore-all-space CSC223f23WAVEassn2.csv reffiles/CSC223f23WAVEassn2.csv > CSC223f23WAVEassn2.dif
		$(MAKE) debug
		diff --ignore-trailing-space --strip-trailing-cr CSC223f23WAVEassn2.txt reffiles/CSC223f23WAVEassn2.txt > CSC223f23WAVEassn2.txt.dif

clean:	subclean
	/bin/rm -f junk* *.pyc *.png CSC223f23WAVEassn2.csv tmpout.csv tmpref.csv
	/bin/rm -f *.tmp *.o *.dif *.out __pycache__/* CSC223f23WAVEassn2.txt
	/bin/rm -f *.dif

# In case student needs space.
clobber:	clean
	/bin/rm -f $$HOME/public_html/CSC223f23*.png

graphs:		CSC223f23WAVEassn2.csv
			bash ./makegraphs.sh

debug:
			bash debug.sh

STUDENT:
	grep 'STUDENT [0-9].*%' CSC223f23WAVEassn2.py
