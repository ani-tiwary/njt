import os
import csv
import glob
import json
import re
from collections import defaultdict
def normalize_station_name(name):
    """Normalize station names to handle inconsistencies"""
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
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
def extract_trains_by_station():
    """Extract which trains stop at each station across all lines"""
    stations_trains = defaultdict(lambda: defaultdict(list))
    original_names = {}
    csv_files = glob.glob('csvs/**/*.csv', recursive=True)
    for file_path in csv_files:
        line_name = file_path.split(os.sep)[1]
        print(f"Processing {file_path}")
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
                if len(rows) < 2:
                    print(f"  Skipping - insufficient data in {file_path}")
                    continue
                train_numbers = rows[0][1:]  
                valid_train_indices = []
                valid_train_numbers = []
                for i, train_num in enumerate(train_numbers):
                    train_num = train_num.strip()
                    if train_num:
                        valid_train_indices.append(i)
                        valid_train_numbers.append(train_num)
                for i in range(1, len(rows)):
                    row = rows[i]
                    if not row or not row[0].strip():
                        continue
                    station_name = row[0].strip()
                    if station_name.lower().startswith(('via', 'note')):
                        continue
                    normalized_name = normalize_station_name(station_name)
                    if normalized_name not in original_names:
                        original_names[normalized_name] = station_name
                    for idx, train_idx in enumerate(valid_train_indices):
                        if train_idx + 1 >= len(row):
                            continue
                        train_num = valid_train_numbers[idx]
                        time = row[train_idx + 1].strip()
                        if time:  
                            if train_num not in stations_trains[normalized_name][line_name]:
                                stations_trains[normalized_name][line_name].append(train_num)
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
    result = {}
    for normalized_name, lines in stations_trains.items():
        original_name = original_names[normalized_name]
        result[original_name] = dict(lines)
    return result
def export_to_json(stations_trains, output_file):
    """Export the stations and their trains to a JSON file"""
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(stations_trains, jsonfile, indent=2, sort_keys=True)
    print(f"Results saved to {output_file}")
def generate_summary_statistics(stations_trains):
    """Generate summary statistics about stations and trains"""
    total_stations = len(stations_trains)
    stations_by_line = defaultdict(int)
    max_trains_station = ""
    max_trains_count = 0
    max_lines_station = ""
    max_lines_count = 0
    for station, lines in stations_trains.items():
        lines_count = len(lines)
        if lines_count > max_lines_count:
            max_lines_count = lines_count
            max_lines_station = station
        total_trains = sum(len(trains) for trains in lines.values())
        if total_trains > max_trains_count:
            max_trains_count = total_trains
            max_trains_station = station
        for line in lines:
            stations_by_line[line] += 1
    print("\nStation Statistics:")
    print(f"Total stations: {total_stations}")
    print("\nStations by line:")
    for line, count in sorted(stations_by_line.items()):
        print(f"  {line}: {count} stations")
    print(f"\nStation with most train stops: {max_trains_station} with {max_trains_count} trains")
    print(f"Station served by most lines: {max_lines_station} with {max_lines_count} lines")
    return {
        "total_stations": total_stations,
        "stations_by_line": dict(stations_by_line),
        "most_trains": {
            "station": max_trains_station,
            "count": max_trains_count
        },
        "most_lines": {
            "station": max_lines_station,
            "count": max_lines_count
        }
    }
def main():
    stations_trains = extract_trains_by_station()
    export_to_json(stations_trains, "NJT_Trains_By_Station.json")
    stats = generate_summary_statistics(stations_trains)
if __name__ == "__main__":
    main() 