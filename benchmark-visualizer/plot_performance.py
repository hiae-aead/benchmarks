#!/usr/bin/env python3
"""Plot the CSV output of the benchmark programs.

Every benchmark prints two sections. "Encryption Only Performance" times the raw
keystream XOR, where decryption is literally the same operation as encryption,
so it is plotted once. "AEAD Performance" times the full authenticated mode, and
that is where encryption and decryption pull apart, so both are plotted there.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REFERENCE_SIZE = 65536
SIZES_TO_PLOT = [64, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]

SECTION_TITLES = {
    "stream": "Encryption Only Performance",
    "aead": "AEAD Performance",
}

COLUMNS = ["Size", "Operation", "Gbps", "MB/s", "Cycles/Byte", "CV%"]


def section_rows(lines, title):
    """Pull the raw rows of one section out of either output format."""
    for i, line in enumerate(lines):
        if title not in line:
            continue

        # CSV output: "# <title>", then a column header, then the rows.
        if line.lstrip().startswith("#"):
            rows = []
            for raw in lines[i + 2 :]:
                row = raw.strip()
                if not row or row.startswith("#"):
                    break
                rows.append(row.split(","))
            return rows

        # Human-readable output: a "====" banner, then a pipe-separated table.
        if "====" in line:
            header = None
            for j in range(i + 1, min(i + 5, len(lines))):
                if "|" in lines[j] and "Operation" in lines[j]:
                    header = j
                    break
            if header is None:
                continue
            rows = []
            for raw in lines[header + 2 :]:
                row = raw.strip()
                if not row or row.startswith("="):
                    break
                if "|" not in row or row.startswith("-"):
                    continue
                parts = [p.strip() for p in row.split("|")]
                if len(parts) >= 6:
                    rows.append(parts[:5] + [parts[5].replace("%", "")])
            return rows

    return []


def parse_csv_file(filepath, section="stream", size_filter=None):
    """Parse one benchmark file and return the rows of the requested section."""
    lines = Path(filepath).read_text().splitlines()
    rows = [r for r in section_rows(lines, SECTION_TITLES[section]) if len(r) >= 6]

    if not rows:
        print(f"Warning: no '{SECTION_TITLES[section]}' section in {filepath}")
        return None

    df = pd.DataFrame([r[:6] for r in rows], columns=COLUMNS)
    df["Operation"] = df["Operation"].str.strip().str.lower()
    # ROCCA-S also reports a MAC-only line, which has no counterpart elsewhere.
    df = df[df["Operation"].isin(["encrypt", "decrypt"])]

    for col in ["Size", "Gbps", "MB/s", "Cycles/Byte", "CV%"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if size_filter is not None:
        df = df[df["Size"] == size_filter]
        if df.empty:
            print(f"Warning: no {size_filter} byte data in {filepath}")
            return None

    df = df.copy()
    df["Algorithm"] = Path(filepath).stem
    return df


def load_section(csv_dir, section, size_filter=None):
    """Read every CSV file in a directory into one frame."""
    frames = []
    for csv_file in sorted(csv_dir.glob("*.csv")):
        data = parse_csv_file(csv_file, section=section, size_filter=size_filter)
        if data is not None:
            frames.append(data)

    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)


def by_operation(df, operation):
    """Index one operation's rows by algorithm name."""
    return df[df["Operation"] == operation].set_index("Algorithm")


def label_bars(ax, bars, fmt):
    span = ax.get_ylim()[1]
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + span * 0.01,
            format(height, fmt),
            ha="center",
            va="bottom",
            fontsize=8,
        )


def plot_aead_comparison(csv_dir, out_dir):
    """Bar charts of AEAD encryption against AEAD decryption at 64 KB."""
    df = load_section(csv_dir, "aead", size_filter=REFERENCE_SIZE)
    if df is None:
        print("Error: no AEAD data found")
        return

    encrypt = by_operation(df, "encrypt")
    decrypt = by_operation(df, "decrypt")
    algorithms = list(encrypt.sort_values("Gbps", ascending=False).index)

    def values(frame, column):
        return [frame.loc[alg, column] if alg in frame.index else 0 for alg in algorithms]

    x = np.arange(len(algorithms))
    width = 0.38

    for column, fmt, ylabel, title, stem in (
        (
            "Gbps",
            ".1f",
            "Performance (Gbps)",
            f"AEAD Encryption vs Decryption Throughput ({REFERENCE_SIZE} bytes)",
            "throughput_comparison",
        ),
        (
            "Cycles/Byte",
            ".3f",
            "Cycles per Byte",
            f"AEAD Encryption vs Decryption Efficiency ({REFERENCE_SIZE} bytes)\n"
            "Cycles per Byte (lower is better)",
            "efficiency_comparison",
        ),
    ):
        fig, ax = plt.subplots(1, 1, figsize=(12, 6.5))
        enc_bars = ax.bar(
            x - width / 2, values(encrypt, column), width,
            label="Encryption", alpha=0.8, color="skyblue",
        )
        dec_bars = ax.bar(
            x + width / 2, values(decrypt, column), width,
            label="Decryption", alpha=0.8, color="lightcoral",
        )

        ax.set_xlabel("Algorithm")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, rotation=45, ha="right")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.margins(y=0.12)

        label_bars(ax, enc_bars, fmt)
        label_bars(ax, dec_bars, fmt)

        plt.tight_layout()
        output = out_dir / f"{stem}_{csv_dir.name}.png"
        plt.savefig(output, dpi=300, bbox_inches="tight")
        print(f"Saved {output}")
        plt.close()


def plot_size_curves(csv_dir, out_dir, section, operation, stem, title, column, ylabel):
    """Line plot of one operation across message sizes."""
    df = load_section(csv_dir, section)
    if df is None:
        print(f"Error: no {section} data found")
        return

    df = df[df["Size"].isin(SIZES_TO_PLOT) & (df["Operation"] == operation)]
    if df.empty:
        print(f"Error: no {operation} data for sizes up to {REFERENCE_SIZE} bytes")
        return

    # Fastest algorithm first, so the legend follows the curves at the right edge.
    largest = df[df["Size"] == REFERENCE_SIZE].set_index("Algorithm")["Gbps"]
    algorithms = list(largest.sort_values(ascending=False).index)
    colors = plt.cm.tab10(np.linspace(0, 1, len(algorithms)))

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    for color, alg in zip(colors, algorithms):
        curve = df[df["Algorithm"] == alg].sort_values("Size")
        ax.plot(curve["Size"], curve[column], "o-", label=alg, color=color,
                linewidth=2, markersize=6)

    ax.set_xlabel("Message Size (bytes)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xscale("log", base=2)
    ax.set_xticks(SIZES_TO_PLOT)
    ax.set_xticklabels([str(s) for s in SIZES_TO_PLOT])
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output = out_dir / f"{stem}_{csv_dir.name}.png"
    plt.savefig(output, dpi=300, bbox_inches="tight")
    print(f"Saved {output}")
    plt.close()


def print_summary(csv_dir):
    """Terminal summary of the 64 KB numbers, keystream next to AEAD."""
    stream = load_section(csv_dir, "stream", size_filter=REFERENCE_SIZE)
    aead = load_section(csv_dir, "aead", size_filter=REFERENCE_SIZE)
    if stream is None or aead is None:
        return

    keystream = by_operation(stream, "encrypt")
    encrypt = by_operation(aead, "encrypt")
    decrypt = by_operation(aead, "decrypt")

    print(f"\nPerformance summary ({REFERENCE_SIZE} bytes, Gbps):")
    print("=" * 78)
    print(f"{'Algorithm':<22}{'Keystream':>12}{'AEAD enc':>12}{'AEAD dec':>12}{'enc/dec':>12}")
    print("-" * 78)

    for alg in encrypt.sort_values("Gbps", ascending=False).index:
        enc = encrypt.loc[alg, "Gbps"]
        dec = decrypt.loc[alg, "Gbps"] if alg in decrypt.index else float("nan")
        raw = keystream.loc[alg, "Gbps"] if alg in keystream.index else float("nan")
        print(f"{alg:<22}{raw:>12.1f}{enc:>12.1f}{dec:>12.1f}{enc / dec:>11.2f}x")


def main():
    if len(sys.argv) != 2:
        print("Usage: python plot_performance.py <csv_directory>")
        print("Example: python plot_performance.py csvs-zen4")
        sys.exit(1)

    csv_dir = Path(sys.argv[1])
    if not csv_dir.exists():
        print(f"Error: directory {csv_dir} does not exist")
        sys.exit(1)
    if not list(csv_dir.glob("*.csv")):
        print(f"Error: no CSV files in {csv_dir}")
        sys.exit(1)

    out_dir = csv_dir.parent

    plot_aead_comparison(csv_dir, out_dir)

    plot_size_curves(
        csv_dir, out_dir, "stream", "encrypt", "encryption_throughput",
        "Keystream Performance vs Message Size", "Gbps", "Throughput (Gbps)",
    )
    plot_size_curves(
        csv_dir, out_dir, "stream", "encrypt", "encryption_efficiency",
        "Keystream Efficiency vs Message Size (lower is better)",
        "Cycles/Byte", "Cycles per Byte",
    )
    plot_size_curves(
        csv_dir, out_dir, "aead", "encrypt", "aead_encryption_throughput",
        "AEAD Encryption Performance vs Message Size", "Gbps", "Throughput (Gbps)",
    )
    plot_size_curves(
        csv_dir, out_dir, "aead", "decrypt", "aead_decryption_throughput",
        "AEAD Decryption Performance vs Message Size", "Gbps", "Throughput (Gbps)",
    )

    print_summary(csv_dir)


if __name__ == "__main__":
    main()
