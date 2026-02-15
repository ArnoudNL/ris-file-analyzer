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
        self.dois = []  # Store title and DOI pairs
        self.title_counts = collections.Counter()  # Track frequency of each title
        
    def read_file(self) -> bool:
        """Read and parse the RIS file"""
        if not self.file_path.exists():
            print(f"Error: File not found at {self.file_path}")
            return False
        
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
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
            
            # Extract DOI
            doi = self.extract_field(record, ['DO'])
            self.dois.append((title, doi))
            
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
        self.export_to_csv()
    
    
    def export_to_csv(self, output_path: str = None):
        """Export summary data to CSV file in the requested format"""
        if output_path is None:
            output_dir = Path(__file__).resolve().parent / "output file"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{self.file_path.stem}_analysis.csv"
        
        unique_count = len(self.title_counts)
        duplicates = {title: count for title, count in self.title_counts.items() if count > 1}
        total_duplicates = sum(duplicates.values()) - len(duplicates)
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
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

                # Titles and DOIs - only unique ones
                writer.writerow(['Title', 'DOI', 'Frequency'])
                seen_titles = set()
                for title, doi in self.dois:
                    if title != "Not Specified":
                        clean_title = title.lower().strip()
                        if clean_title not in seen_titles:
                            frequency = self.title_counts[clean_title]
                            writer.writerow([title, doi, frequency])
                            seen_titles.add(clean_title)

            print(f"✓ Analysis exported to: {output_path}")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")


def main():
    """Main entry point"""
    import sys
    
    # Try to find the RIS file
    possible_paths = [
        '/Users/arnoudvanrooij/Visual Studio Code/PRISMA Log .ris/input file',
        Path.cwd() / 'input file',
        Path.cwd() / 'PRISMA Log .ris',
    ]
    
    # Also check for any .ris files in current directory
    ris_files = list(Path.cwd().glob('*.ris'))
    possible_paths.extend(ris_files)
    
    file_path = None
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Try to find the file automatically
        for path in possible_paths:
            if isinstance(path, Path) and path.exists() and path.is_file():
                file_path = str(path)
                break
        
        if not file_path and ris_files:
            file_path = str(ris_files[0])
    
    if not file_path:
        print("Usage: python analyze_ris.py <path_to_ris_file>")
        print("\nExample: python analyze_ris.py my_citations.ris")
        print("\nNo RIS file found. Please provide a path to your .ris file.")
        sys.exit(1)
    
    analyzer = RISAnalyzer(file_path)
    analyzer.analyze()


if __name__ == "__main__":
    main()