"""
IETF Benchmark Data Visualization Module

This module provides comprehensive visualization capabilities for IETF cryptographic 
benchmark data. It creates publication-ready graphs using matplotlib, seaborn, and plotly
with support for multiple output formats and beautiful styling.

Features:
- Multiple graph types (line plots, heatmaps, comparison charts)
- Professional styling with customizable themes
- Interactive and static plot generation
- Multi-format output (PNG, SVG, HTML, PDF)
- Seamless integration with benchmark_parser module
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
import logging
from dataclasses import dataclass, field
import warnings
warnings.filterwarnings('ignore')

from benchmark_parser import BenchmarkData, BenchmarkDataProcessor, parse_benchmark_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set default plotly template
pio.templates.default = "plotly_white"


@dataclass
class PlotStyle:
    """Configuration for plot styling and appearance."""
    theme: str = "light"  # "light" or "dark"
    color_palette: str = "Set2"  # seaborn palette name
    figure_size: Tuple[int, int] = (12, 8)
    dpi: int = 300
    font_family: str = "Arial"
    font_size: int = 12
    title_size: int = 16
    label_size: int = 14
    legend_size: int = 11
    grid_alpha: float = 0.3
    line_width: float = 2.5
    marker_size: float = 8
    colors: List[str] = field(default_factory=lambda: [
        '#2E86AB', '#A23B72', '#F18F01', '#C73E1D', 
        '#592E83', '#1B998B', '#FF6B35', '#004E64'
    ])
    
    def get_matplotlib_style(self) -> Dict[str, Any]:
        """Get matplotlib style configuration."""
        if self.theme == "dark":
            plt.style.use('dark_background')
            bg_color = '#2E2E2E'
            text_color = 'white'
        else:
            plt.style.use('default')
            bg_color = 'white'
            text_color = 'black'
        
        return {
            'figure.facecolor': bg_color,
            'axes.facecolor': bg_color,
            'text.color': text_color,
            'axes.labelcolor': text_color,
            'xtick.color': text_color,
            'ytick.color': text_color,
            'axes.edgecolor': text_color,
            'font.family': self.font_family,
            'font.size': self.font_size,
            'axes.titlesize': self.title_size,
            'axes.labelsize': self.label_size,
            'legend.fontsize': self.legend_size,
            'figure.figsize': self.figure_size,
            'figure.dpi': self.dpi,
            'lines.linewidth': self.line_width,
            'lines.markersize': self.marker_size,
            'grid.alpha': self.grid_alpha
        }
    
    def get_plotly_template(self) -> str:
        """Get plotly template name."""
        return "plotly_dark" if self.theme == "dark" else "plotly_white"


class BenchmarkVisualizer:
    """
    Comprehensive visualization toolkit for IETF benchmark data.
    
    Provides methods for creating various types of plots including throughput
    analysis, algorithm comparisons, performance heatmaps, and consistency analysis.
    """
    
    def __init__(self, style: Optional[PlotStyle] = None):
        """Initialize the visualizer with optional custom styling."""
        self.style = style or PlotStyle()
        self.processor = BenchmarkDataProcessor()
        
        # Apply matplotlib styling
        plt.rcParams.update(self.style.get_matplotlib_style())
        
        # Configure seaborn
        sns.set_palette(self.style.color_palette)
        
        logger.info(f"Initialized BenchmarkVisualizer with {self.style.theme} theme")
    
    def load_data(self, filepath_or_dir: Union[str, Path], 
                  pattern: str = "*.csv") -> List[str]:
        """Load benchmark data from file or directory."""
        path = Path(filepath_or_dir)
        
        if path.is_file():
            identifier = self.processor.load_file(path)
            return [identifier]
        elif path.is_dir():
            return self.processor.load_directory(path, pattern)
        else:
            raise ValueError(f"Path not found: {path}")
    
    def plot_throughput_vs_size(self, 
                                algorithm: Optional[str] = None,
                                operation: str = "encrypt",
                                section: str = "default",
                                log_scale: bool = True,
                                show_confidence: bool = True,
                                output_path: Optional[str] = None,
                                interactive: bool = False) -> None:
        """
        Create throughput vs message size plot.
        
        Args:
            algorithm: Specific algorithm to plot (None for all)
            operation: Operation type to plot
            section: Section name to use
            log_scale: Use logarithmic scale for x-axis
            show_confidence: Show confidence intervals using CV%
            output_path: Path to save the plot
            interactive: Create interactive plotly plot
        """
        # Get data
        df = self.processor.get_combined_dataframe()
        
        if df.empty:
            logger.warning("No data loaded for plotting")
            return
        
        # Filter data
        plot_data = df[df['operation'] == operation]
        if algorithm:
            plot_data = plot_data[plot_data['algorithm'] == algorithm]
        if section != "all":
            plot_data = plot_data[plot_data['section'] == section]
        
        if plot_data.empty:
            logger.warning(f"No data found for operation '{operation}' in section '{section}'")
            return
        
        if interactive:
            self._plot_throughput_interactive(plot_data, operation, log_scale, 
                                            show_confidence, output_path)
        else:
            self._plot_throughput_static(plot_data, operation, log_scale, 
                                       show_confidence, output_path)
    
    def _plot_throughput_static(self, data: pd.DataFrame, operation: str,
                               log_scale: bool, show_confidence: bool,
                               output_path: Optional[str]) -> None:
        """Create static matplotlib throughput plot."""
        fig, ax = plt.subplots(figsize=self.style.figure_size)
        
        algorithms = data['algorithm'].unique()
        colors = self.style.colors[:len(algorithms)]
        
        for i, algorithm in enumerate(algorithms):
            alg_data = data[data['algorithm'] == algorithm].sort_values('size')
            
            if alg_data.empty:
                continue
            
            color = colors[i % len(colors)]
            
            # Plot main line
            ax.plot(alg_data['size'], alg_data['gbps'], 
                   label=algorithm, color=color, 
                   linewidth=self.style.line_width,
                   marker='o', markersize=self.style.marker_size)
            
            # Add confidence intervals if available
            if show_confidence and 'cv_percent' in alg_data.columns:
                cv_data = alg_data.dropna(subset=['cv_percent'])
                if not cv_data.empty:
                    # Calculate confidence bounds (assuming CV% represents standard error)
                    cv_factor = cv_data['cv_percent'] / 100
                    lower_bound = cv_data['gbps'] * (1 - cv_factor)
                    upper_bound = cv_data['gbps'] * (1 + cv_factor)
                    
                    ax.fill_between(cv_data['size'], lower_bound, upper_bound,
                                   alpha=0.2, color=color)
        
        # Formatting
        if log_scale:
            ax.set_xscale('log')
            ax.set_xlabel('Message Size (bytes, log scale)', fontsize=self.style.label_size)
        else:
            ax.set_xlabel('Message Size (bytes)', fontsize=self.style.label_size)
        
        ax.set_ylabel('Throughput (Gbps)', fontsize=self.style.label_size)
        ax.set_title(f'Throughput vs Message Size - {operation.title()}',
                    fontsize=self.style.title_size, pad=20)
        
        ax.grid(True, alpha=self.style.grid_alpha)
        ax.legend(fontsize=self.style.legend_size, framealpha=0.9)
        
        # Improve layout
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=self.style.dpi, bbox_inches='tight')
            logger.info(f"Saved throughput plot to {output_path}")
        else:
            plt.show()
    
    def _plot_throughput_interactive(self, data: pd.DataFrame, operation: str,
                                   log_scale: bool, show_confidence: bool,
                                   output_path: Optional[str]) -> None:
        """Create interactive plotly throughput plot."""
        fig = go.Figure()
        
        algorithms = data['algorithm'].unique()
        colors = self.style.colors[:len(algorithms)]
        
        for i, algorithm in enumerate(algorithms):
            alg_data = data[data['algorithm'] == algorithm].sort_values('size')
            
            if alg_data.empty:
                continue
            
            color = colors[i % len(colors)]
            
            # Main line
            fig.add_trace(go.Scatter(
                x=alg_data['size'],
                y=alg_data['gbps'],
                mode='lines+markers',
                name=algorithm,
                line=dict(color=color, width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Size: %{x} bytes<br>' +
                             'Throughput: %{y:.2f} Gbps<br>' +
                             '<extra></extra>'
            ))
            
            # Add confidence intervals if available
            if show_confidence and 'cv_percent' in alg_data.columns:
                cv_data = alg_data.dropna(subset=['cv_percent'])
                if not cv_data.empty:
                    cv_factor = cv_data['cv_percent'] / 100
                    upper_bound = cv_data['gbps'] * (1 + cv_factor)
                    lower_bound = cv_data['gbps'] * (1 - cv_factor)
                    
                    # Upper bound
                    fig.add_trace(go.Scatter(
                        x=cv_data['size'],
                        y=upper_bound,
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                    
                    # Lower bound with fill
                    fig.add_trace(go.Scatter(
                        x=cv_data['size'],
                        y=lower_bound,
                        mode='lines',
                        line=dict(width=0),
                        fill='tonexty',
                        fillcolor=f"rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.2])}",
                        showlegend=False,
                        hoverinfo='skip'
                    ))
        
        # Layout
        fig.update_layout(
            title=f'Throughput vs Message Size - {operation.title()}',
            xaxis_title='Message Size (bytes)',
            yaxis_title='Throughput (Gbps)',
            template=self.style.get_plotly_template(),
            width=self.style.figure_size[0] * 80,
            height=self.style.figure_size[1] * 80,
            font=dict(family=self.style.font_family, size=self.style.font_size)
        )
        
        if log_scale:
            fig.update_xaxes(type="log", title_text="Message Size (bytes, log scale)")
        
        if output_path:
            if output_path.endswith('.html'):
                fig.write_html(output_path)
            else:
                fig.write_image(output_path, width=self.style.figure_size[0] * 80,
                               height=self.style.figure_size[1] * 80)
            logger.info(f"Saved interactive throughput plot to {output_path}")
        else:
            fig.show()
    
    def plot_algorithm_comparison(self,
                                 algorithms: Optional[List[str]] = None,
                                 operation: str = "encrypt",
                                 message_size: Optional[int] = None,
                                 metric: str = "gbps",
                                 plot_type: str = "bar",
                                 output_path: Optional[str] = None,
                                 interactive: bool = False) -> None:
        """
        Create algorithm comparison chart.
        
        Args:
            algorithms: List of algorithms to compare (None for all)
            operation: Operation type to compare
            message_size: Specific message size (None for all sizes)
            metric: Metric to compare ('gbps', 'mb_s', 'cycles_byte')
            plot_type: Type of plot ('bar', 'violin', 'box')
            output_path: Path to save the plot
            interactive: Create interactive plotly plot
        """
        df = self.processor.get_combined_dataframe()
        
        if df.empty:
            logger.warning("No data loaded for plotting")
            return
        
        # Filter data
        plot_data = df[df['operation'] == operation]
        if algorithms:
            plot_data = plot_data[plot_data['algorithm'].isin(algorithms)]
        if message_size:
            plot_data = plot_data[plot_data['size'] == message_size]
        
        plot_data = plot_data.dropna(subset=[metric])
        
        if plot_data.empty:
            logger.warning(f"No data found for comparison")
            return
        
        if interactive:
            self._plot_comparison_interactive(plot_data, operation, metric, 
                                            plot_type, output_path)
        else:
            self._plot_comparison_static(plot_data, operation, metric, 
                                       plot_type, output_path)
    
    def _plot_comparison_static(self, data: pd.DataFrame, operation: str,
                               metric: str, plot_type: str,
                               output_path: Optional[str]) -> None:
        """Create static matplotlib comparison plot."""
        fig, ax = plt.subplots(figsize=self.style.figure_size)
        
        metric_labels = {
            'gbps': 'Throughput (Gbps)',
            'mb_s': 'Throughput (MB/s)',
            'cycles_byte': 'Cycles per Byte'
        }
        
        if plot_type == "bar":
            # Aggregate data by algorithm (mean performance)
            agg_data = data.groupby('algorithm')[metric].mean().sort_values(ascending=False)
            bars = ax.bar(range(len(agg_data)), agg_data.values, 
                         color=self.style.colors[:len(agg_data)])
            ax.set_xticks(range(len(agg_data)))
            ax.set_xticklabels(agg_data.index, rotation=45, ha='right')
            
            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(bars, agg_data.values)):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{value:.2f}', ha='center', va='bottom')
        
        elif plot_type == "violin":
            sns.violinplot(data=data, x='algorithm', y=metric, ax=ax)
            plt.xticks(rotation=45, ha='right')
        
        elif plot_type == "box":
            sns.boxplot(data=data, x='algorithm', y=metric, ax=ax)
            plt.xticks(rotation=45, ha='right')
        
        ax.set_ylabel(metric_labels.get(metric, metric), fontsize=self.style.label_size)
        ax.set_xlabel('Algorithm', fontsize=self.style.label_size)
        ax.set_title(f'Algorithm Comparison - {operation.title()} ({metric_labels.get(metric, metric)})',
                    fontsize=self.style.title_size, pad=20)
        
        ax.grid(True, alpha=self.style.grid_alpha)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=self.style.dpi, bbox_inches='tight')
            logger.info(f"Saved comparison plot to {output_path}")
        else:
            plt.show()
    
    def _plot_comparison_interactive(self, data: pd.DataFrame, operation: str,
                                   metric: str, plot_type: str,
                                   output_path: Optional[str]) -> None:
        """Create interactive plotly comparison plot."""
        metric_labels = {
            'gbps': 'Throughput (Gbps)',
            'mb_s': 'Throughput (MB/s)',
            'cycles_byte': 'Cycles per Byte'
        }
        
        if plot_type == "bar":
            agg_data = data.groupby('algorithm')[metric].mean().sort_values(ascending=False)
            fig = px.bar(x=agg_data.index, y=agg_data.values,
                        labels={'x': 'Algorithm', 'y': metric_labels.get(metric, metric)},
                        title=f'Algorithm Comparison - {operation.title()}')
        elif plot_type == "violin":
            fig = px.violin(data, x='algorithm', y=metric,
                           labels={'algorithm': 'Algorithm', metric: metric_labels.get(metric, metric)},
                           title=f'Algorithm Comparison - {operation.title()}')
        elif plot_type == "box":
            fig = px.box(data, x='algorithm', y=metric,
                        labels={'algorithm': 'Algorithm', metric: metric_labels.get(metric, metric)},
                        title=f'Algorithm Comparison - {operation.title()}')
        
        fig.update_layout(
            template=self.style.get_plotly_template(),
            width=self.style.figure_size[0] * 80,
            height=self.style.figure_size[1] * 80,
            font=dict(family=self.style.font_family, size=self.style.font_size)
        )
        
        if output_path:
            if output_path.endswith('.html'):
                fig.write_html(output_path)
            else:
                fig.write_image(output_path)
            logger.info(f"Saved interactive comparison plot to {output_path}")
        else:
            fig.show()
    
    def plot_performance_heatmap(self,
                                metric: str = "gbps",
                                operation: str = "encrypt",
                                output_path: Optional[str] = None,
                                interactive: bool = False) -> None:
        """
        Create performance heatmap showing algorithm vs message size.
        
        Args:
            metric: Metric to visualize ('gbps', 'mb_s', 'cycles_byte')
            operation: Operation type to plot
            output_path: Path to save the plot
            interactive: Create interactive plotly plot
        """
        df = self.processor.get_combined_dataframe()
        
        if df.empty:
            logger.warning("No data loaded for plotting")
            return
        
        # Filter and prepare data
        plot_data = df[df['operation'] == operation].dropna(subset=[metric])
        
        if plot_data.empty:
            logger.warning(f"No data found for operation '{operation}'")
            return
        
        # Create pivot table
        heatmap_data = plot_data.pivot_table(
            values=metric, 
            index='algorithm', 
            columns='size', 
            aggfunc='mean'
        )
        
        if interactive:
            self._plot_heatmap_interactive(heatmap_data, metric, operation, output_path)
        else:
            self._plot_heatmap_static(heatmap_data, metric, operation, output_path)
    
    def _plot_heatmap_static(self, data: pd.DataFrame, metric: str,
                            operation: str, output_path: Optional[str]) -> None:
        """Create static matplotlib heatmap."""
        fig, ax = plt.subplots(figsize=(max(12, len(data.columns)), max(8, len(data.index))))
        
        metric_labels = {
            'gbps': 'Throughput (Gbps)',
            'mb_s': 'Throughput (MB/s)',
            'cycles_byte': 'Cycles per Byte'
        }
        
        # Create heatmap
        sns.heatmap(data, annot=True, fmt='.2f', cmap='viridis', 
                   cbar_kws={'label': metric_labels.get(metric, metric)},
                   ax=ax)
        
        ax.set_title(f'Performance Heatmap - {operation.title()} ({metric_labels.get(metric, metric)})',
                    fontsize=self.style.title_size, pad=20)
        ax.set_xlabel('Message Size (bytes)', fontsize=self.style.label_size)
        ax.set_ylabel('Algorithm', fontsize=self.style.label_size)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=self.style.dpi, bbox_inches='tight')
            logger.info(f"Saved heatmap to {output_path}")
        else:
            plt.show()
    
    def _plot_heatmap_interactive(self, data: pd.DataFrame, metric: str,
                                 operation: str, output_path: Optional[str]) -> None:
        """Create interactive plotly heatmap."""
        metric_labels = {
            'gbps': 'Throughput (Gbps)',
            'mb_s': 'Throughput (MB/s)',
            'cycles_byte': 'Cycles per Byte'
        }
        
        fig = go.Figure(data=go.Heatmap(
            z=data.values,
            x=data.columns,
            y=data.index,
            colorscale='Viridis',
            hoverongaps=False,
            hovertemplate='Algorithm: %{y}<br>Size: %{x} bytes<br>%{text}<extra></extra>',
            text=[[f'{metric_labels.get(metric, metric)}: {val:.2f}' for val in row] for row in data.values]
        ))
        
        fig.update_layout(
            title=f'Performance Heatmap - {operation.title()} ({metric_labels.get(metric, metric)})',
            xaxis_title='Message Size (bytes)',
            yaxis_title='Algorithm',
            template=self.style.get_plotly_template(),
            width=max(800, len(data.columns) * 60),
            height=max(600, len(data.index) * 40),
            font=dict(family=self.style.font_family, size=self.style.font_size)
        )
        
        if output_path:
            if output_path.endswith('.html'):
                fig.write_html(output_path)
            else:
                fig.write_image(output_path)
            logger.info(f"Saved interactive heatmap to {output_path}")
        else:
            fig.show()
    
    def plot_cycles_per_byte(self,
                            algorithms: Optional[List[str]] = None,
                            operation: str = "encrypt",
                            output_path: Optional[str] = None,
                            interactive: bool = False) -> None:
        """
        Create cycles per byte analysis plot.
        
        Args:
            algorithms: List of algorithms to include (None for all)
            operation: Operation type to plot
            output_path: Path to save the plot
            interactive: Create interactive plotly plot
        """
        df = self.processor.get_combined_dataframe()
        
        if df.empty:
            logger.warning("No data loaded for plotting")
            return
        
        # Filter data
        plot_data = df[df['operation'] == operation].dropna(subset=['cycles_byte'])
        if algorithms:
            plot_data = plot_data[plot_data['algorithm'].isin(algorithms)]
        
        if plot_data.empty:
            logger.warning(f"No cycles/byte data found for operation '{operation}'")
            return
        
        if interactive:
            self._plot_cycles_interactive(plot_data, operation, output_path)
        else:
            self._plot_cycles_static(plot_data, operation, output_path)
    
    def _plot_cycles_static(self, data: pd.DataFrame, operation: str,
                           output_path: Optional[str]) -> None:
        """Create static matplotlib cycles per byte plot."""
        fig, ax = plt.subplots(figsize=self.style.figure_size)
        
        algorithms = data['algorithm'].unique()
        colors = self.style.colors[:len(algorithms)]
        
        for i, algorithm in enumerate(algorithms):
            alg_data = data[data['algorithm'] == algorithm].sort_values('size')
            
            if alg_data.empty:
                continue
            
            color = colors[i % len(colors)]
            ax.plot(alg_data['size'], alg_data['cycles_byte'], 
                   label=algorithm, color=color,
                   linewidth=self.style.line_width,
                   marker='o', markersize=self.style.marker_size)
        
        ax.set_xscale('log')
        ax.set_xlabel('Message Size (bytes, log scale)', fontsize=self.style.label_size)
        ax.set_ylabel('Cycles per Byte', fontsize=self.style.label_size)
        ax.set_title(f'Cycles per Byte - {operation.title()}',
                    fontsize=self.style.title_size, pad=20)
        
        ax.grid(True, alpha=self.style.grid_alpha)
        ax.legend(fontsize=self.style.legend_size, framealpha=0.9)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=self.style.dpi, bbox_inches='tight')
            logger.info(f"Saved cycles per byte plot to {output_path}")
        else:
            plt.show()
    
    def _plot_cycles_interactive(self, data: pd.DataFrame, operation: str,
                                output_path: Optional[str]) -> None:
        """Create interactive plotly cycles per byte plot."""
        fig = go.Figure()
        
        algorithms = data['algorithm'].unique()
        colors = self.style.colors[:len(algorithms)]
        
        for i, algorithm in enumerate(algorithms):
            alg_data = data[data['algorithm'] == algorithm].sort_values('size')
            
            if alg_data.empty:
                continue
            
            color = colors[i % len(colors)]
            
            fig.add_trace(go.Scatter(
                x=alg_data['size'],
                y=alg_data['cycles_byte'],
                mode='lines+markers',
                name=algorithm,
                line=dict(color=color, width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Size: %{x} bytes<br>' +
                             'Cycles/Byte: %{y:.2f}<br>' +
                             '<extra></extra>'
            ))
        
        fig.update_layout(
            title=f'Cycles per Byte - {operation.title()}',
            xaxis_title='Message Size (bytes, log scale)',
            yaxis_title='Cycles per Byte',
            xaxis_type="log",
            template=self.style.get_plotly_template(),
            width=self.style.figure_size[0] * 80,
            height=self.style.figure_size[1] * 80,
            font=dict(family=self.style.font_family, size=self.style.font_size)
        )
        
        if output_path:
            if output_path.endswith('.html'):
                fig.write_html(output_path)
            else:
                fig.write_image(output_path)
            logger.info(f"Saved interactive cycles per byte plot to {output_path}")
        else:
            fig.show()
    
    def plot_consistency_analysis(self,
                                 algorithms: Optional[List[str]] = None,
                                 operation: str = "encrypt",
                                 output_path: Optional[str] = None,
                                 interactive: bool = False) -> None:
        """
        Create coefficient of variation (consistency) analysis plot.
        
        Args:
            algorithms: List of algorithms to include (None for all)
            operation: Operation type to plot
            output_path: Path to save the plot
            interactive: Create interactive plotly plot
        """
        df = self.processor.get_combined_dataframe()
        
        if df.empty:
            logger.warning("No data loaded for plotting")
            return
        
        # Filter data
        plot_data = df[df['operation'] == operation].dropna(subset=['cv_percent'])
        if algorithms:
            plot_data = plot_data[plot_data['algorithm'].isin(algorithms)]
        
        if plot_data.empty:
            logger.warning(f"No CV% data found for operation '{operation}'")
            return
        
        if interactive:
            self._plot_consistency_interactive(plot_data, operation, output_path)
        else:
            self._plot_consistency_static(plot_data, operation, output_path)
    
    def _plot_consistency_static(self, data: pd.DataFrame, operation: str,
                                output_path: Optional[str]) -> None:
        """Create static matplotlib consistency plot."""
        fig, ax = plt.subplots(figsize=self.style.figure_size)
        
        algorithms = data['algorithm'].unique()
        colors = self.style.colors[:len(algorithms)]
        
        for i, algorithm in enumerate(algorithms):
            alg_data = data[data['algorithm'] == algorithm].sort_values('size')
            
            if alg_data.empty:
                continue
            
            color = colors[i % len(colors)]
            ax.plot(alg_data['size'], alg_data['cv_percent'], 
                   label=algorithm, color=color,
                   linewidth=self.style.line_width,
                   marker='o', markersize=self.style.marker_size)
        
        ax.set_xscale('log')
        ax.set_xlabel('Message Size (bytes, log scale)', fontsize=self.style.label_size)
        ax.set_ylabel('Coefficient of Variation (%)', fontsize=self.style.label_size)
        ax.set_title(f'Performance Consistency - {operation.title()}',
                    fontsize=self.style.title_size, pad=20)
        
        # Add reference line for good consistency (< 5%)
        ax.axhline(y=5, color='red', linestyle='--', alpha=0.7, label='5% threshold')
        
        ax.grid(True, alpha=self.style.grid_alpha)
        ax.legend(fontsize=self.style.legend_size, framealpha=0.9)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=self.style.dpi, bbox_inches='tight')
            logger.info(f"Saved consistency plot to {output_path}")
        else:
            plt.show()
    
    def _plot_consistency_interactive(self, data: pd.DataFrame, operation: str,
                                     output_path: Optional[str]) -> None:
        """Create interactive plotly consistency plot."""
        fig = go.Figure()
        
        algorithms = data['algorithm'].unique()
        colors = self.style.colors[:len(algorithms)]
        
        for i, algorithm in enumerate(algorithms):
            alg_data = data[data['algorithm'] == algorithm].sort_values('size')
            
            if alg_data.empty:
                continue
            
            color = colors[i % len(colors)]
            
            fig.add_trace(go.Scatter(
                x=alg_data['size'],
                y=alg_data['cv_percent'],
                mode='lines+markers',
                name=algorithm,
                line=dict(color=color, width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Size: %{x} bytes<br>' +
                             'CV: %{y:.2f}%<br>' +
                             '<extra></extra>'
            ))
        
        # Add reference line
        fig.add_hline(y=5, line_dash="dash", line_color="red", 
                     annotation_text="5% threshold", annotation_position="bottom right")
        
        fig.update_layout(
            title=f'Performance Consistency - {operation.title()}',
            xaxis_title='Message Size (bytes, log scale)',
            yaxis_title='Coefficient of Variation (%)',
            xaxis_type="log",
            template=self.style.get_plotly_template(),
            width=self.style.figure_size[0] * 80,
            height=self.style.figure_size[1] * 80,
            font=dict(family=self.style.font_family, size=self.style.font_size)
        )
        
        if output_path:
            if output_path.endswith('.html'):
                fig.write_html(output_path)
            else:
                fig.write_image(output_path)
            logger.info(f"Saved interactive consistency plot to {output_path}")
        else:
            fig.show()
    
    def plot_operation_comparison(self,
                                 algorithm: str,
                                 operations: Optional[List[str]] = None,
                                 metric: str = "gbps",
                                 output_path: Optional[str] = None,
                                 interactive: bool = False) -> None:
        """
        Compare different operations (encrypt vs decrypt) for a single algorithm.
        
        Args:
            algorithm: Algorithm to analyze
            operations: List of operations to compare (None for all available)
            metric: Metric to compare ('gbps', 'mb_s', 'cycles_byte')
            output_path: Path to save the plot
            interactive: Create interactive plotly plot
        """
        df = self.processor.get_combined_dataframe()
        
        if df.empty:
            logger.warning("No data loaded for plotting")
            return
        
        # Filter data
        plot_data = df[df['algorithm'] == algorithm].dropna(subset=[metric])
        if operations:
            plot_data = plot_data[plot_data['operation'].isin(operations)]
        
        if plot_data.empty:
            logger.warning(f"No data found for algorithm '{algorithm}'")
            return
        
        if interactive:
            self._plot_operation_comparison_interactive(plot_data, algorithm, metric, output_path)
        else:
            self._plot_operation_comparison_static(plot_data, algorithm, metric, output_path)
    
    def _plot_operation_comparison_static(self, data: pd.DataFrame, algorithm: str,
                                         metric: str, output_path: Optional[str]) -> None:
        """Create static matplotlib operation comparison plot."""
        fig, ax = plt.subplots(figsize=self.style.figure_size)
        
        metric_labels = {
            'gbps': 'Throughput (Gbps)',
            'mb_s': 'Throughput (MB/s)',
            'cycles_byte': 'Cycles per Byte'
        }
        
        operations = data['operation'].unique()
        colors = self.style.colors[:len(operations)]
        
        for i, operation in enumerate(operations):
            op_data = data[data['operation'] == operation].sort_values('size')
            
            if op_data.empty:
                continue
            
            color = colors[i % len(colors)]
            ax.plot(op_data['size'], op_data[metric], 
                   label=operation.title(), color=color,
                   linewidth=self.style.line_width,
                   marker='o', markersize=self.style.marker_size)
        
        ax.set_xscale('log')
        ax.set_xlabel('Message Size (bytes, log scale)', fontsize=self.style.label_size)
        ax.set_ylabel(metric_labels.get(metric, metric), fontsize=self.style.label_size)
        ax.set_title(f'Operation Comparison - {algorithm} ({metric_labels.get(metric, metric)})',
                    fontsize=self.style.title_size, pad=20)
        
        ax.grid(True, alpha=self.style.grid_alpha)
        ax.legend(fontsize=self.style.legend_size, framealpha=0.9)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=self.style.dpi, bbox_inches='tight')
            logger.info(f"Saved operation comparison plot to {output_path}")
        else:
            plt.show()
    
    def _plot_operation_comparison_interactive(self, data: pd.DataFrame, algorithm: str,
                                              metric: str, output_path: Optional[str]) -> None:
        """Create interactive plotly operation comparison plot."""
        metric_labels = {
            'gbps': 'Throughput (Gbps)',
            'mb_s': 'Throughput (MB/s)',
            'cycles_byte': 'Cycles per Byte'
        }
        
        fig = go.Figure()
        
        operations = data['operation'].unique()
        colors = self.style.colors[:len(operations)]
        
        for i, operation in enumerate(operations):
            op_data = data[data['operation'] == operation].sort_values('size')
            
            if op_data.empty:
                continue
            
            color = colors[i % len(colors)]
            
            fig.add_trace(go.Scatter(
                x=op_data['size'],
                y=op_data[metric],
                mode='lines+markers',
                name=operation.title(),
                line=dict(color=color, width=3),
                marker=dict(size=8),
                hovertemplate=f'<b>%{{fullData.name}}</b><br>' +
                             'Size: %{x} bytes<br>' +
                             f'{metric_labels.get(metric, metric)}: %{{y:.2f}}<br>' +
                             '<extra></extra>'
            ))
        
        fig.update_layout(
            title=f'Operation Comparison - {algorithm} ({metric_labels.get(metric, metric)})',
            xaxis_title='Message Size (bytes, log scale)',
            yaxis_title=metric_labels.get(metric, metric),
            xaxis_type="log",
            template=self.style.get_plotly_template(),
            width=self.style.figure_size[0] * 80,
            height=self.style.figure_size[1] * 80,
            font=dict(family=self.style.font_family, size=self.style.font_size)
        )
        
        if output_path:
            if output_path.endswith('.html'):
                fig.write_html(output_path)
            else:
                fig.write_image(output_path)
            logger.info(f"Saved interactive operation comparison plot to {output_path}")
        else:
            fig.show()
    
    def create_dashboard(self,
                        output_path: str = "benchmark_dashboard.html",
                        include_algorithms: Optional[List[str]] = None) -> None:
        """
        Create a comprehensive dashboard with multiple visualizations.
        
        Args:
            output_path: Path to save the HTML dashboard
            include_algorithms: List of algorithms to include (None for all)
        """
        df = self.processor.get_combined_dataframe()
        
        if df.empty:
            logger.warning("No data loaded for dashboard")
            return
        
        if include_algorithms:
            df = df[df['algorithm'].isin(include_algorithms)]
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=("Throughput vs Size (Encrypt)", "Algorithm Comparison (Encrypt)",
                           "Performance Heatmap", "Cycles per Byte",
                           "Consistency Analysis", "Operation Comparison"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        algorithms = df['algorithm'].unique()
        colors = px.colors.qualitative.Set2
        # Extend colors if we have more algorithms than available colors
        while len(colors) < len(algorithms):
            colors.extend(px.colors.qualitative.Set2)
        
        # 1. Throughput vs Size (Encrypt)
        encrypt_data = df[df['operation'] == 'encrypt']
        for i, algorithm in enumerate(algorithms):
            alg_data = encrypt_data[encrypt_data['algorithm'] == algorithm].sort_values('size')
            if not alg_data.empty:
                color_idx = i % len(colors)  # Wrap around if more algorithms than colors
                fig.add_trace(
                    go.Scatter(x=alg_data['size'], y=alg_data['gbps'],
                              mode='lines+markers', name=algorithm,
                              line=dict(color=colors[color_idx]), showlegend=True),
                    row=1, col=1
                )
        
        # 2. Algorithm Comparison (Bar chart)
        avg_perf = encrypt_data.groupby('algorithm')['gbps'].mean().sort_values(ascending=False)
        bar_colors = [colors[i % len(colors)] for i in range(len(avg_perf))]
        fig.add_trace(
            go.Bar(x=avg_perf.index, y=avg_perf.values, 
                   marker_color=bar_colors, showlegend=False),
            row=1, col=2
        )
        
        # 3. Performance Heatmap
        heatmap_data = encrypt_data.pivot_table(values='gbps', index='algorithm', 
                                               columns='size', aggfunc='mean')
        fig.add_trace(
            go.Heatmap(z=heatmap_data.values, x=heatmap_data.columns, 
                      y=heatmap_data.index, colorscale='Viridis', showlegend=False),
            row=2, col=1
        )
        
        # 4. Cycles per Byte
        cycles_data = df[df['operation'] == 'encrypt'].dropna(subset=['cycles_byte'])
        for i, algorithm in enumerate(algorithms):
            alg_data = cycles_data[cycles_data['algorithm'] == algorithm].sort_values('size')
            if not alg_data.empty:
                color_idx = i % len(colors)  # Wrap around if more algorithms than colors
                fig.add_trace(
                    go.Scatter(x=alg_data['size'], y=alg_data['cycles_byte'],
                              mode='lines+markers', name=algorithm,
                              line=dict(color=colors[color_idx]), showlegend=False),
                    row=2, col=2
                )
        
        # 5. Consistency Analysis
        cv_data = df[df['operation'] == 'encrypt'].dropna(subset=['cv_percent'])
        for i, algorithm in enumerate(algorithms):
            alg_data = cv_data[cv_data['algorithm'] == algorithm].sort_values('size')
            if not alg_data.empty:
                color_idx = i % len(colors)  # Wrap around if more algorithms than colors
                fig.add_trace(
                    go.Scatter(x=alg_data['size'], y=alg_data['cv_percent'],
                              mode='lines+markers', name=algorithm,
                              line=dict(color=colors[color_idx]), showlegend=False),
                    row=3, col=1
                )
        
        # 6. Operation Comparison (first algorithm)
        if len(algorithms) > 0:
            first_alg = algorithms[0]
            alg_data = df[df['algorithm'] == first_alg]
            operations = alg_data['operation'].unique()
            for i, operation in enumerate(operations):
                op_data = alg_data[alg_data['operation'] == operation].sort_values('size')
                if not op_data.empty:
                    color_idx = i % len(colors)  # Wrap around if more operations than colors
                    fig.add_trace(
                        go.Scatter(x=op_data['size'], y=op_data['gbps'],
                                  mode='lines+markers', name=f"{first_alg} - {operation}",
                                  line=dict(color=colors[color_idx]), showlegend=False),
                        row=3, col=2
                    )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="IETF Benchmark Performance Dashboard",
            template=self.style.get_plotly_template(),
            font=dict(family=self.style.font_family, size=self.style.font_size)
        )
        
        # Update axes
        for row in range(1, 4):
            for col in range(1, 3):
                if row == 1 and col == 1:  # Throughput plot
                    fig.update_xaxes(type="log", title_text="Message Size (bytes)", row=row, col=col)
                    fig.update_yaxes(title_text="Throughput (Gbps)", row=row, col=col)
                elif row == 1 and col == 2:  # Bar chart
                    fig.update_yaxes(title_text="Avg Throughput (Gbps)", row=row, col=col)
                elif row == 2 and col == 1:  # Heatmap
                    fig.update_xaxes(title_text="Message Size", row=row, col=col)
                    fig.update_yaxes(title_text="Algorithm", row=row, col=col)
                elif row == 2 and col == 2:  # Cycles
                    fig.update_xaxes(type="log", title_text="Message Size (bytes)", row=row, col=col)
                    fig.update_yaxes(title_text="Cycles per Byte", row=row, col=col)
                elif row == 3 and col == 1:  # CV%
                    fig.update_xaxes(type="log", title_text="Message Size (bytes)", row=row, col=col)
                    fig.update_yaxes(title_text="CV (%)", row=row, col=col)
                elif row == 3 and col == 2:  # Operations
                    fig.update_xaxes(type="log", title_text="Message Size (bytes)", row=row, col=col)
                    fig.update_yaxes(title_text="Throughput (Gbps)", row=row, col=col)
        
        # Save dashboard
        fig.write_html(output_path)
        logger.info(f"Saved comprehensive dashboard to {output_path}")
    
    def export_plots_batch(self,
                          output_dir: str = "plots",
                          formats: List[str] = ["png", "svg"],
                          interactive: bool = True) -> None:
        """
        Export all plot types in batch for all loaded algorithms.
        
        Args:
            output_dir: Directory to save plots
            formats: List of formats to export ('png', 'svg', 'html', 'pdf')
            interactive: Whether to create interactive versions
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        df = self.processor.get_combined_dataframe()
        if df.empty:
            logger.warning("No data loaded for batch export")
            return
        
        algorithms = df['algorithm'].unique()
        operations = df['operation'].unique()
        
        plot_functions = [
            ("throughput_vs_size", self.plot_throughput_vs_size),
            ("algorithm_comparison", self.plot_algorithm_comparison),
            ("performance_heatmap", self.plot_performance_heatmap),
            ("cycles_per_byte", self.plot_cycles_per_byte),
            ("consistency_analysis", self.plot_consistency_analysis)
        ]
        
        for plot_name, plot_func in plot_functions:
            for operation in operations:
                for fmt in formats:
                    # Static plots
                    filename = f"{plot_name}_{operation}.{fmt}"
                    filepath = output_path / filename
                    
                    try:
                        if plot_name == "algorithm_comparison":
                            plot_func(operation=operation, output_path=str(filepath), 
                                    interactive=(fmt == "html"))
                        else:
                            plot_func(operation=operation, output_path=str(filepath), 
                                    interactive=(fmt == "html"))
                    except Exception as e:
                        logger.error(f"Failed to create {filename}: {e}")
        
        # Operation comparison for each algorithm
        for algorithm in algorithms:
            for fmt in formats:
                filename = f"operation_comparison_{algorithm}.{fmt}"
                filepath = output_path / filename
                
                try:
                    self.plot_operation_comparison(algorithm=algorithm, 
                                                 output_path=str(filepath),
                                                 interactive=(fmt == "html"))
                except Exception as e:
                    logger.error(f"Failed to create {filename}: {e}")
        
        # Dashboard
        if interactive:
            dashboard_path = output_path / "dashboard.html"
            try:
                self.create_dashboard(str(dashboard_path))
            except Exception as e:
                logger.error(f"Failed to create dashboard: {e}")
        
        logger.info(f"Batch export completed. Files saved to {output_path}")


# Convenience functions for quick usage
def quick_visualize(data_path: Union[str, Path], 
                   output_dir: str = "plots",
                   theme: str = "light") -> BenchmarkVisualizer:
    """
    Quick function to load data and create basic visualizations.
    
    Args:
        data_path: Path to CSV file or directory containing CSV files
        output_dir: Directory to save plots
        theme: Visual theme ("light" or "dark")
    
    Returns:
        BenchmarkVisualizer instance for further customization
    """
    style = PlotStyle(theme=theme)
    visualizer = BenchmarkVisualizer(style)
    
    # Load data
    visualizer.load_data(data_path)
    
    # Create basic plots
    Path(output_dir).mkdir(exist_ok=True)
    
    # Throughput plot
    visualizer.plot_throughput_vs_size(
        output_path=f"{output_dir}/throughput_encrypt.png"
    )
    
    # Algorithm comparison
    visualizer.plot_algorithm_comparison(
        output_path=f"{output_dir}/algorithm_comparison.png"
    )
    
    # Performance heatmap
    visualizer.plot_performance_heatmap(
        output_path=f"{output_dir}/performance_heatmap.png"
    )
    
    return visualizer


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "example_plots"
        
        # Create visualizations
        visualizer = quick_visualize(data_path, output_dir)
        
        # Create interactive dashboard
        visualizer.create_dashboard(f"{output_dir}/dashboard.html")
        
        print(f"Visualizations created in {output_dir}/")
    else:
        print("Usage: python benchmark_visualizer.py <data_path> [output_dir]")
        print("Example: python benchmark_visualizer.py ../aegis-benchmark-results/ plots/")