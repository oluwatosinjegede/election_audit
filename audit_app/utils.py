import csv
from collections import Counter


def normalize(name):
    if not name:
        return ""
    return " ".join(name.strip().lower().split())


def decode_file(file):
    """
    Try multiple encodings to safely decode uploaded CSV files.
    """
    raw = file.read()

    for encoding in ['utf-8-sig', 'utf-8', 'cp1252', 'latin-1']:
        try:
            decoded = raw.decode(encoding).splitlines()
            return decoded
        except UnicodeDecodeError:
            continue

    raise ValueError("Unable to decode file. Please upload a valid CSV.")


def find_header_row(lines, possible_headers):
    """
    Identify the row index that contains the correct header.
    """
    for i, line in enumerate(lines):
        cols = [c.strip().lower() for c in line.split(',')]
        for header in possible_headers:
            if header in cols:
                return i
    return None


def extract_names(lines, possible_headers):
    """
    Extract names from CSV after detecting correct header row.
    """
    header_index = find_header_row(lines, possible_headers)

    if header_index is None:
        raise ValueError(
            f"Could not find a valid header row. Expected one of: {possible_headers}"
        )

    reader = csv.DictReader(lines[header_index:])

    # Normalize headers
    headers = [h.strip().lower() for h in reader.fieldnames]

    # Find correct column
    name_column = None
    for header in possible_headers:
        if header in headers:
            name_column = reader.fieldnames[headers.index(header)]
            break

    if not name_column:
        raise ValueError(
            f"No valid name column found. Found columns: {reader.fieldnames}"
        )

    return [
        normalize(row[name_column])
        for row in reader
        if row.get(name_column) and normalize(row[name_column])
    ]


def load_names(file):
    """
    Main loader function (handles decoding + extraction).
    """
    lines = decode_file(file)

    # Reset pointer (important for Django file reuse)
    file.seek(0)

    possible_headers = ['full name', 'name', 'fullname']

    return extract_names(lines, possible_headers)


def run_audit(voters_file, votes_file):
    voters = load_names(voters_file)
    votes = load_names(votes_file)

    voters_set = set(voters)
    votes_set = set(votes)

    invalid = sorted(votes_set - voters_set)

    counts = Counter(votes)
    duplicates = sorted([name for name, count in counts.items() if count > 1])

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