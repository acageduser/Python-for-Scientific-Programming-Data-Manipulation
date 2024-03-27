#       makefile for CSC223f23DeriveAssn3 assignment 3 project
#       Dr. Dale Parson. Fall 2023

all:		test

TARGET = CSC223f23DeriveAssn3
include ./makelib
# FOLLOWING SET floating point comparison tolerance in diffcsv.py
# REL_TOL Relative tolerance of .01%, ABS_TOL Absolute tolerance of 10**-6.
REL_TOL = 0.0001
ABS_TOL = 0.000001

build:	test

test:	clean RT_month_10_Derive.csv

RT_month_10_Derive.csv:		CSC223f23DeriveAssn3.py RT_month_10.csv
		$(PYTHON) CSC223f23DeriveAssn3.py RT_month_10.csv HMtempC_mean WindSpd_mean wnd_WNW_NW -exp.5 -avg5 -delta1 
		# -exp.N means exponential smoothing with a fractional alpha of .N
		# -avgN means average the current value and the previous N-1 rows
		# -deltaN means compute difference between previous Nth row and current
		$(MAKE) debug
		diff --ignore-trailing-space --strip-trailing-cr --ignore-all-space RT_month_10_Derive.csv RT_month_10_Derive.ref > RT_month_10_Derive.dif

debug:
		bash debug.sh

clean:	subclean
	/bin/rm -f junk* *.pyc *.png RT_month_10_Derive.csv
	/bin/rm -f *.tmp *.o *.dif *.out __pycache__/*
	/bin/rm -f *.dif tmp* *.tmp
