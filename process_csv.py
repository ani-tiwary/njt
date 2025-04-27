import os
import csv
import re
import glob
def convert_time_to_military(value, is_pm):
    """Convert time to military format if it's PM"""
    if not value or not re.match(r'^\d+\.\d+$', value):
        return value
    try:
        hours, minutes = value.split('.')
        hours = int(hours)
        if is_pm and hours < 12:
            hours += 12
        return f"{hours}.{minutes}"
    except:
        return value
def process_csv_file(file_path):
    """Process a CSV file to:
    1. Remove letter prefixes from times
    2. Convert PM times to military time (adding 12 to hours)
    3. Remove the AM/PM row
    """
    print(f"Processing {file_path}")
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        rows = list(csv.reader(csvfile))
    if len(rows) < 2:
        return False  
    am_pm_row = rows[1] if len(rows) > 1 else []
    is_pm_column = {}
    for j, cell in enumerate(am_pm_row):
        is_pm_column[j] = cell.strip() == "P.M."
    modified = False
    new_rows = [rows[0]]  
    for i in range(2, len(rows)):
        row = rows[i]
        new_row = []
        for j, cell in enumerate(row):
            cleaned = cell
            match = re.match(r'[A-Za-z]\s*(\d+\.\d+)', cell.strip())
            if match:
                cleaned = match.group(1)
                modified = True
            if j in is_pm_column and is_pm_column[j]:
                military_time = convert_time_to_military(cleaned, True)
                if military_time != cleaned:
                    cleaned = military_time
                    modified = True
            new_row.append(cleaned)
        new_rows.append(new_row)
    if modified or len(new_rows) != len(rows):  
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(new_rows)
        return True
    return False
def main():
    """Process all CSV files in the csvs directory and its subdirectories"""
    csv_files = glob.glob('csvs/**/*.csv', recursive=True)
    processed_count = 0
    total_count = len(csv_files)
    for file_path in csv_files:
        if process_csv_file(file_path):
            processed_count += 1
    print(f"Processed {processed_count} out of {total_count} CSV files")
if __name__ == "__main__":
    main()