#!/bin/bash
# build.sh — Install ns-3.41 and compile qicaaf-ns3.cc
# Tested on Ubuntu 24.04 (noble)
set -e

echo "=== Installing ns-3.41 via apt ==="
apt-get update
apt-get install -y ns3 libns3-dev ns3-doc

echo "=== Compiling qicaaf-ns3.cc ==="
# IMPORTANT: use -I/usr/include (the PARENT directory), NOT -I/usr/include/ns3.
# ns-3 ships its own ns3/string.h; if /usr/include/ns3 is placed directly on
# the include path, angle-bracket lookups for <string.h> / <cstring> resolve
# to ns-3's string.h instead of glibc's, and the build fails with errors like
# "'memcpy' has not been declared in '::'". Always include as "ns3/xxx.h"
# with -I/usr/include on the search path instead.
g++ -std=c++17 -O2 -I/usr/include qicaaf-ns3.cc -o qicaaf-ns3 \
  -lns3-core -lns3-network -lns3-internet -lns3-point-to-point \
  -lns3-applications -lns3-flow-monitor

echo "=== Build complete: ./qicaaf-ns3 ==="
echo "Example run:"
echo "  ./qicaaf-ns3 --n=100 --loss=0.01 --fth=0.90 --run=1 --out=results.csv"
