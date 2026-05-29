from pathlib import Path

paths = [
    Path("data/archive.db"),
    Path("data/company_reports.csv"),
]

for p in paths:
    if p.exists():
        mb = p.stat().st_size / 1024 / 1024
        print(f"{p}: {mb:.2f} MB")
    else:
        print(f"{p}: not found")
