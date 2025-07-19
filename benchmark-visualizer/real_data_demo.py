#!/usr/bin/env python3
"""
Real Data Demo Script for IETF Benchmark Visualizer

This script demonstrates the complete visualization pipeline using real benchmark 
data from HiAE and AEGIS-128x2 algorithms.
"""

from benchmark_parser import BenchmarkCSVParser
from benchmark_visualizer import BenchmarkVisualizer
import os

def main():
    print("=== IETF Benchmark Visualizer: Real Data Demo ===\n")
    
    # Initialize components
    parser = BenchmarkCSVParser()
    visualizer = BenchmarkVisualizer()
    
    # CSV files with real benchmark data
    csv_files = ['hiae_results.csv', 'aegis_results.csv']
    
    print("1. Testing CSV Parser...")
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            data = parser.parse_file(csv_file)
            total_records = sum(len(section.records) for section in data.sections.values())
            print(f"   ✓ {csv_file}: {data.algorithm} - {total_records} records in {len(data.sections)} sections")
        else:
            print(f"   ✗ {csv_file}: File not found")
    
    print("\n2. Loading data into visualizer...")
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            visualizer.load_data(csv_file)
    
    print(f"   ✓ Loaded datasets: {list(visualizer.processor.data_sets.keys())}")
    
    print("\n3. Creating visualizations...")
    output_dir = "real_data_demo_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Algorithm comparison
    visualizer.plot_algorithm_comparison(
        algorithms=['HiAE', 'AEGIS-128x2'],
        operation='encrypt',
        output_path=f'{output_dir}/algorithm_comparison_encrypt.png'
    )
    print("   ✓ Algorithm comparison (encrypt)")
    
    visualizer.plot_algorithm_comparison(
        algorithms=['HiAE', 'AEGIS-128x2'],
        operation='decrypt',
        output_path=f'{output_dir}/algorithm_comparison_decrypt.png'
    )
    print("   ✓ Algorithm comparison (decrypt)")
    
    # Performance heatmap
    visualizer.plot_performance_heatmap(
        output_path=f'{output_dir}/performance_heatmap.png'
    )
    print("   ✓ Performance heatmap")
    
    # Cycles per byte analysis
    visualizer.plot_cycles_per_byte(
        output_path=f'{output_dir}/cycles_per_byte.png'
    )
    print("   ✓ Cycles per byte analysis")
    
    # Throughput vs message size
    visualizer.plot_throughput_vs_size(
        output_path=f'{output_dir}/throughput_vs_size.png'
    )
    print("   ✓ Throughput vs message size")
    
    # Interactive dashboard
    visualizer.create_dashboard(
        output_path=f'{output_dir}/interactive_dashboard.html'
    )
    print("   ✓ Interactive dashboard")
    
    print(f"\n4. Demo completed successfully!")
    print(f"   All visualizations saved to: {output_dir}/")
    print(f"   Open {output_dir}/interactive_dashboard.html in a browser for interactive exploration")
    
    # Print some sample performance data
    print("\n5. Sample Performance Data:")
    hiae_data = parser.parse_file('hiae_results.csv')
    aegis_data = parser.parse_file('aegis_results.csv')
    
    print("   HiAE (AEAD Performance):")
    for record in hiae_data.sections['AEAD Performance'].records[:3]:
        print(f"     {record.size:>6} bytes {record.operation}: {record.gbps:>7.2f} Gbps")
    
    print("   AEGIS-128x2 (AEAD Performance):")
    for record in aegis_data.sections['AEAD Performance'].records[:3]:
        print(f"     {record.size:>6} bytes {record.operation}: {record.gbps:>7.2f} Gbps")

if __name__ == "__main__":
    main()