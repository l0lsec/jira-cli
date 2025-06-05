import json
import csv

# Input and output filenames
INPUT_FILE = 'issues.json'
OUTPUT_FILE = 'output.csv'

# Fields to extract: (CSV column name, JSON path as list)
FIELDS = [
    ("Name", ["fields", "summary"]),
    ("Email", ["fields", "customfield_10037"]),
    ("Phone", ["fields", "customfield_10038"]),
    ("Status", ["fields", "status", "name"]),
    ("Created Date", ["fields", "created"]),
    ("Reporter Name", ["fields", "reporter", "displayName"]),
    ("Reporter Email", ["fields", "reporter", "emailAddress"]),
]

def get_nested(data, path):
    """Safely get a nested value from a dict, return '' if not found."""
    for key in path:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return ''
    return data

def main():
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    # If the file is a single object, wrap it in a list
    if isinstance(data, dict) and 'fields' in data:
        issues = [data]
    elif isinstance(data, list):
        issues = data
    elif isinstance(data, dict) and 'issues' in data:
        issues = data['issues']
    else:
        raise ValueError('Unrecognized JSON structure')

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([col for col, _ in FIELDS])
        for issue in issues:
            row = [get_nested(issue, path) for _, path in FIELDS]
            writer.writerow(row)

if __name__ == '__main__':
    main() 