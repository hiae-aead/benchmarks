"""
Example Usage of IETF Benchmark Visualizer

This script demonstrates various ways to use the benchmark_visualizer module
to create beautiful, publication-ready visualizations of cryptographic benchmark data.
"""

from pathlib import Path
from benchmark_visualizer import BenchmarkVisualizer, PlotStyle, quick_visualize
from benchmark_parser import BenchmarkDataProcessor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Example 1: Basic usage with default styling."""
    print("=== Example 1: Basic Usage ===")
    
    # Create visualizer with default styling
    visualizer = BenchmarkVisualizer()
    
    # Load sample data (adjust path as needed)
    # visualizer.load_data("../sample_data/")
    
    # Create basic throughput plot
    # visualizer.plot_throughput_vs_size(
    #     operation="encrypt",
    #     log_scale=True,
    #     output_path="basic_throughput.png"
    # )
    
    print("Basic visualizer created with default light theme")


def example_custom_styling():
    """Example 2: Custom styling and themes."""
    print("\n=== Example 2: Custom Styling ===")
    
    # Create custom style for dark theme
    dark_style = PlotStyle(
        theme="dark",
        color_palette="viridis",
        figure_size=(14, 10),
        font_family="Times New Roman",
        font_size=14,
        title_size=18,
        dpi=300,
        colors=['#FF6B35', '#F7931E', '#FFD23F', '#06FFA5', '#118AB2', '#073B4C']
    )
    
    # Create visualizer with custom style
    visualizer = BenchmarkVisualizer(style=dark_style)
    
    print("Created visualizer with custom dark theme styling")
    
    # Example of creating styled plots (uncomment when you have data)
    # visualizer.plot_algorithm_comparison(
    #     algorithms=["aegis-128x2", "aes128-gcm"],
    #     operation="encrypt",
    #     plot_type="violin",
    #     output_path="styled_comparison.png"
    # )


def example_comprehensive_analysis():
    """Example 3: Comprehensive analysis with multiple plot types."""
    print("\n=== Example 3: Comprehensive Analysis ===")
    
    # Create publication-ready style
    pub_style = PlotStyle(
        theme="light",
        color_palette="Set2",
        figure_size=(12, 8),
        font_family="Arial",
        font_size=12,
        title_size=16,
        dpi=300,
        line_width=2.5
    )
    
    visualizer = BenchmarkVisualizer(style=pub_style)
    
    # Example workflow (uncomment when you have data)
    """
    # Load data from multiple sources
    data_files = [
        "../aegis-benchmark/results.csv",
        "../aes-gcm-benchmark/results.csv",
        "../chacha20-poly1305/results.csv"
    ]
    
    for file_path in data_files:
        if Path(file_path).exists():
            visualizer.load_data(file_path)
    
    # Create output directory
    output_dir = Path("comprehensive_analysis")
    output_dir.mkdir(exist_ok=True)
    
    # 1. Throughput analysis
    visualizer.plot_throughput_vs_size(
        operation="encrypt",
        log_scale=True,
        show_confidence=True,
        output_path=output_dir / "throughput_encrypt.png"
    )
    
    visualizer.plot_throughput_vs_size(
        operation="decrypt", 
        log_scale=True,
        show_confidence=True,
        output_path=output_dir / "throughput_decrypt.png"
    )
    
    # 2. Algorithm comparison
    visualizer.plot_algorithm_comparison(
        operation="encrypt",
        metric="gbps",
        plot_type="bar",
        output_path=output_dir / "algorithm_comparison_bar.png"
    )
    
    visualizer.plot_algorithm_comparison(
        operation="encrypt",
        metric="gbps",
        plot_type="violin",
        output_path=output_dir / "algorithm_comparison_violin.png"
    )
    
    # 3. Performance heatmap
    visualizer.plot_performance_heatmap(
        metric="gbps",
        operation="encrypt",
        output_path=output_dir / "performance_heatmap.png"
    )
    
    # 4. Cycles per byte analysis
    visualizer.plot_cycles_per_byte(
        operation="encrypt",
        output_path=output_dir / "cycles_per_byte.png"
    )
    
    # 5. Consistency analysis
    visualizer.plot_consistency_analysis(
        operation="encrypt",
        output_path=output_dir / "consistency_analysis.png"
    )
    
    # 6. Operation comparison for each algorithm
    algorithms = ["aegis-128x2", "aes128-gcm", "chacha20-poly1305"]
    for algorithm in algorithms:
        visualizer.plot_operation_comparison(
            algorithm=algorithm,
            metric="gbps",
            output_path=output_dir / f"operations_{algorithm}.png"
        )
    
    print(f"Comprehensive analysis saved to {output_dir}/")
    """
    
    print("Comprehensive analysis example prepared (uncomment code when data is available)")


def example_interactive_plots():
    """Example 4: Interactive plots with Plotly."""
    print("\n=== Example 4: Interactive Plots ===")
    
    visualizer = BenchmarkVisualizer()
    
    # Example interactive plots (uncomment when you have data)
    """
    # Load data
    visualizer.load_data("../benchmark_data/")
    
    output_dir = Path("interactive_plots")
    output_dir.mkdir(exist_ok=True)
    
    # Interactive throughput plot
    visualizer.plot_throughput_vs_size(
        operation="encrypt",
        interactive=True,
        output_path=output_dir / "interactive_throughput.html"
    )
    
    # Interactive comparison
    visualizer.plot_algorithm_comparison(
        operation="encrypt",
        interactive=True,
        plot_type="violin",
        output_path=output_dir / "interactive_comparison.html"
    )
    
    # Interactive heatmap
    visualizer.plot_performance_heatmap(
        interactive=True,
        output_path=output_dir / "interactive_heatmap.html"
    )
    
    # Comprehensive dashboard
    visualizer.create_dashboard(
        output_path=output_dir / "dashboard.html"
    )
    
    print(f"Interactive plots saved to {output_dir}/")
    """
    
    print("Interactive plots example prepared (uncomment code when data is available)")


def example_batch_export():
    """Example 5: Batch export in multiple formats."""
    print("\n=== Example 5: Batch Export ===")
    
    visualizer = BenchmarkVisualizer()
    
    # Example batch export (uncomment when you have data)
    """
    # Load all data from directory
    visualizer.load_data("../benchmark_results/", pattern="*.csv")
    
    # Export all plots in multiple formats
    visualizer.export_plots_batch(
        output_dir="publication_plots",
        formats=["png", "svg", "pdf", "html"],
        interactive=True
    )
    
    print("Batch export completed to publication_plots/")
    """
    
    print("Batch export example prepared (uncomment code when data is available)")


def example_custom_analysis():
    """Example 6: Custom analysis using the processor directly."""
    print("\n=== Example 6: Custom Analysis ===")
    
    # Example custom analysis workflow
    """
    from benchmark_parser import BenchmarkDataProcessor
    import pandas as pd
    import matplotlib.pyplot as plt
    
    # Load and process data
    processor = BenchmarkDataProcessor()
    processor.load_directory("../benchmark_data/")
    
    # Get combined dataframe for custom analysis
    df = processor.get_combined_dataframe()
    
    # Custom analysis: throughput efficiency vs message size
    encrypt_data = df[df['operation'] == 'encrypt']
    
    # Calculate efficiency score (higher throughput, lower cycles/byte = better)
    encrypt_data['efficiency'] = encrypt_data['gbps'] / (encrypt_data['cycles_byte'] + 1)
    
    # Create custom plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for algorithm in encrypt_data['algorithm'].unique():
        alg_data = encrypt_data[encrypt_data['algorithm'] == algorithm]
        ax.scatter(alg_data['size'], alg_data['efficiency'], 
                  label=algorithm, alpha=0.7, s=50)
    
    ax.set_xscale('log')
    ax.set_xlabel('Message Size (bytes)')
    ax.set_ylabel('Efficiency Score (Gbps/cycles_per_byte)')
    ax.set_title('Algorithm Efficiency Analysis')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('custom_efficiency_analysis.png', dpi=300)
    plt.show()
    
    # Generate summary statistics
    summary_stats = encrypt_data.groupby('algorithm').agg({
        'gbps': ['mean', 'max', 'std'],
        'cycles_byte': ['mean', 'min', 'std'],
        'cv_percent': ['mean', 'std'],
        'efficiency': ['mean', 'max']
    }).round(2)
    
    print("Algorithm Performance Summary:")
    print(summary_stats)
    
    # Export detailed results
    summary_stats.to_csv('algorithm_performance_summary.csv')
    """
    
    print("Custom analysis example prepared (uncomment code when data is available)")


def example_quick_visualization():
    """Example 7: Quick visualization using convenience function."""
    print("\n=== Example 7: Quick Visualization ===")
    
    # Example quick visualization (uncomment when you have data)
    """
    # Single function call to create basic visualizations
    visualizer = quick_visualize(
        data_path="../benchmark_data/",
        output_dir="quick_plots",
        theme="light"
    )
    
    # Optionally create additional custom plots
    visualizer.create_dashboard("quick_plots/dashboard.html")
    
    print("Quick visualization completed in quick_plots/")
    """
    
    print("Quick visualization example prepared (uncomment code when data is available)")


def example_paper_ready_plots():
    """Example 8: Publication-ready plots with academic styling."""
    print("\n=== Example 8: Publication-Ready Plots ===")
    
    # Academic paper style
    academic_style = PlotStyle(
        theme="light",
        color_palette="colorblind",  # Colorblind-friendly palette
        figure_size=(10, 6),  # Common academic paper size
        font_family="Times New Roman",
        font_size=10,
        title_size=12,
        label_size=11,
        legend_size=9,
        dpi=600,  # High resolution for papers
        line_width=1.5,
        marker_size=4,
        grid_alpha=0.2
    )
    
    visualizer = BenchmarkVisualizer(style=academic_style)
    
    print("Created visualizer with academic publication styling")
    
    # Example academic plots (uncomment when you have data)
    """
    # Load data
    visualizer.load_data("../benchmark_results/")
    
    # Create publication plots
    output_dir = Path("paper_figures")
    output_dir.mkdir(exist_ok=True)
    
    # Figure 1: Algorithm throughput comparison
    visualizer.plot_throughput_vs_size(
        operation="encrypt",
        algorithms=["AEGIS-128x2", "AES-128-GCM", "ChaCha20-Poly1305"],
        log_scale=True,
        show_confidence=False,  # Cleaner for papers
        output_path=output_dir / "figure1_throughput_comparison.pdf"
    )
    
    # Figure 2: Performance vs message size heatmap
    visualizer.plot_performance_heatmap(
        metric="gbps",
        operation="encrypt",
        output_path=output_dir / "figure2_performance_heatmap.pdf"
    )
    
    # Figure 3: Efficiency analysis (cycles per byte)
    visualizer.plot_cycles_per_byte(
        algorithms=["AEGIS-128x2", "AES-128-GCM"],
        operation="encrypt",
        output_path=output_dir / "figure3_efficiency_analysis.pdf"
    )
    
    # Table data for paper
    processor = visualizer.processor
    df = processor.get_combined_dataframe()
    
    # Generate summary table for paper
    summary_table = df[df['operation'] == 'encrypt'].groupby('algorithm').agg({
        'gbps': ['mean', 'max'],
        'cycles_byte': 'mean',
        'cv_percent': 'mean'
    }).round(2)
    
    summary_table.to_csv(output_dir / "table1_performance_summary.csv")
    summary_table.to_latex(output_dir / "table1_performance_summary.tex")
    
    print(f"Publication-ready figures saved to {output_dir}/")
    """
    
    print("Publication-ready plots example prepared")


if __name__ == "__main__":
    print("IETF Benchmark Visualizer - Examples")
    print("=" * 50)
    
    # Run all examples
    example_basic_usage()
    example_custom_styling()
    example_comprehensive_analysis()
    example_interactive_plots()
    example_batch_export()
    example_custom_analysis()
    example_quick_visualization()
    example_paper_ready_plots()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("\nTo use with real data:")
    print("1. Uncomment the relevant code sections in each example")
    print("2. Update file paths to point to your actual benchmark data")
    print("3. Run individual example functions")
    print("\nFor quick start with your data:")
    print("python benchmark_visualizer.py <your_data_path> <output_directory>")