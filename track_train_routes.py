import os
import csv
import glob
import json
from collections import defaultdict
def extract_train_routes():
    """Extract the routes for each individual train across all lines"""
    train_routes = defaultdict(dict)
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
                    if train_num.strip() and train_num.strip().isdigit():
                        valid_train_indices.append(i)
                        valid_train_numbers.append(train_num.strip())
                    elif train_num.strip():
                        valid_train_indices.append(i)
                        valid_train_numbers.append(train_num.strip())
                for i in range(1, len(rows)):
                    row = rows[i]
                    if not row or not row[0].strip():
                        continue
                    station_name = row[0].strip()
                    if station_name.lower().startswith(('via', 'note')):
                        continue
                    for idx, train_idx in enumerate(valid_train_indices):
                        if train_idx + 1 >= len(row):
                            continue
                        train_num = valid_train_numbers[idx]
                        time = row[train_idx + 1].strip()
                        if time:
                            if train_num not in train_routes[line_name]:
                                train_routes[line_name][train_num] = []
                            train_routes[line_name][train_num].append({
                                "station": station_name,
                                "time": time
                            })
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
    return train_routes
def export_to_json(train_routes, output_file):
    """Export the train routes to a JSON file"""
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(train_routes, jsonfile, indent=2)
    print(f"Results saved to {output_file}")
def export_to_csv(train_routes, output_file):
    """Export the train routes to a CSV file"""
    rows = []
    header = ["Line", "Train Number", "Route (Station: Time)"]
    rows.append(header)
    for line_name, trains in sorted(train_routes.items()):
        for train_num, route in sorted(trains.items(), key=lambda x: x[0]):
            route_str = " → ".join([f"{stop['station']}: {stop['time']}" for stop in route])
            rows.append([line_name, train_num, route_str])
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    print(f"Results saved to {output_file}")
def generate_summary_statistics(train_routes):
    """Generate summary statistics about the train routes"""
    total_trains = 0
    routes_by_line = {}
    max_route_length = 0
    max_route_train = ""
    max_route_line = ""
    for line_name, trains in train_routes.items():
        line_train_count = len(trains)
        total_trains += line_train_count
        routes_by_line[line_name] = line_train_count
        for train_num, route in trains.items():
            if len(route) > max_route_length:
                max_route_length = len(route)
                max_route_train = train_num
                max_route_line = line_name
    print("\nTrain Route Statistics:")
    print(f"Total unique trains: {total_trains}")
    print("\nTrains by line:")
    for line, count in sorted(routes_by_line.items()):
        print(f"  {line}: {count} trains")
    print(f"\nLongest route: Train {max_route_train} on line {max_route_line} with {max_route_length} stops")
    return {
        "total_trains": total_trains,
        "trains_by_line": routes_by_line,
        "longest_route": {
            "train": max_route_train,
            "line": max_route_line,
            "stops": max_route_length
        }
    }
def main():
    train_routes = extract_train_routes()
    export_to_json(train_routes, "NJT_Train_Routes.json")
    export_to_csv(train_routes, "NJT_Train_Routes.csv")
    stats = generate_summary_statistics(train_routes)
if __name__ == "__main__":
    main() 