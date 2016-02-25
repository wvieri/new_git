#!/bin/bash

echo "run run_step1.sh "

test -e plot && rm -r plot || echo " plot Not exist"
mkdir plot

cd /afs/cern.ch/work/y/yuchang/13_TeV_Task/Optimize_cuts_with_limit/CMSSW_7_1_5/src/
eval `scramv1 runtime -sh`
cd -

time root -l -q -b Control_auto.C++





