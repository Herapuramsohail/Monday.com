import csv
import json

def inspect_csv(path):
    print(f"=== Inspecting {path} ===")
    with open(path, mode='r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        print("Headers:", headers)
        rows = []
        for i, row in enumerate(reader):
            if i < 5:
                rows.append(row)
            i += 1
        print(f"Total Rows read sample: {i}")
        print("Sample 3 rows:")
        print(json.dumps(rows[:3], indent=2))

inspect_csv(r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\deal_funnel.csv")
print("\n" + "="*50 + "\n")
inspect_csv(r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\work_order_tracker.csv")
