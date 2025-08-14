#!/usr/bin/env bash

make -C ./ImageCompare run ARGS="../bin/Serial/visualiseSearch.png ../bin/Parallel/visualiseSearch.png"
echo
make -C ./ImageCompare run ARGS="../bin/Serial/visualiseSearchPath.png ../bin/Parallel/visualiseSearchPath.png"
