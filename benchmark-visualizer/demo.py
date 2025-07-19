#!/usr/bin/env python3
"""
IETF Benchmark Visualizer - Demonstration Script

This script demonstrates the key features of the benchmark visualization module
by creating sample data and generating various types of plots.
"""

import numpy as np
import pandas as pd
import tempfile
import shutil
from pathlib import Path
import logging

from benchmark_visualizer import BenchmarkVisualizer, PlotStyle, quick_visualize
from plot_config import (
    get_academic_style, get_presentation_style, get_web_style, 
    get_dark_style, COLOR_PALETTES
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def create_demo_data():
    """Create realistic demo benchmark data."""
    
    logger.info("Creating demo benchmark data...")
    
    # Algorithm configurations
    algorithms = {
        "AEGIS-128x2": {
            "base_throughput": 28.5,
            "base_cycles": 2.4,
            "consistency": 0.8
        },
        "AES-128-GCM": {
            "base_throughput": 19.2,
            "base_cycles": 3.6,
            "consistency": 1.2
        },
        "ChaCha20-Poly1305": {
            "base_throughput": 14.8,
            "base_cycles": 4.9,
            "consistency": 1.5
        },
        "ASCON-128": {
            "base_throughput": 8.3,
            "base_cycles": 8.7,
            "consistency": 2.1
        }
    }
    
    message_sizes = [64, 256, 1024, 4096, 16384, 65536]
    operations = ["encrypt", "decrypt", "aead_encrypt", "aead_decrypt"]
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="ietf_benchmark_demo_"))
    logger.info(f"Demo data directory: {temp_dir}")
    
    for alg_name, alg_config in algorithms.items():
        csv_content = f"""# Algorithm: {alg_name}
# {alg_name} Performance Benchmark Results
# Generated for demonstration purposes
# 
# Test Configuration:
# - Platform: Intel Core i7-12700K
# - Compiler: Clang 15.0
# - Optimization: -O3 -march=native
# - Iterations: 1000000 per test

# Encryption Performance
Size,Operation,Gbps,MB/s,Cycles/Byte,CV%
"""
        
        for size in message_sizes:
            # Realistic performance scaling
            size_log = np.log2(size / 64)  # Normalize to smallest size
            
            # Performance improves with larger messages (amortized overhead)
            throughput_factor = 1.0 + (size_log * 0.12)  # 12% improvement per doubling
            cycles_factor = 1.0 - (size_log * 0.05)      # 5% fewer cycles per doubling
            
            for operation in operations:
                # Base performance
                base_gbps = alg_config["base_throughput"]
                base_cycles = alg_config["base_cycles"]
                base_cv = alg_config["consistency"]
                
                # Apply size scaling
                gbps = base_gbps * throughput_factor
                cycles = base_cycles * cycles_factor
                
                # Operation-specific adjustments
                if "decrypt" in operation:
                    gbps *= 0.96  # Decrypt slightly slower
                    cycles *= 1.04
                elif "aead" in operation:
                    gbps *= 0.91  # AEAD has authentication overhead
                    cycles *= 1.15
                
                # Add realistic noise
                gbps += np.random.normal(0, gbps * 0.02)  # 2% noise
                cycles += np.random.normal(0, cycles * 0.03)  # 3% noise
                
                # Ensure positive values
                gbps = max(0.1, gbps)
                cycles = max(0.1, cycles)
                
                # Calculate derived metrics
                mb_s = gbps * 125.0  # Convert Gbps to MB/s
                cv_percent = base_cv + np.random.uniform(-0.3, 0.3)
                cv_percent = max(0.1, cv_percent)  # Ensure positive
                
                csv_content += f"{size},{operation},{gbps:.1f},{mb_s:.1f},{cycles:.1f},{cv_percent:.1f}\n"
        
        # Add performance section headers for different operations
        csv_content += "\n# AEAD Performance\n"
        for size in message_sizes:
            size_log = np.log2(size / 64)
            throughput_factor = 1.0 + (size_log * 0.10)  # Slightly less scaling for AEAD
            
            # AEAD-specific performance
            gbps = alg_config["base_throughput"] * 0.88 * throughput_factor
            mb_s = gbps * 125.0
            cycles = alg_config["base_cycles"] * 1.2 * (1.0 - size_log * 0.04)
            cv_percent = alg_config["consistency"] * 1.1
            
            csv_content += f"{size},aead,{gbps:.1f},{mb_s:.1f},{cycles:.1f},{cv_percent:.1f}\n"
        
        # Save to file
        filename = alg_name.lower().replace("-", "_") + "_benchmark.csv"
        filepath = temp_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(csv_content)
        
        logger.info(f"Created {filename}")
    
    return temp_dir


def demo_basic_usage(data_dir, output_dir):
    """Demonstrate basic usage of the visualizer."""
    
    logger.info("=== Demo 1: Basic Usage ===")
    
    # Create visualizer with default settings
    visualizer = BenchmarkVisualizer()
    
    # Load data
    logger.info("Loading demo data...")
    identifiers = visualizer.load_data(data_dir)
    logger.info(f"Loaded {len(identifiers)} algorithm datasets")
    
    # Create basic throughput plot
    logger.info("Creating throughput vs message size plot...")
    visualizer.plot_throughput_vs_size(
        operation="encrypt",
        log_scale=True,
        show_confidence=True,
        output_path=str(output_dir / "demo_throughput.png")
    )
    
    # Create algorithm comparison
    logger.info("Creating algorithm comparison...")
    visualizer.plot_algorithm_comparison(
        operation="encrypt",
        metric="gbps",
        plot_type="bar",
        output_path=str(output_dir / "demo_comparison.png")
    )
    
    logger.info("✓ Basic usage demo completed")


def demo_styling(data_dir, output_dir):
    """Demonstrate different styling options."""
    
    logger.info("=== Demo 2: Styling Options ===")
    
    styles = [
        ("academic", get_academic_style(), "Academic paper style"),
        ("presentation", get_presentation_style(), "Presentation slides"),
        ("web", get_web_style(), "Web-friendly style"),
        ("dark", get_dark_style(), "Dark theme")
    ]
    
    for style_name, style, description in styles:
        logger.info(f"Creating {style_name} style plot - {description}")
        
        visualizer = BenchmarkVisualizer(style=style)
        visualizer.load_data(data_dir)
        
        visualizer.plot_throughput_vs_size(
            operation="encrypt",
            log_scale=True,
            output_path=str(output_dir / f"demo_style_{style_name}.png")
        )
    
    logger.info("✓ Styling demo completed")


def demo_plot_types(data_dir, output_dir):
    """Demonstrate different plot types."""
    
    logger.info("=== Demo 3: Plot Types ===")
    
    # Use web style for consistent appearance
    visualizer = BenchmarkVisualizer(style=get_web_style())
    visualizer.load_data(data_dir)
    
    # 1. Performance heatmap
    logger.info("Creating performance heatmap...")
    visualizer.plot_performance_heatmap(
        metric="gbps",
        operation="encrypt",
        output_path=str(output_dir / "demo_heatmap.png")
    )
    
    # 2. Cycles per byte analysis
    logger.info("Creating cycles per byte analysis...")
    visualizer.plot_cycles_per_byte(
        operation="encrypt",
        output_path=str(output_dir / "demo_cycles.png")
    )
    
    # 3. Consistency analysis
    logger.info("Creating consistency analysis...")
    visualizer.plot_consistency_analysis(
        operation="encrypt",
        output_path=str(output_dir / "demo_consistency.png")
    )
    
    # 4. Operation comparison (for first algorithm)
    df = visualizer.processor.get_combined_dataframe()
    first_algorithm = df['algorithm'].iloc[0]
    
    logger.info(f"Creating operation comparison for {first_algorithm}...")
    visualizer.plot_operation_comparison(
        algorithm=first_algorithm,
        metric="gbps",
        output_path=str(output_dir / f"demo_operations_{first_algorithm.replace('-', '_')}.png")
    )
    
    # 5. Violin plot comparison
    logger.info("Creating violin plot comparison...")
    visualizer.plot_algorithm_comparison(
        operation="encrypt",
        plot_type="violin",
        output_path=str(output_dir / "demo_violin.png")
    )
    
    logger.info("✓ Plot types demo completed")


def demo_interactive(data_dir, output_dir):
    """Demonstrate interactive plots and dashboard."""
    
    logger.info("=== Demo 4: Interactive Plots ===")
    
    visualizer = BenchmarkVisualizer()
    visualizer.load_data(data_dir)
    
    # Interactive throughput plot
    logger.info("Creating interactive throughput plot...")
    visualizer.plot_throughput_vs_size(
        operation="encrypt",
        interactive=True,
        output_path=str(output_dir / "demo_interactive_throughput.html")
    )
    
    # Interactive comparison
    logger.info("Creating interactive algorithm comparison...")
    visualizer.plot_algorithm_comparison(
        operation="encrypt",
        interactive=True,
        plot_type="violin",
        output_path=str(output_dir / "demo_interactive_comparison.html")
    )
    
    # Comprehensive dashboard
    logger.info("Creating comprehensive dashboard...")
    visualizer.create_dashboard(
        output_path=str(output_dir / "demo_dashboard.html")
    )
    
    logger.info("✓ Interactive demo completed")


def demo_custom_styling(data_dir, output_dir):
    """Demonstrate custom styling and configuration."""
    
    logger.info("=== Demo 5: Custom Styling ===")
    
    # Create custom crypto-themed style
    crypto_style = PlotStyle(
        theme="light",
        figure_size=(14, 9),
        font_family="Arial",
        font_size=13,
        title_size=18,
        dpi=300,
        line_width=3,
        marker_size=10,
        colors=COLOR_PALETTES["crypto_themed"]
    )
    
    visualizer = BenchmarkVisualizer(style=crypto_style)
    visualizer.load_data(data_dir)
    
    logger.info("Creating custom-styled throughput plot...")
    visualizer.plot_throughput_vs_size(
        operation="encrypt",
        log_scale=True,
        show_confidence=True,
        output_path=str(output_dir / "demo_custom_style.png")
    )
    
    # High-contrast style for accessibility
    accessible_style = PlotStyle(
        theme="light",
        figure_size=(12, 8),
        font_size=16,
        line_width=4,
        marker_size=12,
        colors=COLOR_PALETTES["high_contrast"]
    )
    
    visualizer2 = BenchmarkVisualizer(style=accessible_style)
    visualizer2.load_data(data_dir)
    
    logger.info("Creating high-contrast accessible plot...")
    visualizer2.plot_algorithm_comparison(
        operation="encrypt",
        plot_type="bar",
        output_path=str(output_dir / "demo_accessible.png")
    )
    
    logger.info("✓ Custom styling demo completed")


def demo_batch_export(data_dir, output_dir):
    """Demonstrate batch export functionality."""
    
    logger.info("=== Demo 6: Batch Export ===")
    
    visualizer = BenchmarkVisualizer(style=get_web_style())
    visualizer.load_data(data_dir)
    
    batch_dir = output_dir / "batch_export"
    batch_dir.mkdir(exist_ok=True)
    
    logger.info("Running batch export...")
    visualizer.export_plots_batch(
        output_dir=str(batch_dir),
        formats=["png", "svg"],
        interactive=False
    )
    
    logger.info("✓ Batch export demo completed")


def demo_quick_mode(data_dir, output_dir):
    """Demonstrate quick visualization mode."""
    
    logger.info("=== Demo 7: Quick Mode ===")
    
    quick_dir = output_dir / "quick_mode"
    quick_dir.mkdir(exist_ok=True)
    
    logger.info("Running quick visualization...")
    visualizer = quick_visualize(
        data_path=data_dir,
        output_dir=str(quick_dir),
        theme="light"
    )
    
    # Add dashboard
    logger.info("Creating quick dashboard...")
    visualizer.create_dashboard(str(quick_dir / "quick_dashboard.html"))
    
    logger.info("✓ Quick mode demo completed")


def main():
    """Run all demonstration scenarios."""
    
    print("🚀 IETF Benchmark Visualizer - Comprehensive Demo")
    print("=" * 60)
    
    # Create demo data
    data_dir = create_demo_data()
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Run all demos
        demo_basic_usage(data_dir, output_dir)
        demo_styling(data_dir, output_dir)
        demo_plot_types(data_dir, output_dir)
        demo_interactive(data_dir, output_dir)
        demo_custom_styling(data_dir, output_dir)
        demo_batch_export(data_dir, output_dir)
        demo_quick_mode(data_dir, output_dir)
        
        print("\n" + "=" * 60)
        print("🎉 All demos completed successfully!")
        print(f"📁 Output directory: {output_dir.absolute()}")
        
        # List created files
        all_files = list(output_dir.rglob("*"))
        image_files = [f for f in all_files if f.suffix in ['.png', '.svg', '.pdf']]
        html_files = [f for f in all_files if f.suffix == '.html']
        
        print(f"📊 Created {len(image_files)} static plots")
        print(f"🌐 Created {len(html_files)} interactive plots")
        
        print("\nKey files to check out:")
        key_files = [
            "demo_throughput.png",
            "demo_heatmap.png", 
            "demo_dashboard.html",
            "demo_interactive_throughput.html"
        ]
        
        for filename in key_files:
            filepath = output_dir / filename
            if filepath.exists():
                print(f"  • {filename}")
        
        print(f"\n💡 To view HTML files, open them in a web browser")
        print(f"📖 See VISUALIZATION_README.md for detailed documentation")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up demo data
        shutil.rmtree(data_dir)
        logger.info("Cleaned up temporary demo data")


if __name__ == "__main__":
    main()