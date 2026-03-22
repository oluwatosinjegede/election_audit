import csv
from collections import Counter
from rapidfuzz import fuzz


# =========================
# NORMALIZATION
# =========================
def normalize(name):
    if not name:
        return ""
    return " ".join(name.strip().lower().split())


# =========================
# FILE DECODING
# =========================
def decode_file(file):
    raw = file.read()

    for encoding in ['utf-8-sig', 'utf-8', 'cp1252', 'latin-1']:
        try:
            decoded = raw.decode(encoding).splitlines()
            return decoded
        except UnicodeDecodeError:
            continue

    raise ValueError("Unable to decode file. Please upload a valid CSV.")


# =========================
# HEADER DETECTION
# =========================
def find_header_row(lines, possible_headers):
    for i, line in enumerate(lines):
        cols = [c.strip().lower() for c in line.split(',')]
        for header in possible_headers:
            if header in cols:
                return i
    return None


# =========================
# RECORD EXTRACTION (NAME + ID)
# =========================
def extract_records(lines):
    possible_name_headers = ['full name', 'name', 'fullname']
    possible_id_headers = ['id', 'voter id', 'member id']

    header_index = find_header_row(lines, possible_name_headers)

    if header_index is None:
        raise ValueError("Could not find a valid header row with a name column.")

    reader = csv.DictReader(lines[header_index:])

    headers = [h.strip().lower() for h in reader.fieldnames]

    name_col = None
    id_col = None

    # Identify columns
    for i, h in enumerate(headers):
        if h in possible_name_headers:
            name_col = reader.fieldnames[i]
        if h in possible_id_headers:
            id_col = reader.fieldnames[i]

    if not name_col:
        raise ValueError(f"No valid name column found. Found columns: {reader.fieldnames}")

    records = []

    for row in reader:
        name = normalize(row.get(name_col, ""))
        vid = row.get(id_col, "").strip() if id_col else None

        if name:
            records.append({
                "name": name,
                "id": vid
            })

    return records


# =========================
# FUZZY MATCHING
# =========================
def name_similarity(a, b):
    if not a or not b:
        return 0

    score1 = fuzz.ratio(a, b)

    # Reverse name order
    rev_a = " ".join(a.split()[::-1])
    score2 = fuzz.ratio(rev_a, b)

    return max(score1, score2)


def fuzzy_match(name, candidates, threshold=85):
    best_match = None
    best_score = 0

    for candidate in candidates:
        score = name_similarity(name, candidate)
        if score > best_score:
            best_score = score
            best_match = candidate

    if best_score >= threshold:
        return best_match

    return None


# =========================
# MAIN LOAD FUNCTION
# =========================
def load_records(file):
    lines = decode_file(file)

    # Reset pointer for safety
    file.seek(0)

    return extract_records(lines)


# =========================
# AUDIT ENGINE
# =========================
def run_audit(voters_file, votes_file):
    voters = load_records(voters_file)
    votes = load_records(votes_file)

    # Build lookup sets
    voter_names = set(v["name"] for v in voters)
    voter_ids = set(v["id"] for v in voters if v["id"])

    vote_names = [v["name"] for v in votes]
    vote_ids = [v["id"] for v in votes if v["id"]]

    invalid = []
    fuzzy_matches = []
    valid = []

    for vote in votes:
        name = vote["name"]
        vid = vote["id"]

        # Priority 1: ID match (most reliable)
        if vid and vid in voter_ids:
            valid.append(name)
            continue

        # Priority 2: Exact name match
        if name in voter_names:
            valid.append(name)
            continue

        # Priority 3: Fuzzy match
        match = fuzzy_match(name, voter_names)
        if match:
            fuzzy_matches.append({
                "input": name,
                "matched": match
            })
            valid.append(match)
        else:
            invalid.append(name)

    # Duplicate detection
    counts = Counter(vote_names)
    duplicates = sorted([name for name, c in counts.items() if c > 1])

    return {
        "invalid": sorted(set(invalid)),
        "duplicates": duplicates,
        "fuzzy_matches": fuzzy_matches,
        "valid": sorted(set(valid)),
        "stats": {
            "Registered": len(voter_names),
            "Votes Cast": len(vote_names),
            "Unique Votes": len(set(vote_names)),
            "Valid Votes": len(set(valid)),
            "Invalid Votes": len(set(invalid)),
            "Duplicate Votes": len(duplicates),
            "Fuzzy Matches Detected": len(fuzzy_matches),
        }
    }