"""
analyze_results.py — Produces every summary table quoted in the QI-CAAF
ns-3 validation report, directly from the raw CSVs produced by
run_all_experiments.sh.

Requires: pandas, scipy  (pip install pandas scipy --break-system-packages)
"""
import pandas as pd
import numpy as np
from scipy import stats


def ci95(x):
    """Return (mean, half-width of 95% CI) for an array-like of samples."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return float("nan"), float("nan")
    m = x.mean()
    if len(x) > 1:
        se = stats.sem(x)
        h = se * stats.t.ppf(0.975, len(x) - 1)
    else:
        h = 0.0
    return m, h


def table_ack_overhead(df):
    print("=" * 100)
    print("TABLE 7 — ACK/Confirmation overhead: conventional TCP (real) vs QI-CAAF")
    print("=" * 100)
    for n in sorted(df["n"].unique()):
        for loss in sorted(df["loss"].unique()):
            sub = df[(df["n"] == n) & (df["loss"] == loss)]
            conv_m, conv_h = ci95(sub["conv_ack_bytes"])
            qi_m, qi_h = ci95(sub["qicaaf_confirm_bytes"])
            reduction = (1 - qi_m / conv_m) * 100 if conv_m > 0 else float("nan")
            print(
                f"n={n:5d} loss={loss:.2f}  ConvACK={conv_m:9.1f}±{conv_h:6.1f} B   "
                f"QI-CAAF={qi_m:8.1f}±{qi_h:5.1f} B   Reduction={reduction:6.2f}%"
            )


def table_latency(df):
    print("=" * 100)
    print("TABLE 8 — Confirmation completion latency (successful rounds only)")
    print("=" * 100)
    for n in sorted(df["n"].unique()):
        for loss in sorted(df["loss"].unique()):
            sub = df[(df["n"] == n) & (df["loss"] == loss) & (df["global_confirmed"] == 1)]
            total = len(df[(df["n"] == n) & (df["loss"] == loss)])
            if len(sub) == 0:
                print(f"n={n:5d} loss={loss:.2f}  NO SUCCESSFUL ROUNDS (0/{total})")
                continue
            lat_m, lat_h = ci95(sub["confirm_time_ms"])
            print(
                f"n={n:5d} loss={loss:.2f}  ConfirmLatency={lat_m:8.3f}±{lat_h:6.3f} ms  "
                f"(successful rounds: {len(sub)}/{total})"
            )


def table_fidelity(df):
    print("=" * 100)
    print("TABLE 10 — Fidelity / global-confirmation rate at Fth=0.90")
    print("=" * 100)
    for n in sorted(df["n"].unique()):
        for loss in sorted(df["loss"].unique()):
            sub = df[(df["n"] == n) & (df["loss"] == loss)]
            fid_m, fid_h = ci95(sub["fidelity"])
            global_rate = sub["global_confirmed"].mean() * 100
            dc_m, dc_h = ci95(sub["data_complete_count"] / n * 100)
            print(
                f"n={n:5d} loss={loss:.2f}  meanFidelity={fid_m:.4f}±{fid_h:.4f}  "
                f"GlobalConfirmed(Fth=0.9)={global_rate:5.1f}%  "
                f"DataDeliveryRate={dc_m:6.2f}%±{dc_h:.2f}"
            )


def table_fth_sensitivity(df):
    print("=" * 100)
    print("Fidelity-threshold sensitivity at n=500")
    print("=" * 100)
    for loss in sorted(df["loss"].unique()):
        for fth in sorted(df["fth"].unique()):
            sub = df[(df["loss"] == loss) & (df["fth"] == fth)]
            fid_m, fid_h = ci95(sub["fidelity"])
            global_rate = sub["global_confirmed"].mean() * 100
            print(
                f"loss={loss:.2f} Fth={fth:.2f}  meanFidelity={fid_m:.4f}±{fid_h:.4f}  "
                f"GlobalConfirmedRate={global_rate:5.1f}%"
            )
        print()


def table_tcp_variant(df):
    print("=" * 100)
    print("TCP variant robustness (Reno vs Cubic) at n=1000")
    print("=" * 100)
    for tcp in df["tcp_variant"].unique():
        for loss in sorted(df["loss"].unique()):
            sub = df[(df["tcp_variant"] == tcp) & (df["loss"] == loss)]
            conv_m, _ = ci95(sub["conv_ack_bytes"])
            qi_m, _ = ci95(sub["qicaaf_confirm_bytes"])
            red = (1 - qi_m / conv_m) * 100
            print(
                f"{tcp:25s} loss={loss:.2f}  ConvACK={conv_m:9.1f}B  "
                f"QI-CAAF={qi_m:8.1f}B  Reduction={red:5.1f}%"
            )


def table_delack(df):
    print("=" * 100)
    print("Immediate ACK (delack=1) vs Delayed ACK (delack=2) vs QI-CAAF")
    print("=" * 100)
    for n in sorted(df["n"].unique()):
        for loss in sorted(df["loss"].unique()):
            sub1 = df[(df["n"] == n) & (df["loss"] == loss) & (df["delack"] == 1)]
            sub2 = df[(df["n"] == n) & (df["loss"] == loss) & (df["delack"] == 2)]
            if len(sub1) == 0 or len(sub2) == 0:
                continue
            m1, _ = ci95(sub1["conv_ack_bytes"])
            m2, _ = ci95(sub2["conv_ack_bytes"])
            qi_m, _ = ci95(sub2["qicaaf_confirm_bytes"])
            red_imm = (1 - qi_m / m1) * 100
            red_del = (1 - qi_m / m2) * 100
            print(
                f"n={n:5d} loss={loss:.2f}  ImmediateACK={m1:9.1f}B  DelayedACK={m2:9.1f}B  "
                f"QI-CAAF={qi_m:8.1f}B | Reduction vs Immediate={red_imm:5.1f}%  "
                f"vs Delayed={red_del:5.1f}%"
            )


if __name__ == "__main__":
    main = pd.read_csv("main_results.csv")
    table_ack_overhead(main)
    table_latency(main)
    table_fidelity(main)

    fth = pd.read_csv("fth_sweep.csv")
    table_fth_sensitivity(fth)

    tcpv = pd.read_csv("tcp_variant.csv")
    table_tcp_variant(tcpv)

    delack = pd.read_csv("delack_compare.csv")
    table_delack(delack)
