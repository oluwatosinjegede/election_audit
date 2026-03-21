# audit_app/utils.py

import csv
from collections import Counter


def normalize(name):
    return name.strip().lower()

def load_names(file):
    decoded = file.read().decode('utf-8-sig').splitlines()

    # 🔥 Step 1: Find the correct header row
    header_index = None
    possible_headers = ['full name', 'name']

    for i, line in enumerate(decoded):
        cols = [c.strip().lower() for c in line.split(',')]
        for h in possible_headers:
            if h in cols:
                header_index = i
                break
        if header_index is not None:
            break

    if header_index is None:
        raise ValueError("Could not find a valid header row with 'Name' or 'Full Name'")

    # 🔥 Step 2: Read from correct header row
    reader = csv.DictReader(decoded[header_index:])

    # Normalize headers
    headers = [h.strip().lower() for h in reader.fieldnames]

    # Identify correct column
    name_column = None
    for h in possible_headers:
        if h in headers:
            name_column = reader.fieldnames[headers.index(h)]
            break

    if not name_column:
        raise ValueError(f"No valid name column found. Found columns: {reader.fieldnames}")

    return [
        normalize(row[name_column])
        for row in reader
        if row.get(name_column)
    ]

def run_audit(voters_file, votes_file):
    voters = load_names(voters_file)
    votes = load_names(votes_file)

    voters_set = set(voters)
    votes_set = set(votes)

    invalid = sorted(votes_set - voters_set)

    counts = Counter(votes)
    duplicates = sorted([name for name, c in counts.items() if c > 1])

    valid = sorted(votes_set & voters_set)

    return {
        "invalid": invalid,
        "duplicates": duplicates,
        "valid": valid,
        "stats": {
            "registered": len(voters_set),
            "votes": len(votes),
            "unique_votes": len(votes_set),
            "invalid": len(invalid),
            "duplicates": len(duplicates),
            "valid": len(valid),
        }
    }