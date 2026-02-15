# RIS File Analyzer

A lightweight Python utility for analyzing RIS (Research Information Systems) citation files. Identifies duplicate citations, extracts metadata, and generates detailed CSV reports.

## Overview

RIS File Analyzer processes citation databases exported in RIS format and produces comprehensive analysis reports. It detects duplicate records using case-insensitive title matching and provides database breakdowns, frequency counts, and source information in a structured CSV format.

## Features

- **Duplicate Detection**: Identifies and counts duplicate citations using case-insensitive title matching
- **Metadata Extraction**: Extracts titles, DOIs, journals, and database sources
- **Frequency Analysis**: Tracks how many times each paper appears in the original file
- **CSV Export**: Generates structured reports with summary statistics and detailed records
- **Database Summarization**: Categorizes citations by source database
- **Error Tolerant**: Handles various RIS formats and encoding issues gracefully

## Requirements

- Python 3.6 or higher
- No external dependencies (standard library only)

## Installation & Usage

### Basic Usage

```bash
python analyze_ris.py <path_to_file.ris>
```

### Example

```bash
python analyze_ris.py citation.ris
```

Output:
```
✓ Analysis exported to: output file/citation_analysis.csv
```

### Batch Processing

Process multiple RIS files in a directory:

```bash
for file in input_folder/*.ris; do python3 analyze_ris.py "$file"; done
```

## Output Format

The script generates a CSV file in the `output file/` directory (`{filename}_analysis.csv`). If the folder does not exist, it is created automatically.

1. **Source Information**: Original file name
2. **Summary Statistics**:
   - Records identified
   - Duplicate records removed
   - Records screened (unique titles)
   - Database sources
   - Journal sources
3. **Database Summary**: Breakdown by citation source
4. **Detailed Records**: Title, DOI, and frequency count for each unique citation

### Example CSV Output

```csv
Source File,citation.ris

Records identified,10
Duplicate records removed,3
Records screened,7
Database Sources,4
Journal Sources,6

Database Summary,"ScienceDirect (4), Elsevier (3), CrossRef (2)"

Title,DOI,Frequency
"Linking social exchange theory to B2B relationship innovation",10.1016/j.techfore.2025.124003,2
"The Coronavirus crisis in B2B settings",10.1016/j.indmarman.2020.05.004,3
```

## Extracted Metadata

The analyzer extracts the following fields from RIS records:

| Element | RIS Field | Purpose |
|---------|-----------|---------|
| Title | TI / T1 | Citation identifier and duplicate detection |
| DOI | DO | Digital Object Identifier for linking |
| Database | DP / DB | Source/platform of the citation |
| Journal | T2 | Publication venue |

## RIS Format Reference

For more information on RIS file format, see: https://en.wikipedia.org/wiki/RIS_(file_format)

Common field tags:
- `TI` / `T1`: Title
- `DO`: Digital Object Identifier
- `DP` / `DB`: Database/Source
- `T2`: Journal/Publication Name
- `ER`: End of Record delimiter

## Troubleshooting

| Issue | Solution |
|-------|----------|
| File not found | Verify the file path is correct and the file exists |
| Empty or missing data | Ensure your RIS file uses standard field tags (TI, AU, etc.) |
| Encoding errors | The script handles UTF-8 with error tolerance; some special characters may not display perfectly |
| No output generated | Check that the RIS file contains valid records with proper `ER  -` delimiters
