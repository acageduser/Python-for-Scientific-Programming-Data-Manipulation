#       makefile for CSC223f23DataflowAssn4 project
#       Dr. Dale Parson. Fall 2023

all:		test

TARGET = CSC223f23DataflowAssn4
include ./makelib
DPOS := $(DPARSON)
PARSONFILES := $(DPOS)/DataMine
PARSONTMP := $(DPOS)/tmp
# FOLLOWING SET floating point comparison tolerance in diffarff.py
# REL_TOL Relative tolerance of .01%, ABS_TOL Absolute tolerance of 10**-6.
REL_TOL = 0.0001
ABS_TOL = 0.000001

build:	test

test:	clean
	$(PYTHON) CSC223f23DataflowAssn4.py 543343458 CSC223f23DataflowAssn4.csv
	diff --ignore-trailing-space --strip-trailing-cr CSC223f23DataflowAssn4.csv CSC223f23DataflowAssn4.ref > CSC223f23DataflowAssn4.dif

clean:	subclean
	/bin/rm -f junk* *.pyc 
	/bin/rm -f *.tmp *.o *.dif *.out __pycache__/*
	/bin/rm -f DEBUG*arff* tmp* CSC223f23DataflowAssn4.csv
