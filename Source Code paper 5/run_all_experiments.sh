#!/bin/bash
# run_all_experiments.sh — Reproduces every experiment referenced in the
# QI-CAAF ns-3 validation report. Run ./build.sh first.
set -e
cd "$(dirname "$0")"

# ---------------------------------------------------------------------
# 1. MAIN SWEEP: n x loss, 20 replications each -> main_results.csv
#    Used for Tables 7, 8, 10 (ACK overhead, latency, fidelity/PDR).
# ---------------------------------------------------------------------
rm -f main_results.csv
for n in 10 50 100 250 500 750 1000; do
  for loss in 0.01 0.05 0.10; do
    for run in $(seq 1 20); do
      ./qicaaf-ns3 --n=$n --loss=$loss --fth=0.90 --delack=2 \
        --run=$run --out=main_results.csv > /dev/null 2>&1
    done
  done
  echo "done n=$n ($(date +%T))"
done
echo "main sweep total rows: $(wc -l < main_results.csv)"

# ---------------------------------------------------------------------
# 2. IMMEDIATE-ACK vs DELAYED-ACK comparison -> delack_compare.csv
# ---------------------------------------------------------------------
rm -f delack_compare.csv
for delack in 1 2; do
  for n in 100 500 1000; do
    for loss in 0.01 0.05 0.10; do
      for run in $(seq 1 10); do
        ./qicaaf-ns3 --n=$n --loss=$loss --fth=0.90 --delack=$delack \
          --run=$run --out=delack_compare.csv > /dev/null 2>&1
      done
    done
  done
  echo "done delack=$delack"
done
echo "delack_compare total rows: $(wc -l < delack_compare.csv)"

# ---------------------------------------------------------------------
# 3. FIDELITY-THRESHOLD SENSITIVITY -> fth_sweep.csv
#    n=500, Fth in {0.80..1.00}, loss in {0.05, 0.10}, 20 reps each.
# ---------------------------------------------------------------------
rm -f fth_sweep.csv
for fth in 0.80 0.85 0.90 0.95 1.00; do
  for loss in 0.05 0.10; do
    for run in $(seq 1 20); do
      ./qicaaf-ns3 --n=500 --loss=$loss --fth=$fth --delack=2 \
        --run=$run --out=fth_sweep.csv > /dev/null 2>&1
    done
  done
done
echo "fth_sweep total rows: $(wc -l < fth_sweep.csv)"

# ---------------------------------------------------------------------
# 4. TCP VARIANT ROBUSTNESS (Reno vs Cubic) -> tcp_variant.csv
#    n=1000, both variants, all three loss rates, 15 reps each.
# ---------------------------------------------------------------------
rm -f tcp_variant.csv
for tcp in ns3::TcpLinuxReno ns3::TcpCubic; do
  for loss in 0.01 0.05 0.10; do
    for run in $(seq 1 15); do
      ./qicaaf-ns3 --n=1000 --loss=$loss --fth=0.90 --tcp=$tcp --delack=2 \
        --run=$run --out=tcp_variant.csv > /dev/null 2>&1
    done
  done
done
echo "tcp_variant total rows: $(wc -l < tcp_variant.csv)"

echo "=== All experiments complete ==="
