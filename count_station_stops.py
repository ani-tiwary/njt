import os
import csv
import glob
import pandas as pd
import re

def normalize_station_name(name):
    """Normalize station names to handle inconsistencies"""
    # Convert to lowercase for case-insensitive comparison
    name = name.lower().strip()
    
    # Remove punctuation and standardize spacing
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
    
    # Common abbreviations and variations
    replacements = {
        'intl': 'international',
        'int': 'international',
        'jct': 'junction',
        'hts': 'heights',
        'pk': 'park',
        'newark intl airport': 'newark airport',
        'newark international airport': 'newark airport',
        'newark intl': 'newark airport'
    }
    
    for old, new in replacements.items():
        if old in name:
            name = name.replace(old, new)
            
    return name

def count_stops_per_station():
    """Count the number of stopping trains at each station across all lines"""
    # Dictionary to store station counts, with line information
    station_counts = {}
    
    # Process each CSV file
    csv_files = glob.glob('csvs/**/*.csv', recursive=True)
    
    for file_path in csv_files:
        # Extract line name from path (e.g., NEC, RVL, etc.)
        line_name = file_path.split(os.sep)[1]
        print(f"Processing {file_path}")
        
        try:
            # Read the CSV file
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
                
                if len(rows) < 2:
                    print(f"  Skipping - insufficient data in {file_path}")
                    continue
                    
                # Skip the header row with train numbers
                train_numbers = rows[0]
                
                # For each station row
                for row in rows[1:]:  # Skip the train number row
                    if not row:  # Skip empty rows
                        continue
                        
                    # First column should be the station name
                    if not row[0]:  # Skip if no station name
                        continue
                    
                    station_name = row[0].strip()
                    
                    # Skip rows that aren't stations (like "via..." notes)
                    if station_name.lower().startswith(('via', 'note')):
                        continue
                    
                    # Normalize the station name
                    normalized_name = normalize_station_name(station_name)
                    
                    # Count non-empty cells (stops at this station)
                    # Skip the first column (station name)
                    stop_count = sum(1 for cell in row[1:] if cell.strip())
                    
                    # Store the count with line information
                    if normalized_name not in station_counts:
                        station_counts[normalized_name] = {
                            'original_name': station_name,
                            'total_stops': 0,
                            'lines': {}
                        }
                    
                    # Add the count for this line
                    if line_name not in station_counts[normalized_name]['lines']:
                        station_counts[normalized_name]['lines'][line_name] = 0
                    
                    station_counts[normalized_name]['lines'][line_name] += stop_count
                    station_counts[normalized_name]['total_stops'] += stop_count
                    
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
    
    return station_counts

def export_to_csv(station_counts, output_file):
    """Export the station counts to a CSV file"""
    # Prepare the data for CSV
    rows = []
    
    # Header row
    header = ['Station', 'Total Stops']
    # Get all unique line names
    all_lines = set()
    for station_data in station_counts.values():
        all_lines.update(station_data['lines'].keys())
    
    # Sort the line names for consistent output
    all_lines = sorted(all_lines)
    header.extend(all_lines)
    
    rows.append(header)
    
    # Add data for each station
    for normalized_name, data in sorted(station_counts.items()):
        row = [data['original_name'], data['total_stops']]
        
        # Add counts for each line
        for line in all_lines:
            row.append(data['lines'].get(line, 0))
        
        rows.append(row)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    
    print(f"Results saved to {output_file}")

def main():
    # Count stops per station
    station_counts = count_stops_per_station()
    
    # Export the results
    export_to_csv(station_counts, "NJT_Station_Record.csv")
    
    # Print summary
    print(f"\nTotal unique stations: {len(station_counts)}")
    
    # Count total stops across all stations
    total_stops = sum(data['total_stops'] for data in station_counts.values())
    print(f"Total train stops: {total_stops}")

if __name__ == "__main__":
    main() 