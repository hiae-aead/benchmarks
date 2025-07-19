#!/usr/bin/env python3
"""
Script to generate bar plots comparing encryption and decryption performance
for 65536 byte messages from CSV benchmark files.
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def parse_csv_file(filepath, size_filter=None):
    """Parse a benchmark CSV file and extract performance data."""
    algorithm_name = Path(filepath).stem
    
    # Read the file and find the "Encryption Only Performance" section
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Try different patterns for encryption performance sections
    encryption_start = None
    header_format = None
    
    # Pattern 1: "# Encryption Only Performance" (aegis, hiae variants)
    for i, line in enumerate(lines):
        if "# Encryption Only Performance" in line:
            encryption_start = i + 2  # Skip the header comment and column headers
            header_format = "csv"
            break
    
    # Pattern 2: "================ Encryption Only Performance ================" (rocca-s, hiae, aes)
    if encryption_start is None:
        for i, line in enumerate(lines):
            if "Encryption Only Performance" in line and "====" in line:
                # Find the table header line (contains |)
                for j in range(i + 1, min(i + 5, len(lines))):
                    if "|" in lines[j] and "Operation" in lines[j]:
                        encryption_start = j + 2  # Skip header and separator line
                        header_format = "table"
                        break
                break
    
    if encryption_start is None:
        print(f"Warning: Could not find 'Encryption Only Performance' section in {filepath}")
        return None
    
    # Read the data based on format
    data_rows = []
    
    if header_format == "csv":
        # CSV format parsing
        for i in range(encryption_start, len(lines)):
            line = lines[i].strip()
            if line.startswith('#') or line == '':
                break
            data_rows.append(line.split(','))
    
    elif header_format == "table":
        # Table format parsing (pipe-separated)
        for i in range(encryption_start, len(lines)):
            line = lines[i].strip()
            if line.startswith('=') or line == '' or 'AEAD Performance' in line:
                break
            if '|' in line and not line.startswith('-'):
                # Parse table row: Size | Operation | Gbps | MB/s | cyc/B | CV%
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 6:
                    # Convert to CSV format: Size,Operation,Gbps,MB/s,Cycles/Byte,CV%
                    size = parts[0]
                    operation = parts[1]
                    gbps = parts[2]
                    mbs = parts[3]
                    cycles = parts[4]
                    cv = parts[5].replace('%', '')
                    data_rows.append([size, operation, gbps, mbs, cycles, cv])
    
    if not data_rows:
        return None
    
    # Create DataFrame
    df = pd.DataFrame(data_rows, columns=['Size', 'Operation', 'Gbps', 'MB/s', 'Cycles/Byte', 'CV%'])
    
    # Convert numeric columns
    for col in ['Size', 'Gbps', 'MB/s', 'Cycles/Byte', 'CV%']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter by size if specified, otherwise return all data
    if size_filter is not None:
        df_filtered = df[df['Size'] == size_filter].copy()
        if df_filtered.empty:
            print(f"Warning: No {size_filter} byte data found in {filepath}")
            return None
    else:
        df_filtered = df.copy()
    
    # Add algorithm name
    df_filtered['Algorithm'] = algorithm_name
    
    return df_filtered


def create_performance_plot(csv_dir):
    """Create bar plots comparing encryption and decryption performance."""
    csv_dir = Path(csv_dir)
    
    if not csv_dir.exists():
        print(f"Error: Directory {csv_dir} does not exist")
        return
    
    # Find all CSV files
    csv_files = list(csv_dir.glob("*.csv"))
    
    if not csv_files:
        print(f"Error: No CSV files found in {csv_dir}")
        return
    
    # Parse all CSV files for 65536 byte size
    all_data = []
    for csv_file in csv_files:
        data = parse_csv_file(csv_file, size_filter=65536)
        if data is not None:
            all_data.append(data)
    
    if not all_data:
        print("Error: No valid data found in any CSV files")
        return
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Prepare data for plotting
    algorithms = combined_df['Algorithm'].unique()
    encrypt_data = combined_df[combined_df['Operation'] == 'encrypt']
    decrypt_data = combined_df[combined_df['Operation'] == 'decrypt']
    
    x = np.arange(len(algorithms))
    width = 0.35
    
    # Extract data for plotting
    encrypt_gbps = [encrypt_data[encrypt_data['Algorithm'] == alg]['Gbps'].iloc[0] if not encrypt_data[encrypt_data['Algorithm'] == alg].empty else 0 for alg in algorithms]
    decrypt_gbps = [decrypt_data[decrypt_data['Algorithm'] == alg]['Gbps'].iloc[0] if not decrypt_data[decrypt_data['Algorithm'] == alg].empty else 0 for alg in algorithms]
    encrypt_cycles = [encrypt_data[encrypt_data['Algorithm'] == alg]['Cycles/Byte'].iloc[0] if not encrypt_data[encrypt_data['Algorithm'] == alg].empty else 0 for alg in algorithms]
    decrypt_cycles = [decrypt_data[decrypt_data['Algorithm'] == alg]['Cycles/Byte'].iloc[0] if not decrypt_data[decrypt_data['Algorithm'] == alg].empty else 0 for alg in algorithms]
    
    # Plot 1: Throughput (Gbps)
    fig1, ax1 = plt.subplots(1, 1, figsize=(10, 6))
    
    bars1 = ax1.bar(x - width/2, encrypt_gbps, width, label='Encryption', alpha=0.8, color='skyblue')
    bars2 = ax1.bar(x + width/2, decrypt_gbps, width, label='Decryption', alpha=0.8, color='lightcoral')
    
    ax1.set_xlabel('Algorithm')
    ax1.set_ylabel('Performance (Gbps)')
    ax1.set_title('Encryption vs Decryption Throughput (65536 bytes)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(algorithms, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}', ha='center', va='bottom', fontsize=9)
    
    for bar in bars2:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save throughput plot
    output_file1 = csv_dir.parent / f"throughput_comparison_{csv_dir.name}.png"
    plt.savefig(output_file1, dpi=300, bbox_inches='tight')
    print(f"Throughput comparison saved to: {output_file1}")
    plt.close()
    
    # Plot 2: Cycles per Byte (lower is better)
    fig2, ax2 = plt.subplots(1, 1, figsize=(10, 6))
    
    bars3 = ax2.bar(x - width/2, encrypt_cycles, width, label='Encryption', alpha=0.8, color='skyblue')
    bars4 = ax2.bar(x + width/2, decrypt_cycles, width, label='Decryption', alpha=0.8, color='lightcoral')
    
    ax2.set_xlabel('Algorithm')
    ax2.set_ylabel('Cycles per Byte')
    ax2.set_title('Encryption vs Decryption Efficiency (65536 bytes)\nCycles per Byte (lower is better)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(algorithms, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars3:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    for bar in bars4:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save efficiency plot
    output_file2 = csv_dir.parent / f"efficiency_comparison_{csv_dir.name}.png"
    plt.savefig(output_file2, dpi=300, bbox_inches='tight')
    print(f"Efficiency comparison saved to: {output_file2}")
    plt.close()
    
    # Display summary table
    print("\nPerformance Summary (65536 bytes):")
    print("=" * 70)
    print(f"{'Algorithm':<20} {'Encrypt (Gbps)':<15} {'Decrypt (Gbps)':<15} {'Encrypt (c/b)':<15} {'Decrypt (c/b)':<15}")
    print("-" * 70)
    
    for i, alg in enumerate(algorithms):
        print(f"{alg:<20} {encrypt_gbps[i]:<15.2f} {decrypt_gbps[i]:<15.2f} {encrypt_cycles[i]:<15.3f} {decrypt_cycles[i]:<15.3f}")


def create_multi_size_plot(csv_dir):
    """Create line plots showing performance across different message sizes up to 65536 bytes."""
    csv_dir = Path(csv_dir)
    
    if not csv_dir.exists():
        print(f"Error: Directory {csv_dir} does not exist")
        return
    
    # Find all CSV files
    csv_files = list(csv_dir.glob("*.csv"))
    
    if not csv_files:
        print(f"Error: No CSV files found in {csv_dir}")
        return
    
    # Parse all CSV files for all sizes
    all_data = []
    for csv_file in csv_files:
        data = parse_csv_file(csv_file)  # No size filter to get all data
        if data is not None:
            all_data.append(data)
    
    if not all_data:
        print("Error: No valid data found in any CSV files")
        return
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Filter for sizes up to 65536 bytes
    sizes_to_plot = [64, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
    df_filtered = combined_df[combined_df['Size'].isin(sizes_to_plot)].copy()
    
    if df_filtered.empty:
        print("Error: No data found for sizes up to 65536 bytes")
        return
    
    algorithms = df_filtered['Algorithm'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(algorithms)))
    
    # Plot 1: Encryption Throughput (Gbps)
    fig1, ax1 = plt.subplots(1, 1, figsize=(10, 6))
    for i, alg in enumerate(algorithms):
        alg_data = df_filtered[(df_filtered['Algorithm'] == alg) & (df_filtered['Operation'] == 'encrypt')]
        if not alg_data.empty:
            alg_data = alg_data.sort_values('Size')
            ax1.plot(alg_data['Size'], alg_data['Gbps'], 'o-', label=alg, color=colors[i], linewidth=2, markersize=6)
    
    ax1.set_xlabel('Message Size (bytes)')
    ax1.set_ylabel('Throughput (Gbps)')
    ax1.set_title('Encryption Performance vs Message Size')
    ax1.set_xscale('log', base=2)
    ax1.set_xticks(sizes_to_plot)
    ax1.set_xticklabels([str(s) for s in sizes_to_plot])
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file1 = csv_dir.parent / f"encryption_throughput_{csv_dir.name}.png"
    plt.savefig(output_file1, dpi=300, bbox_inches='tight')
    print(f"Encryption throughput plot saved to: {output_file1}")
    plt.close()
    
    # Plot 2: Decryption Throughput (Gbps)
    fig2, ax2 = plt.subplots(1, 1, figsize=(10, 6))
    for i, alg in enumerate(algorithms):
        alg_data = df_filtered[(df_filtered['Algorithm'] == alg) & (df_filtered['Operation'] == 'decrypt')]
        if not alg_data.empty:
            alg_data = alg_data.sort_values('Size')
            ax2.plot(alg_data['Size'], alg_data['Gbps'], 'o-', label=alg, color=colors[i], linewidth=2, markersize=6)
    
    ax2.set_xlabel('Message Size (bytes)')
    ax2.set_ylabel('Throughput (Gbps)')
    ax2.set_title('Decryption Performance vs Message Size')
    ax2.set_xscale('log', base=2)
    ax2.set_xticks(sizes_to_plot)
    ax2.set_xticklabels([str(s) for s in sizes_to_plot])
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file2 = csv_dir.parent / f"decryption_throughput_{csv_dir.name}.png"
    plt.savefig(output_file2, dpi=300, bbox_inches='tight')
    print(f"Decryption throughput plot saved to: {output_file2}")
    plt.close()
    
    # Plot 3: Encryption Cycles per Byte
    fig3, ax3 = plt.subplots(1, 1, figsize=(10, 6))
    for i, alg in enumerate(algorithms):
        alg_data = df_filtered[(df_filtered['Algorithm'] == alg) & (df_filtered['Operation'] == 'encrypt')]
        if not alg_data.empty:
            alg_data = alg_data.sort_values('Size')
            ax3.plot(alg_data['Size'], alg_data['Cycles/Byte'], 'o-', label=alg, color=colors[i], linewidth=2, markersize=6)
    
    ax3.set_xlabel('Message Size (bytes)')
    ax3.set_ylabel('Cycles per Byte')
    ax3.set_title('Encryption Efficiency vs Message Size (lower is better)')
    ax3.set_xscale('log', base=2)
    ax3.set_xticks(sizes_to_plot)
    ax3.set_xticklabels([str(s) for s in sizes_to_plot])
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file3 = csv_dir.parent / f"encryption_efficiency_{csv_dir.name}.png"
    plt.savefig(output_file3, dpi=300, bbox_inches='tight')
    print(f"Encryption efficiency plot saved to: {output_file3}")
    plt.close()
    
    # Plot 4: Decryption Cycles per Byte
    fig4, ax4 = plt.subplots(1, 1, figsize=(10, 6))
    for i, alg in enumerate(algorithms):
        alg_data = df_filtered[(df_filtered['Algorithm'] == alg) & (df_filtered['Operation'] == 'decrypt')]
        if not alg_data.empty:
            alg_data = alg_data.sort_values('Size')
            ax4.plot(alg_data['Size'], alg_data['Cycles/Byte'], 'o-', label=alg, color=colors[i], linewidth=2, markersize=6)
    
    ax4.set_xlabel('Message Size (bytes)')
    ax4.set_ylabel('Cycles per Byte')
    ax4.set_title('Decryption Efficiency vs Message Size (lower is better)')
    ax4.set_xscale('log', base=2)
    ax4.set_xticks(sizes_to_plot)
    ax4.set_xticklabels([str(s) for s in sizes_to_plot])
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file4 = csv_dir.parent / f"decryption_efficiency_{csv_dir.name}.png"
    plt.savefig(output_file4, dpi=300, bbox_inches='tight')
    print(f"Decryption efficiency plot saved to: {output_file4}")
    plt.close()


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python plot_performance.py <csv_directory>")
        print("Example: python plot_performance.py csvs-zen4")
        sys.exit(1)
    
    csv_directory = sys.argv[1]
    
    print("Generating 65536-byte performance comparison...")
    create_performance_plot(csv_directory)
    
    print("\nGenerating multi-size performance comparison...")
    create_multi_size_plot(csv_directory)
    
    print("\nAll plots generated successfully!")


if __name__ == "__main__":
    main()