#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p results/plots
mvn clean verify | tee results/build.log
java -Xms256m -Xmx1g -jar target/daa-assignment4-1.0.jar benchmark results
python3 scripts/analyze.py
python3 scripts/render_report.py
