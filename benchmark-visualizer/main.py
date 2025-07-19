"""
Main CLI interface for IETF Benchmark Visualizer

This script provides a command-line interface for creating visualizations
from IETF cryptographic benchmark data.
"""

import argparse
import sys
from pathlib import Path
import logging

from benchmark_visualizer import BenchmarkVisualizer, quick_visualize
from plot_config import (
    get_academic_style, get_presentation_style, get_web_style, 
    get_dark_style, get_custom_style, get_export_config
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="IETF Benchmark Data Visualizer",
        epilog="""Examples:
  main.py data.csv -o plots/
  main.py benchmark_dir/ --style academic --format pdf
  main.py data.csv --interactive --dashboard""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Input/Output
    parser.add_argument("input", help="Input CSV file or directory containing CSV files")
    parser.add_argument("-o", "--output", default="plots", 
                       help="Output directory for plots (default: plots)")
    
    # Plot types
    parser.add_argument("--throughput", action="store_true",
                       help="Create throughput vs message size plots")
    parser.add_argument("--comparison", action="store_true",
                       help="Create algorithm comparison plots")
    parser.add_argument("--heatmap", action="store_true",
                       help="Create performance heatmap")
    parser.add_argument("--cycles", action="store_true",
                       help="Create cycles per byte analysis")
    parser.add_argument("--consistency", action="store_true",
                       help="Create consistency analysis (CV%%)")
    parser.add_argument("--operations", action="store_true",
                       help="Create operation comparison plots")
    parser.add_argument("--dashboard", action="store_true",
                       help="Create interactive dashboard")
    parser.add_argument("--all", action="store_true",
                       help="Create all plot types")
    
    # Styling
    parser.add_argument("--style", default="web",
                       choices=["academic", "presentation", "web", "dark", "minimal", "poster"],
                       help="Plot style preset (default: web)")
    parser.add_argument("--theme", choices=["light", "dark"],
                       help="Override theme (light/dark)")
    
    # Output formats
    parser.add_argument("--format", action="append",
                       choices=["png", "svg", "pdf", "html"],
                       help="Output format(s) - can be specified multiple times")
    parser.add_argument("--interactive", action="store_true",
                       help="Create interactive plots with Plotly")
    parser.add_argument("--dpi", type=int, default=300,
                       help="DPI for raster formats (default: 300)")
    
    # Filtering
    parser.add_argument("--algorithms", nargs="+",
                       help="Specific algorithms to include")
    parser.add_argument("--filter-operations", nargs="+", dest="op_filter",
                       help="Specific operations to include")
    parser.add_argument("--sizes", nargs="+", type=int,
                       help="Specific message sizes to include")
    
    # Analysis options
    parser.add_argument("--metric", default="gbps",
                       choices=["gbps", "mb_s", "cycles_byte"],
                       help="Primary metric for analysis (default: gbps)")
    parser.add_argument("--log-scale", action="store_true", default=True,
                       help="Use logarithmic scale for size axis")
    parser.add_argument("--confidence", action="store_true",
                       help="Show confidence intervals (CV%%) when available")
    
    # Quick mode
    parser.add_argument("--quick", action="store_true",
                       help="Quick mode: create basic visualizations with defaults")
    
    return parser


def main():
    """Main CLI function."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        if args.quick:
            # Quick mode
            logger.info("Running in quick mode...")
            visualizer = quick_visualize(
                data_path=input_path,
                output_dir=str(output_dir),
                theme=args.theme or "light"
            )
            
            if args.dashboard:
                dashboard_path = output_dir / "dashboard.html"
                visualizer.create_dashboard(str(dashboard_path))
                logger.info(f"Dashboard created: {dashboard_path}")
            
            logger.info(f"Quick visualization completed in {output_dir}")
            return
        
        # Full mode
        logger.info("Initializing visualizer...")
        
        # Get style configuration
        style_funcs = {
            "academic": get_academic_style,
            "presentation": get_presentation_style,
            "web": get_web_style,
            "dark": get_dark_style,
            "minimal": lambda: get_custom_style("minimal"),
            "poster": lambda: get_custom_style("poster")
        }
        
        style = style_funcs[args.style]()
        
        # Override theme if specified
        if args.theme:
            style.theme = args.theme
        
        # Override DPI if specified
        if args.dpi != 300:
            style.dpi = args.dpi
        
        # Create visualizer
        visualizer = BenchmarkVisualizer(style=style)
        
        # Load data
        logger.info(f"Loading data from {input_path}")
        identifiers = visualizer.load_data(input_path)
        logger.info(f"Loaded {len(identifiers)} datasets")
        
        # Determine output formats
        formats = args.format or ["png"]
        if args.interactive and "html" not in formats:
            formats.append("html")
        
        # Determine which plots to create
        create_plots = {
            "throughput": args.throughput or args.all,
            "comparison": args.comparison or args.all,
            "heatmap": args.heatmap or args.all,
            "cycles": args.cycles or args.all,
            "consistency": args.consistency or args.all,
            "operations": args.operations or args.all,
            "dashboard": args.dashboard or args.all
        }
        
        # If no specific plots requested, create basic set
        if not any(create_plots.values()):
            create_plots.update({
                "throughput": True,
                "comparison": True,
                "heatmap": True
            })
        
        # Create plots
        logger.info("Creating visualizations...")
        
        # Throughput plots
        if create_plots["throughput"]:
            for fmt in formats:
                interactive = fmt == "html" or args.interactive
                output_path = output_dir / f"throughput_encrypt.{fmt}"
                
                visualizer.plot_throughput_vs_size(
                    operation="encrypt",
                    log_scale=args.log_scale,
                    show_confidence=args.confidence,
                    output_path=str(output_path),
                    interactive=interactive
                )
        
        # Algorithm comparison
        if create_plots["comparison"]:
            for fmt in formats:
                interactive = fmt == "html" or args.interactive
                output_path = output_dir / f"algorithm_comparison.{fmt}"
                
                visualizer.plot_algorithm_comparison(
                    algorithms=args.algorithms,
                    operation="encrypt",
                    metric=args.metric,
                    plot_type="bar",
                    output_path=str(output_path),
                    interactive=interactive
                )
        
        # Performance heatmap
        if create_plots["heatmap"]:
            for fmt in formats:
                interactive = fmt == "html" or args.interactive
                output_path = output_dir / f"performance_heatmap.{fmt}"
                
                visualizer.plot_performance_heatmap(
                    metric=args.metric,
                    operation="encrypt",
                    output_path=str(output_path),
                    interactive=interactive
                )
        
        # Cycles per byte
        if create_plots["cycles"]:
            for fmt in formats:
                interactive = fmt == "html" or args.interactive
                output_path = output_dir / f"cycles_per_byte.{fmt}"
                
                visualizer.plot_cycles_per_byte(
                    algorithms=args.algorithms,
                    operation="encrypt",
                    output_path=str(output_path),
                    interactive=interactive
                )
        
        # Consistency analysis
        if create_plots["consistency"]:
            for fmt in formats:
                interactive = fmt == "html" or args.interactive
                output_path = output_dir / f"consistency_analysis.{fmt}"
                
                visualizer.plot_consistency_analysis(
                    algorithms=args.algorithms,
                    operation="encrypt",
                    output_path=str(output_path),
                    interactive=interactive
                )
        
        # Operation comparison (per algorithm)
        if create_plots["operations"]:
            df = visualizer.processor.get_combined_dataframe()
            algorithms = args.algorithms or df['algorithm'].unique()
            
            for algorithm in algorithms:
                for fmt in formats:
                    interactive = fmt == "html" or args.interactive
                    output_path = output_dir / f"operations_{algorithm}.{fmt}"
                    
                    try:
                        visualizer.plot_operation_comparison(
                            algorithm=algorithm,
                            metric=args.metric,
                            output_path=str(output_path),
                            interactive=interactive
                        )
                    except Exception as e:
                        logger.warning(f"Failed to create operation plot for {algorithm}: {e}")
        
        # Dashboard
        if create_plots["dashboard"]:
            dashboard_path = output_dir / "dashboard.html"
            visualizer.create_dashboard(
                output_path=str(dashboard_path),
                include_algorithms=args.algorithms
            )
            logger.info(f"Dashboard created: {dashboard_path}")
        
        logger.info(f"All visualizations completed successfully!")
        logger.info(f"Output directory: {output_dir}")
        
    except Exception as e:
        logger.error(f"Error during visualization: {e}")
        if args.verbose if hasattr(args, 'verbose') else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
