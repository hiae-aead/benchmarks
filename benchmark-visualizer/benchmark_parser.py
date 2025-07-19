"""
IETF Benchmark CSV Parser and Data Processing Module

This module provides comprehensive parsing and data processing capabilities for IETF 
cryptographic benchmark CSV files. It handles the specific format used by the benchmark
implementations in this repository.

CSV Format Handled:
- Comment lines starting with '#'
- Headers: Size,Operation,Gbps,MB/s,Cycles/Byte,CV%
- Multiple sections (Encryption Only, AEAD Performance, etc.)
- Empty/missing Cycles/Byte fields
- Algorithm name extraction from comments
"""

import csv
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkRecord:
    """Represents a single benchmark measurement record."""
    size: int
    operation: str
    gbps: float
    mb_s: float
    cycles_byte: Optional[float]
    cv_percent: Optional[float]
    section: str = ""
    
    def __post_init__(self):
        """Validate and clean data after initialization."""
        self.size = int(self.size)
        self.gbps = float(self.gbps)
        self.mb_s = float(self.mb_s)
        
        # Handle empty/missing cycles_byte
        if self.cycles_byte is not None and self.cycles_byte != "":
            try:
                self.cycles_byte = float(self.cycles_byte)
            except (ValueError, TypeError):
                self.cycles_byte = None
        else:
            self.cycles_byte = None
            
        # Handle CV percentage
        if self.cv_percent is not None and self.cv_percent != "":
            try:
                self.cv_percent = float(self.cv_percent)
            except (ValueError, TypeError):
                self.cv_percent = None
        else:
            self.cv_percent = None


@dataclass
class BenchmarkSection:
    """Represents a section of benchmark data (e.g., 'Encryption Only', 'AEAD Performance')."""
    name: str
    records: List[BenchmarkRecord] = field(default_factory=list)
    
    def get_operations(self) -> List[str]:
        """Get unique operations in this section."""
        return list(set(record.operation for record in self.records))
    
    def get_sizes(self) -> List[int]:
        """Get unique sizes in this section, sorted."""
        return sorted(list(set(record.size for record in self.records)))
    
    def filter_by_operation(self, operation: str) -> List[BenchmarkRecord]:
        """Get all records for a specific operation."""
        return [record for record in self.records if record.operation == operation]
    
    def filter_by_size(self, size: int) -> List[BenchmarkRecord]:
        """Get all records for a specific size."""
        return [record for record in self.records if record.size == size]


@dataclass
class BenchmarkData:
    """Complete benchmark data for a single algorithm/file."""
    algorithm: str
    filename: str
    sections: Dict[str, BenchmarkSection] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_section_names(self) -> List[str]:
        """Get names of all sections."""
        return list(self.sections.keys())
    
    def get_all_operations(self) -> List[str]:
        """Get all unique operations across all sections."""
        operations = set()
        for section in self.sections.values():
            operations.update(section.get_operations())
        return list(operations)
    
    def get_all_sizes(self) -> List[int]:
        """Get all unique sizes across all sections, sorted."""
        sizes = set()
        for section in self.sections.values():
            sizes.update(section.get_sizes())
        return sorted(list(sizes))
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame for analysis."""
        records = []
        for section_name, section in self.sections.items():
            for record in section.records:
                row = {
                    'algorithm': self.algorithm,
                    'section': section_name,
                    'size': record.size,
                    'operation': record.operation,
                    'gbps': record.gbps,
                    'mb_s': record.mb_s,
                    'cycles_byte': record.cycles_byte,
                    'cv_percent': record.cv_percent
                }
                records.append(row)
        return pd.DataFrame(records)


class BenchmarkCSVParser:
    """Parser for IETF benchmark CSV files."""
    
    def __init__(self):
        self.comment_pattern = re.compile(r'^#\s*(.+)')
        self.algorithm_patterns = [
            re.compile(r'Algorithm:\s*([^\s,]+)', re.IGNORECASE),
            re.compile(r'Testing\s+([^\s,]+)', re.IGNORECASE),
            re.compile(r'([a-zA-Z0-9_-]+)\s+benchmark', re.IGNORECASE),
            re.compile(r'([a-zA-Z0-9_-]+)\s+performance', re.IGNORECASE),
        ]
        
    def _extract_algorithm_name(self, comments: List[str], filename: str) -> str:
        """Extract algorithm name from comments or filename."""
        # Try to extract from comments first
        for comment in comments:
            for pattern in self.algorithm_patterns:
                match = pattern.search(comment)
                if match:
                    return match.group(1).strip()
        
        # Fall back to filename-based extraction
        path = Path(filename)
        name = path.stem
        
        # Remove common suffixes
        suffixes_to_remove = ['_benchmark', '_results', '_output', '_data']
        for suffix in suffixes_to_remove:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
                
        return name if name else "unknown"
    
    def _parse_section_header(self, comment: str) -> Optional[str]:
        """Parse section headers from comments."""
        # Common section patterns
        section_patterns = [
            r'(Encryption\s+Only)',
            r'(AEAD\s+Performance)',
            r'(Decryption\s+Only)',
            r'(Authentication\s+Only)', 
            r'(Key\s+Setup)',
            r'(Overall\s+Performance)',
            r'([A-Z][a-zA-Z\s]+Performance)',
            r'([A-Z][a-zA-Z\s]+Results)',
        ]
        
        for pattern in section_patterns:
            match = re.search(pattern, comment, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def parse_file(self, filepath: Union[str, Path]) -> BenchmarkData:
        """Parse a single CSV benchmark file."""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        logger.info(f"Parsing benchmark file: {filepath}")
        
        comments = []
        sections = {}
        current_section = "default"
        expected_headers = ['Size', 'Operation', 'Gbps', 'MB/s', 'Cycles/Byte', 'CV%']
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                
                for line_num, row in enumerate(reader, 1):
                    if not row or all(cell.strip() == '' for cell in row):
                        continue
                    
                    # Handle comment lines
                    if row[0].startswith('#'):
                        comment = row[0][1:].strip()
                        comments.append(comment)
                        
                        # Check for section headers
                        section_name = self._parse_section_header(comment)
                        if section_name:
                            current_section = section_name
                            if current_section not in sections:
                                sections[current_section] = BenchmarkSection(current_section)
                        
                        continue
                    
                    # Handle header row
                    if any(header.lower() in [cell.lower() for cell in row] for header in expected_headers):
                        continue
                    
                    # Parse data row
                    if len(row) >= 4:  # Minimum required columns
                        try:
                            # Ensure we have the current section
                            if current_section not in sections:
                                sections[current_section] = BenchmarkSection(current_section)
                            
                            # Parse with flexible column handling
                            size = row[0].strip()
                            operation = row[1].strip() if len(row) > 1 else ""
                            gbps = row[2].strip() if len(row) > 2 else "0"
                            mb_s = row[3].strip() if len(row) > 3 else "0"
                            cycles_byte = row[4].strip() if len(row) > 4 else None
                            cv_percent = row[5].strip() if len(row) > 5 else None
                            
                            record = BenchmarkRecord(
                                size=size,
                                operation=operation,
                                gbps=gbps,
                                mb_s=mb_s,
                                cycles_byte=cycles_byte,
                                cv_percent=cv_percent,
                                section=current_section
                            )
                            
                            sections[current_section].records.append(record)
                            
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Error parsing line {line_num} in {filepath}: {e}")
                            continue
        
        except Exception as e:
            raise RuntimeError(f"Error reading file {filepath}: {e}")
        
        # Extract algorithm name
        algorithm = self._extract_algorithm_name(comments, str(filepath))
        
        # Create benchmark data object
        benchmark_data = BenchmarkData(
            algorithm=algorithm,
            filename=str(filepath),
            sections=sections,
            metadata={
                'comments': comments,
                'total_records': sum(len(section.records) for section in sections.values()),
                'sections_count': len(sections)
            }
        )
        
        logger.info(f"Parsed {benchmark_data.metadata['total_records']} records "
                   f"in {benchmark_data.metadata['sections_count']} sections")
        
        return benchmark_data


class BenchmarkDataProcessor:
    """Advanced data processing and analysis for benchmark data."""
    
    def __init__(self):
        self.data_sets = {}
    
    def load_file(self, filepath: Union[str, Path], parser: Optional[BenchmarkCSVParser] = None) -> str:
        """Load a benchmark file and return its identifier."""
        if parser is None:
            parser = BenchmarkCSVParser()
        
        data = parser.parse_file(filepath)
        identifier = f"{data.algorithm}_{Path(filepath).stem}"
        self.data_sets[identifier] = data
        
        logger.info(f"Loaded dataset: {identifier}")
        return identifier
    
    def load_directory(self, directory: Union[str, Path], 
                      pattern: str = "*.csv") -> List[str]:
        """Load all CSV files from a directory."""
        directory = Path(directory)
        parser = BenchmarkCSVParser()
        loaded = []
        
        for filepath in directory.glob(pattern):
            try:
                identifier = self.load_file(filepath, parser)
                loaded.append(identifier)
            except Exception as e:
                logger.error(f"Failed to load {filepath}: {e}")
        
        logger.info(f"Loaded {len(loaded)} files from {directory}")
        return loaded
    
    def get_combined_dataframe(self, identifiers: Optional[List[str]] = None) -> pd.DataFrame:
        """Get combined DataFrame from multiple datasets."""
        if identifiers is None:
            identifiers = list(self.data_sets.keys())
        
        dataframes = []
        for identifier in identifiers:
            if identifier in self.data_sets:
                df = self.data_sets[identifier].to_dataframe()
                df['dataset_id'] = identifier
                dataframes.append(df)
        
        if not dataframes:
            return pd.DataFrame()
        
        return pd.concat(dataframes, ignore_index=True)
    
    def compare_algorithms(self, algorithms: List[str], 
                          operation: str = "encrypt", 
                          section: str = "default") -> pd.DataFrame:
        """Compare performance across algorithms for specific operation."""
        relevant_data = []
        
        for identifier, data in self.data_sets.items():
            if data.algorithm in algorithms and section in data.sections:
                records = data.sections[section].filter_by_operation(operation)
                for record in records:
                    relevant_data.append({
                        'algorithm': data.algorithm,
                        'size': record.size,
                        'gbps': record.gbps,
                        'mb_s': record.mb_s,
                        'cycles_byte': record.cycles_byte,
                        'cv_percent': record.cv_percent
                    })
        
        return pd.DataFrame(relevant_data)
    
    def get_performance_summary(self, identifier: str) -> Dict[str, Any]:
        """Get performance summary statistics for a dataset."""
        if identifier not in self.data_sets:
            raise ValueError(f"Dataset {identifier} not found")
        
        data = self.data_sets[identifier]
        df = data.to_dataframe()
        
        summary = {
            'algorithm': data.algorithm,
            'total_records': len(df),
            'sections': data.get_section_names(),
            'operations': data.get_all_operations(),
            'size_range': (min(data.get_all_sizes()), max(data.get_all_sizes())),
            'performance_stats': {}
        }
        
        # Calculate statistics by operation
        for operation in data.get_all_operations():
            op_data = df[df['operation'] == operation]
            if not op_data.empty:
                summary['performance_stats'][operation] = {
                    'avg_gbps': op_data['gbps'].mean(),
                    'max_gbps': op_data['gbps'].max(),
                    'min_gbps': op_data['gbps'].min(),
                    'avg_cycles_byte': op_data['cycles_byte'].mean() if op_data['cycles_byte'].notna().any() else None
                }
        
        return summary
    
    def export_processed_data(self, filepath: Union[str, Path], 
                            identifiers: Optional[List[str]] = None,
                            format: str = 'csv') -> None:
        """Export processed data to file."""
        df = self.get_combined_dataframe(identifiers)
        filepath = Path(filepath)
        
        if format.lower() == 'csv':
            df.to_csv(filepath, index=False)
        elif format.lower() == 'json':
            df.to_json(filepath, orient='records', indent=2)
        elif format.lower() == 'parquet':
            df.to_parquet(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Exported data to {filepath} in {format} format")


# Convenience functions for quick usage
def parse_benchmark_file(filepath: Union[str, Path]) -> BenchmarkData:
    """Quick function to parse a single benchmark file."""
    parser = BenchmarkCSVParser()
    return parser.parse_file(filepath)


def load_and_process_directory(directory: Union[str, Path], 
                              pattern: str = "*.csv") -> BenchmarkDataProcessor:
    """Quick function to load and process all CSV files in a directory."""
    processor = BenchmarkDataProcessor()
    processor.load_directory(directory, pattern)
    return processor


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        file_or_dir = Path(sys.argv[1])
        
        if file_or_dir.is_file():
            # Parse single file
            data = parse_benchmark_file(file_or_dir)
            print(f"Parsed {data.algorithm} with {len(data.get_all_operations())} operations")
            print(f"Sections: {data.get_section_names()}")
            print(f"Operations: {data.get_all_operations()}")
            
        elif file_or_dir.is_dir():
            # Process directory
            processor = load_and_process_directory(file_or_dir)
            print(f"Loaded {len(processor.data_sets)} datasets")
            
            for identifier in processor.data_sets:
                summary = processor.get_performance_summary(identifier)
                print(f"\n{summary['algorithm']}:")
                print(f"  Operations: {summary['operations']}")
                print(f"  Size range: {summary['size_range']}")
        else:
            print(f"Path not found: {file_or_dir}")
    else:
        print("Usage: python benchmark_parser.py <file_or_directory>")