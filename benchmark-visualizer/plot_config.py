"""
Plot Configuration Presets for IETF Benchmark Visualizer

This module provides predefined styling configurations for different use cases,
making it easy to create consistent, professional visualizations.
"""

from benchmark_visualizer import PlotStyle
from typing import Dict, Any


# Predefined color palettes
COLOR_PALETTES = {
    "academic": [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange  
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f',  # Gray
    ],
    "colorblind_friendly": [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f',  # Gray
    ],
    "high_contrast": [
        '#000000',  # Black
        '#FF0000',  # Red
        '#0000FF',  # Blue
        '#008000',  # Green
        '#800080',  # Purple
        '#FFA500',  # Orange
        '#A52A2A',  # Brown
        '#808080',  # Gray
    ],
    "pastel": [
        '#AEC7E8',  # Light Blue
        '#FFBB78',  # Light Orange
        '#98DF8A',  # Light Green
        '#FF9896',  # Light Red
        '#C5B0D5',  # Light Purple
        '#C49C94',  # Light Brown
        '#F7B6D3',  # Light Pink
        '#C7C7C7',  # Light Gray
    ],
    "dark_theme": [
        '#8DD3C7',  # Cyan
        '#FFFFB3',  # Yellow
        '#BEBADA',  # Purple
        '#FB8072',  # Red
        '#80B1D3',  # Blue
        '#FDB462',  # Orange
        '#B3DE69',  # Green
        '#FCCDE5',  # Pink
    ],
    "crypto_themed": [
        '#2E86AB',  # Deep Blue (Trust)
        '#A23B72',  # Magenta (Security)
        '#F18F01',  # Orange (Performance)
        '#C73E1D',  # Red (Critical)
        '#592E83',  # Purple (Advanced)
        '#1B998B',  # Teal (Efficiency)
        '#FF6B35',  # Coral (Speed)
        '#004E64',  # Navy (Reliability)
    ]
}


def get_academic_style() -> PlotStyle:
    """
    Academic paper style - suitable for IEEE, ACM publications.
    
    Features:
    - Times New Roman font
    - Conservative sizing
    - High DPI for crisp printing
    - Colorblind-friendly palette
    """
    return PlotStyle(
        theme="light",
        color_palette="colorblind",
        figure_size=(10, 6),
        dpi=600,
        font_family="Times New Roman",
        font_size=10,
        title_size=12,
        label_size=11,
        legend_size=9,
        grid_alpha=0.2,
        line_width=1.5,
        marker_size=4,
        colors=COLOR_PALETTES["colorblind_friendly"]
    )


def get_presentation_style() -> PlotStyle:
    """
    Presentation style - suitable for conference slides, talks.
    
    Features:
    - Large, bold fonts
    - High contrast colors
    - Thick lines for visibility
    """
    return PlotStyle(
        theme="light",
        color_palette="Set1",
        figure_size=(16, 10),
        dpi=150,
        font_family="Arial",
        font_size=16,
        title_size=24,
        label_size=20,
        legend_size=16,
        grid_alpha=0.3,
        line_width=4,
        marker_size=12,
        colors=COLOR_PALETTES["high_contrast"]
    )


def get_poster_style() -> PlotStyle:
    """
    Poster style - suitable for academic posters, large format prints.
    
    Features:
    - Very large fonts
    - Extra thick lines
    - High contrast for distance viewing
    """
    return PlotStyle(
        theme="light",
        color_palette="Set1",
        figure_size=(20, 12),
        dpi=300,
        font_family="Arial",
        font_size=20,
        title_size=32,
        label_size=24,
        legend_size=20,
        grid_alpha=0.4,
        line_width=5,
        marker_size=16,
        colors=COLOR_PALETTES["high_contrast"]
    )


def get_web_style() -> PlotStyle:
    """
    Web style - suitable for websites, blogs, online documentation.
    
    Features:
    - Web-safe fonts
    - Moderate sizing
    - Good contrast for screens
    """
    return PlotStyle(
        theme="light",
        color_palette="Set2",
        figure_size=(12, 8),
        dpi=100,
        font_family="Arial",
        font_size=12,
        title_size=16,
        label_size=14,
        legend_size=12,
        grid_alpha=0.3,
        line_width=2.5,
        marker_size=8,
        colors=COLOR_PALETTES["crypto_themed"]
    )


def get_dark_style() -> PlotStyle:
    """
    Dark theme style - suitable for dark mode interfaces, modern presentations.
    
    Features:
    - Dark background
    - Light text
    - Bright, contrasting colors
    """
    return PlotStyle(
        theme="dark",
        color_palette="bright",
        figure_size=(12, 8),
        dpi=150,
        font_family="Arial",
        font_size=12,
        title_size=16,
        label_size=14,
        legend_size=12,
        grid_alpha=0.3,
        line_width=2.5,
        marker_size=8,
        colors=COLOR_PALETTES["dark_theme"]
    )


def get_minimal_style() -> PlotStyle:
    """
    Minimal style - clean, simple, distraction-free.
    
    Features:
    - Minimal grid
    - Subtle colors
    - Clean typography
    """
    return PlotStyle(
        theme="light",
        color_palette="muted",
        figure_size=(10, 6),
        dpi=300,
        font_family="Arial",
        font_size=11,
        title_size=14,
        label_size=12,
        legend_size=10,
        grid_alpha=0.1,
        line_width=2,
        marker_size=6,
        colors=COLOR_PALETTES["pastel"]
    )


def get_high_contrast_style() -> PlotStyle:
    """
    High contrast style - suitable for accessibility, clear distinction.
    
    Features:
    - Maximum contrast
    - Bold lines and markers
    - Clear differentiation
    """
    return PlotStyle(
        theme="light",
        color_palette="bright",
        figure_size=(12, 8),
        dpi=300,
        font_family="Arial",
        font_size=14,
        title_size=18,
        label_size=16,
        legend_size=14,
        grid_alpha=0.4,
        line_width=3,
        marker_size=10,
        colors=COLOR_PALETTES["high_contrast"]
    )


def get_custom_style(style_name: str, **kwargs) -> PlotStyle:
    """
    Create a custom style based on a preset with overrides.
    
    Args:
        style_name: Base style name ("academic", "presentation", etc.)
        **kwargs: Style parameters to override
    
    Returns:
        PlotStyle with custom modifications
    """
    style_functions = {
        "academic": get_academic_style,
        "presentation": get_presentation_style,
        "poster": get_poster_style,
        "web": get_web_style,
        "dark": get_dark_style,
        "minimal": get_minimal_style,
        "high_contrast": get_high_contrast_style
    }
    
    if style_name not in style_functions:
        raise ValueError(f"Unknown style: {style_name}. Available: {list(style_functions.keys())}")
    
    # Get base style
    base_style = style_functions[style_name]()
    
    # Apply overrides
    for key, value in kwargs.items():
        if hasattr(base_style, key):
            setattr(base_style, key, value)
        else:
            raise ValueError(f"Unknown style parameter: {key}")
    
    return base_style


# Configuration presets for specific use cases
BENCHMARK_CONFIGS = {
    "throughput_analysis": {
        "log_scale": True,
        "show_confidence": True,
        "metric": "gbps"
    },
    "efficiency_analysis": {
        "log_scale": True,
        "show_confidence": False,
        "metric": "cycles_byte"
    },
    "consistency_analysis": {
        "log_scale": True,
        "show_confidence": False,
        "metric": "cv_percent"
    },
    "algorithm_comparison": {
        "plot_type": "violin",
        "metric": "gbps"
    },
    "operation_comparison": {
        "operations": ["encrypt", "decrypt"],
        "metric": "gbps"
    }
}


def get_benchmark_config(config_name: str) -> Dict[str, Any]:
    """
    Get predefined configuration for specific analysis types.
    
    Args:
        config_name: Configuration name
    
    Returns:
        Dictionary of configuration parameters
    """
    if config_name not in BENCHMARK_CONFIGS:
        raise ValueError(f"Unknown config: {config_name}. Available: {list(BENCHMARK_CONFIGS.keys())}")
    
    return BENCHMARK_CONFIGS[config_name].copy()


# Export format configurations
EXPORT_CONFIGS = {
    "publication": {
        "formats": ["pdf", "png", "svg"],
        "dpi": 600,
        "style": "academic"
    },
    "presentation": {
        "formats": ["png", "svg"],
        "dpi": 150,
        "style": "presentation"
    },
    "web": {
        "formats": ["png", "html"],
        "dpi": 100,
        "style": "web"
    },
    "poster": {
        "formats": ["pdf", "png"],
        "dpi": 300,
        "style": "poster"
    },
    "all": {
        "formats": ["png", "svg", "pdf", "html"],
        "dpi": 300,
        "style": "web"
    }
}


def get_export_config(config_name: str) -> Dict[str, Any]:
    """
    Get predefined export configuration.
    
    Args:
        config_name: Export configuration name
    
    Returns:
        Dictionary of export parameters
    """
    if config_name not in EXPORT_CONFIGS:
        raise ValueError(f"Unknown export config: {config_name}. Available: {list(EXPORT_CONFIGS.keys())}")
    
    return EXPORT_CONFIGS[config_name].copy()


if __name__ == "__main__":
    # Demonstrate style configurations
    print("Available Plot Styles:")
    print("=" * 30)
    
    styles = [
        ("Academic", get_academic_style()),
        ("Presentation", get_presentation_style()),
        ("Poster", get_poster_style()),
        ("Web", get_web_style()),
        ("Dark", get_dark_style()),
        ("Minimal", get_minimal_style()),
        ("High Contrast", get_high_contrast_style())
    ]
    
    for name, style in styles:
        print(f"{name}:")
        print(f"  Font: {style.font_family}, Size: {style.font_size}")
        print(f"  Figure: {style.figure_size}, DPI: {style.dpi}")
        print(f"  Theme: {style.theme}")
        print()
    
    print("Available Color Palettes:")
    print("=" * 30)
    for name, colors in COLOR_PALETTES.items():
        print(f"{name}: {len(colors)} colors")
    
    print("\nAvailable Benchmark Configs:")
    print("=" * 30)
    for name, config in BENCHMARK_CONFIGS.items():
        print(f"{name}: {config}")
    
    print("\nAvailable Export Configs:")
    print("=" * 30)
    for name, config in EXPORT_CONFIGS.items():
        print(f"{name}: {config}")