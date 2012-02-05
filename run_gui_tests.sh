#!/bin/bash

# script to run gui tests

if which xvfb-run >/dev/null ; then
	echo "Running tests using xvfb-run"
	xvfb-run python run_tests.py -a gui tests/gui/ --nologcapture  
	exit $?
fi

if which Xvfb >/dev/null ; then
	echo "Running tests using Xvfb"
	Xvfb :99 2>/dev/null &
	PID=$!
	DISPLAY=":99" python run_tests.py -a gui tests/gui/ --nologcapture
	RET=$?
	kill -9 $PID
	exit $RET
fi

# just run in the normal x server
python run_tests.py -a gui tests/gui/ --nologcapture
