from config import COMPANY_PROFILES_CSV
from collectors.profile_auto_collector import build_clean_profiles


def main():
    df = build_clean_profiles()
    df.to_csv(COMPANY_PROFILES_CSV, index=False, encoding="utf-8-sig")
    print(f"Updated: {COMPANY_PROFILES_CSV}")


if __name__ == "__main__":
    main()
