from pathlib import Path
from config import DATABASE_PATH, REPORT_DIR

def main():
    db = Path(DATABASE_PATH)
    if db.exists(): db.unlink(); print(f"Deleted: {db}")
    if REPORT_DIR.exists():
        for p in REPORT_DIR.glob("*.md"):
            p.unlink(); print(f"Deleted: {p}")
    print("Reset done.")
if __name__ == "__main__": main()
