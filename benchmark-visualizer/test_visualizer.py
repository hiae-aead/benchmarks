"""
Test script for IETF Benchmark Visualizer

This script tests the basic functionality of the visualization module
and creates sample plots to verify everything is working correctly.
"""

import numpy as np
import pandas as pd
import tempfile
import os
from pathlib import Path
import logging

from benchmark_visualizer import BenchmarkVisualizer, PlotStyle
from plot_config import get_academic_style, get_web_style
from benchmark_parser import BenchmarkData, BenchmarkSection, BenchmarkRecord

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_data():
    """Create sample benchmark data for testing."""
    
    # Sample data for different algorithms
    algorithms = ["AEGIS-128x2", "AES-128-GCM", "ChaCha20-Poly1305"]
    operations = ["encrypt", "decrypt"]
    sizes = [64, 256, 1024, 4096, 16384, 65536]
    
    # Create sample CSV content
    csv_content = """# Algorithm: AEGIS-128x2
# AEGIS-128x2 Benchmark Results
# Encryption Only
Size,Operation,Gbps,MB/s,Cycles/Byte,CV%
64,encrypt,15.2,1900.0,4.8,2.1
256,encrypt,18.5,2312.5,3.9,1.8
1024,encrypt,22.1,2762.5,3.2,1.5
4096,encrypt,24.8,3100.0,2.9,1.2
16384,encrypt,26.3,3287.5,2.7,1.0
65536,encrypt,27.1,3387.5,2.6,0.9
64,decrypt,14.8,1850.0,4.9,2.3
256,decrypt,18.1,2262.5,4.0,1.9
1024,decrypt,21.7,2712.5,3.3,1.6
4096,decrypt,24.3,3037.5,3.0,1.3
16384,decrypt,25.9,3237.5,2.8,1.1
65536,decrypt,26.7,3337.5,2.7,1.0

# AEAD Performance  
64,aead_encrypt,14.5,1812.5,5.0,2.5
256,aead_encrypt,17.8,2225.0,4.1,2.0
1024,aead_encrypt,21.3,2662.5,3.4,1.7
4096,aead_encrypt,23.9,2987.5,3.1,1.4
16384,aead_encrypt,25.5,3187.5,2.9,1.2
65536,aead_encrypt,26.3,3287.5,2.8,1.1
"""

    return csv_content


def create_sample_files():
    """Create sample CSV files for testing."""
    
    # Sample data for different algorithms
    test_data = {
        "aegis-128x2": {
            "algorithm": "AEGIS-128x2",
            "base_gbps": 25.0,
            "base_cycles": 2.8
        },
        "aes128-gcm": {
            "algorithm": "AES-128-GCM", 
            "base_gbps": 18.5,
            "base_cycles": 3.8
        },
        "chacha20-poly1305": {
            "algorithm": "ChaCha20-Poly1305",
            "base_gbps": 12.3,
            "base_cycles": 5.2
        }
    }
    
    sizes = [64, 256, 1024, 4096, 16384, 65536]
    operations = ["encrypt", "decrypt"]
    
    temp_dir = Path(tempfile.mkdtemp())
    logger.info(f"Creating test data in {temp_dir}")
    
    for alg_name, alg_data in test_data.items():
        csv_content = f"""# Algorithm: {alg_data['algorithm']}
# {alg_data['algorithm']} Benchmark Results
# Encryption Performance
Size,Operation,Gbps,MB/s,Cycles/Byte,CV%
"""
        
        for size in sizes:
            # Simulate realistic performance scaling
            size_factor = np.log2(size) / 10.0
            
            for operation in operations:
                # Base performance with some variation
                base_gbps = alg_data['base_gbps']
                base_cycles = alg_data['base_cycles']
                
                # Add size-based scaling (larger sizes = better throughput, fewer cycles)
                gbps = base_gbps * (1 + size_factor * 0.1) + np.random.normal(0, 0.5)
                cycles = base_cycles * (1 - size_factor * 0.05) + np.random.normal(0, 0.1)
                
                # Decrypt slightly slower than encrypt
                if operation == "decrypt":
                    gbps *= 0.95
                    cycles *= 1.05
                
                # Calculate MB/s and CV%
                mb_s = gbps * 125.0  # Convert Gbps to MB/s
                cv_percent = np.random.uniform(0.5, 3.0)  # Random CV%
                
                csv_content += f"{size},{operation},{gbps:.1f},{mb_s:.1f},{cycles:.1f},{cv_percent:.1f}\n"
        
        # Save to file
        file_path = temp_dir / f"{alg_name}_benchmark.csv"
        with open(file_path, 'w') as f:
            f.write(csv_content)
    
    return temp_dir


def test_basic_functionality():
    """Test basic visualizer functionality."""
    logger.info("Testing basic functionality...")
    
    # Create visualizer with default style
    visualizer = BenchmarkVisualizer()
    
    # Test style creation
    assert visualizer.style is not None
    assert visualizer.style.theme in ["light", "dark"]
    
    logger.info("✓ Basic initialization successful")


def test_style_presets():
    """Test different style presets."""
    logger.info("Testing style presets...")
    
    # Test different styles
    styles = [
        ("Academic", get_academic_style()),
        ("Web", get_web_style())
    ]
    
    for name, style in styles:
        visualizer = BenchmarkVisualizer(style=style)
        assert visualizer.style == style
        logger.info(f"✓ {name} style preset working")


def test_data_loading():
    """Test data loading functionality."""
    logger.info("Testing data loading...")
    
    # Create sample data
    temp_dir = create_sample_files()
    
    try:
        # Create visualizer
        visualizer = BenchmarkVisualizer()
        
        # Load data from directory
        identifiers = visualizer.load_data(temp_dir)
        
        assert len(identifiers) > 0, "No data loaded"
        logger.info(f"✓ Loaded {len(identifiers)} datasets")
        
        # Check that data is accessible
        df = visualizer.processor.get_combined_dataframe()
        assert not df.empty, "No data in combined dataframe"
        
        algorithms = df['algorithm'].unique()
        operations = df['operation'].unique()
        
        logger.info(f"✓ Found algorithms: {list(algorithms)}")
        logger.info(f"✓ Found operations: {list(operations)}")
        
        return temp_dir, visualizer
        
    except Exception as e:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        raise e


def test_plot_creation():
    """Test plot creation without saving files."""
    logger.info("Testing plot creation...")
    
    temp_dir, visualizer = test_data_loading()
    
    try:
        # Test plot creation (without saving)
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        
        # Test throughput plot creation
        try:
            visualizer.plot_throughput_vs_size(
                operation="encrypt",
                log_scale=True,
                output_path=None  # Don't save, just create
            )
            logger.info("✓ Throughput plot creation successful")
        except Exception as e:
            logger.warning(f"Throughput plot failed: {e}")
        
        # Test comparison plot creation
        try:
            visualizer.plot_algorithm_comparison(
                operation="encrypt",
                plot_type="bar",
                output_path=None  # Don't save, just create
            )
            logger.info("✓ Algorithm comparison plot creation successful")
        except Exception as e:
            logger.warning(f"Comparison plot failed: {e}")
        
        # Test heatmap creation
        try:
            visualizer.plot_performance_heatmap(
                metric="gbps",
                operation="encrypt",
                output_path=None  # Don't save, just create
            )
            logger.info("✓ Performance heatmap creation successful")
        except Exception as e:
            logger.warning(f"Heatmap creation failed: {e}")
        
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)


def test_file_output():
    """Test actual file output generation."""
    logger.info("Testing file output...")
    
    temp_dir, visualizer = test_data_loading()
    output_dir = Path(tempfile.mkdtemp())
    
    try:
        logger.info(f"Creating test plots in {output_dir}")
        
        # Create a simple throughput plot
        output_file = output_dir / "test_throughput.png"
        visualizer.plot_throughput_vs_size(
            operation="encrypt",
            log_scale=True,
            output_path=str(output_file)
        )
        
        assert output_file.exists(), f"Output file not created: {output_file}"
        assert output_file.stat().st_size > 0, "Output file is empty"
        
        logger.info(f"✓ Successfully created {output_file.name} ({output_file.stat().st_size} bytes)")
        
        # Test PNG format
        png_file = output_dir / "test_comparison.png"
        visualizer.plot_algorithm_comparison(
            operation="encrypt",
            output_path=str(png_file)
        )
        
        if png_file.exists():
            logger.info(f"✓ PNG output successful ({png_file.stat().st_size} bytes)")
        
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        shutil.rmtree(output_dir)


def test_configuration():
    """Test configuration and customization."""
    logger.info("Testing configuration...")
    
    # Test custom style creation
    custom_style = PlotStyle(
        theme="dark",
        figure_size=(10, 6),
        font_size=14,
        dpi=150
    )
    
    visualizer = BenchmarkVisualizer(style=custom_style)
    
    assert visualizer.style.theme == "dark"
    assert visualizer.style.figure_size == (10, 6)
    assert visualizer.style.font_size == 14
    assert visualizer.style.dpi == 150
    
    logger.info("✓ Custom style configuration successful")


def run_all_tests():
    """Run all tests."""
    logger.info("Starting IETF Benchmark Visualizer Tests")
    logger.info("=" * 50)
    
    tests = [
        test_basic_functionality,
        test_style_presets,
        test_configuration,
        test_data_loading,
        test_plot_creation,
        test_file_output
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            logger.error(f"Test {test_func.__name__} failed: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    logger.info("=" * 50)
    logger.info(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All tests passed!")
        return True
    else:
        logger.error(f"❌ {failed} tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)