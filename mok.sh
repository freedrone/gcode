#!/usr/bin/env bash
mkdir mok
cd mok
export MOKDIR=$(pwd)
curl -O http://www.math.uwaterloo.ca/tsp/concorde/downloads/codes/src/co031219.tgz
mkdir qsopt
cd qsopt
curl -O http://www.math.uwaterloo.ca/~bico/qsopt/beta/codes/PIC/qsopt.PIC.a
curl -O http://www.math.uwaterloo.ca/~bico/qsopt/beta/codes/PIC/qsopt.h
curl -O http://www.math.uwaterloo.ca/~bico/qsopt/beta/codes/PIC/qsopt
ln -s qsopt.PIC.a qsopt.a
ln -s qsopt.a libqsopt.a
export QSOPT_DIR=$(pwd)
cd ..
gunzip co031219.tgz
tar xvf co031219.tar
cd concorde
export CONCORDE_DIR=$(pwd)
./configure --with-qsopt=$QSOPT_DIR
make
rm concorde.h
curl -O https://gist.githubusercontent.com/freedrone/27d48beef2e2369e0e0495a2eb0c6b89/raw/cac9e7927a03872b4f7aa7aaedefe9ab17923513/concorde.h
cd ..
git clone https://github.com/freedrone/gcode.git
mkdir gcode/libs
rm -rf gcode/libs/concorde
rm -rf gcode/libs/qsopt
ln -s $CONCORDE_DIR/TSP/concorde $MOKDIR/gcode/libs/concorde
ln -s $CONCORDE_DIR/LINKERN/linkern $MOKDIR/gcode/libs/linkern
