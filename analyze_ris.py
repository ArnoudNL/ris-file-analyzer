#!/usr/bin/env python3
"""
RIS File Analyzer - Extracts and reports data from RIS (Research Information Systems) files
"""

import collections
import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple


class RISAnalyzer:
    """Analyzes RIS citation files for duplicates and metadata extraction"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.records = []
        self.titles = []
        self.databases = []
        self.journals = []
        self.dois = []  # Store title, authors, and DOI tuples
        self.title_counts = collections.Counter()  # Track frequency of each title
        
    def read_file(self) -> bool:
        """Read and parse the RIS file"""
        if not self.file_path.exists():
            print(f"Error: File not found at {self.file_path}")
            return False
        
        try:
            # Try UTF-8 with BOM first, then fall back to UTF-8
            with open(self.file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                # Fall back to UTF-8 without BOM
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    # Try latin-1 as last resort
                    with open(self.file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    print(f"Error reading file: {e}")
                    return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
        
        # Split by the "End of Record" tag
        self.records = content.split('ER  -')
        return True
    
    def extract_field(self, record: str, field_patterns: List[str]) -> str:
        """Extract a field from a record using multiple possible patterns"""
        for pattern in field_patterns:
            match = re.search(rf'^{pattern}\s+-\s+(.*)$', record, re.MULTILINE)
            if match:
                return match.group(1).strip()
        return "Not Specified"
    
    def extract_authors(self, record: str) -> str:
        """Extract all authors from a record and join them"""
        matches = re.findall(r'^AU\s+-\s+(.*)$', record, re.MULTILINE)
        if matches:
            return "; ".join(matches)
        return "Not Specified"
    
    def parse_records(self):
        """Parse individual records and extract metadata"""
        for record in self.records:
            if not record.strip():
                continue
            
            # Extract Title
            title = self.extract_field(record, ['TI', 'T1'])
            clean_title = title.lower().strip() if title != "Not Specified" else title
            self.titles.append((title, clean_title))
            self.title_counts[clean_title] += 1  # Count frequency
            
            # Extract Authors
            authors = self.extract_authors(record)
            
            # Extract DOI
            doi = self.extract_field(record, ['DO'])
            self.dois.append((title, authors, doi))
            
            # Extract Database
            database = self.extract_field(record, ['DP', 'DB'])
            self.databases.append(database)
            
            # Extract Journal/Publisher (T2 field)
            journal = self.extract_field(record, ['T2'])
            self.journals.append((journal, database))
    
    def analyze(self):
        """Perform analysis and export to CSV"""
        if not self.read_file():
            return
        self.parse_records()
        self.export_to_csv(include_authors=True)
        self.export_to_csv(include_authors=False)
    
    
    def export_to_csv(self, output_path: str = None, include_authors: bool = True):
        """Export summary data to CSV file in the requested format"""
        if output_path is None:
            output_dir = Path(__file__).resolve().parent / "output file"
            output_dir.mkdir(parents=True, exist_ok=True)
            suffix = "_analysis.csv" if include_authors else "_analysis_no_authors.csv"
            output_path = output_dir / f"{self.file_path.stem}{suffix}"
        
        unique_count = len(self.title_counts)
        duplicates = {title: count for title, count in self.title_counts.items() if count > 1}
        total_duplicates = sum(duplicates.values()) - len(duplicates)
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                # Row 1: Source file name
                writer.writerow(['Source File', self.file_path.name])
                writer.writerow([])  # Empty row

                # Rows 3-7: Summary statistics
                writer.writerow(['Records identified', len([t for t, _ in self.titles if t != 'Not Specified'])])
                writer.writerow(['Duplicate records removed', total_duplicates])
                writer.writerow(['Records screened', unique_count])
                writer.writerow(['Database Sources', len(set(self.databases))])
                writer.writerow(['Journal Sources', len(set([j for j, _ in self.journals]))])
                writer.writerow([])  # Empty row

                # Database summary
                db_counts = collections.Counter(self.databases)
                db_list = ", ".join([f"{db} ({count})" for db, count in sorted(db_counts.items(), key=lambda x: x[1], reverse=True)])
                writer.writerow(['Database Summary', db_list] if db_list else ['Database Summary', 'None'])
                writer.writerow([])  # Empty row

                # Titles, Authors (if included), and DOIs - only unique ones
                if include_authors:
                    writer.writerow(['Title', 'Authors', 'DOI', 'Frequency'])
                else:
                    writer.writerow(['Title', 'DOI', 'Frequency'])
                seen_titles = set()
                for title, authors, doi in self.dois:
                    if title != "Not Specified":
                        clean_title = title.lower().strip()
                        if clean_title not in seen_titles:
                            frequency = self.title_counts[clean_title]
                            if include_authors:
                                writer.writerow([title, authors, doi, frequency])
                            else:
                                writer.writerow([title, doi, frequency])
                            seen_titles.add(clean_title)

            print(f"✓ Analysis exported to: {output_path}")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")


def main():
    """Main entry point"""
    import sys
    
    # Look for RIS files to process
    input_dir = Path.cwd() / 'input file'
    
    if len(sys.argv) > 1:
        # Process specified file(s)
        for arg in sys.argv[1:]:
            file_path = Path(arg)
            if file_path.exists() and file_path.suffix == '.ris':
                analyzer = RISAnalyzer(str(file_path))
                analyzer.analyze()
            elif file_path.is_dir():
                # If a directory is provided, process all .ris files in it
                for ris_file in file_path.glob('*.ris'):
                    analyzer = RISAnalyzer(str(ris_file))
                    analyzer.analyze()
            else:
                print(f"File not found or not a .ris file: {arg}")
    else:
        # Process all .ris files in the input folder
        if input_dir.exists():
            ris_files = list(input_dir.glob('*.ris'))
            if ris_files:
                print(f"Found {len(ris_files)} RIS file(s) to process...\n")
                for ris_file in ris_files:
                    analyzer = RISAnalyzer(str(ris_file))
                    analyzer.analyze()
            else:
                print(f"No .ris files found in {input_dir}")
                print(f"\nUsage: python analyze_ris.py <path_to_ris_file>")
                sys.exit(1)
        else:
            print(f"Input directory not found: {input_dir}")
            print(f"\nUsage: python analyze_ris.py <path_to_ris_file>")
            sys.exit(1)


if __name__ == "__main__":
    main()