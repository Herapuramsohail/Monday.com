with open(r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\work_order_tracker.csv", "r", encoding="utf-8-sig", errors="replace") as f:
    lines = [f.readline() for _ in range(15)]
    for idx, l in enumerate(lines):
        print(f"Line {idx}: {l.strip()}")
