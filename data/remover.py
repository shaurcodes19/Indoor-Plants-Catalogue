import csv

seen = set()
rows = []

# Read and remove duplicates
with open("plants_data.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["Plant Name"].strip().lower()
        if name not in seen:
            seen.add(name)
            rows.append(row)

# Renumber Plant ID fields
for i, row in enumerate(rows, start=1):
    row["Plant ID"] = i

# Write cleaned CSV
with open("plants_data_new.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Duplicates removed and Plant ID reordered.")
