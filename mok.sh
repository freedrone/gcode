#!/usr/bin/env bash
OUTFILE=$(pwd)/mok-install-logs.txt
touch ${OUTFILE}
if !(dpkg -s build-essential >> ${OUTFILE}); then
    sudo apt install build-essential
fi
if !(dpkg -s git >> ${OUTFILE}); then
    sudo apt install git
fi
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
echo 'extracting...'
gunzip co031219.tgz >>${OUTFILE}
tar xvf co031219.tar >>${OUTFILE}
cd concorde
export CONCORDE_DIR=$(pwd)
echo 'configuring...'
./configure --with-qsopt=${QSOPT_DIR} >> ${OUTFILE}
echo 'running make...'
make >> ${OUTFILE}
rm concorde.h
curl -O https://gist.githubusercontent.com/freedrone/27d48beef2e2369e0e0495a2eb0c6b89/raw/cac9e7927a03872b4f7aa7aaedefe9ab17923513/concorde.h
cd ..
git clone https://github.com/freedrone/gcode.git
mkdir gcode/libs
rm -rf gcode/libs/concorde
rm -rf gcode/libs/qsopt
ln -s ${CONCORDE_DIR}/TSP/concorde ${MOKDIR}/gcode/libs/concorde
ln -s ${CONCORDE_DIR}/LINKERN/linkern ${MOKDIR}/gcode/libs/linkern
exit
