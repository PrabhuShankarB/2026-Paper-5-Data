# QI-CAAF ns-3 Validation — Complete Reproducible Code

This is the exact code used to produce the ns-3 validation results referenced
in the QI-CAAF manuscript. Nothing here is illustrative — it's the literal
source, build script, and experiment driver that generated every number in
`QICAAF_ns3_Results_Report.md`.

## Files

| File | Purpose |
|---|---|
| `qicaaf-ns3.cc` | The ns-3 C++ simulation itself (conventional TCP baseline + QI-CAAF CECSF/GADCE implementation) |
| `build.sh` | Installs ns-3.41 and compiles `qicaaf-ns3.cc` |
| `run_all_experiments.sh` | Runs every experiment (main sweep, delayed-ACK comparison, Fth sensitivity, TCP-variant robustness) |
| `analyze_results.py` | Reproduces every summary table from the raw CSVs |
| `main_results.csv` | Raw output: 420 trials (7 values of n × 3 loss rates × 20 replications) |
| `fth_sweep.csv` | Raw output: fidelity-threshold sensitivity sweep |
| `tcp_variant.csv` | Raw output: TcpLinuxReno vs TcpCubic comparison |
| `delack_compare.csv` | Raw output: immediate-ACK vs delayed-ACK comparison |

## How to reproduce from scratch

```bash
# 1. Install ns-3.41 and compile (requires apt/root, Ubuntu 24.04 tested)
chmod +x build.sh
./build.sh

# 2. Run every experiment (takes a few minutes; ~600 total simulation runs)
chmod +x run_all_experiments.sh
./run_all_experiments.sh

# 3. Reproduce every summary table in the report
pip install pandas scipy --break-system-packages
python3 analyze_results.py
```

## What the simulation actually models

- **Topology:** star — 1 source node, n receiver nodes, independent
  point-to-point links (100 Mbps, 1 ms delay, DropTail queue, 100 packets).
- **Data path:** real ns-3 TCP (`TcpLinuxReno` or `TcpCubic`) delivers a
  512-byte payload from source to each receiver via `BulkSendApplication` →
  `PacketSink`. This exercises ns-3's actual congestion control, RTO
  backoff, and delayed-ACK timer — not an analytical approximation.
- **Loss:** `RateErrorModel`, applied independently to both directions of
  every link (so both data and confirmation/ACK traffic can be lost).
- **Conventional TCP baseline:** ACK overhead is measured directly from
  ns-3's `FlowMonitor` — specifically, the reverse-direction flow
  (receiver→source) on the TCP sink port, which is exactly the real ACK
  traffic ns-3's stack generates, including delayed ACKs and
  loss-triggered duplicate ACKs.
- **QI-CAAF:** implemented as two custom `ns3::Application` subclasses —
  `ConfirmSenderApp` (receiver side: fires one 4-byte UDP confirmation
  packet once its `PacketSink` has the full payload) and `AggregatorApp`
  (source side: collects confirmations, computes fidelity F = k/n,
  and evaluates the global confirmation decision against `Fth`).
- **Command-line parameters:** `--n`, `--loss`, `--fth`, `--run` (RNG seed
  index), `--tcp` (TCP variant), `--delack` (1=immediate, 2=delayed),
  `--out` (CSV path), plus `--bw`, `--delay`, `--queue` for link tuning.

## Known scope limitations (documented honestly in the manuscript)

- Payload is 512 bytes (below the 536-byte MSS), so it completes in a
  single TCP segment — this is why the TcpLinuxReno/TcpCubic and
  immediate/delayed-ACK comparisons came back identical. A multi-segment
  payload is needed to actually exercise those differences.
- FASRO's multi-round retry loop is not implemented end-to-end yet — this
  validates single-round confirmation behavior only.
- Only independent per-packet loss (`RateErrorModel`) was tested; bursty/
  correlated loss models were not run in this pass.

## Toolchain note (in case you hit this rebuilding it)

If you see `'memcpy' has not been declared in '::'` or similar errors from
`<cstring>` when compiling: this happens if `-I/usr/include/ns3` is placed
directly on the compiler's include path, because ns-3 ships its own
`ns3/string.h` which then shadows glibc's `string.h` for angle-bracket
lookups. Always compile with `-I/usr/include` (the parent directory) and
let the `#include "ns3/xxx.h"` includes in the source resolve normally —
`build.sh` already does this correctly.
