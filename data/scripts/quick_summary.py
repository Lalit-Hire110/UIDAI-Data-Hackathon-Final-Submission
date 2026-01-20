"""Quick summary of domain analysis outputs"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"C:\Users\Lalit Hire\UIDAI Data Hackathon 2026\data")
DOMAINS_DIR = BASE_DIR / "outputs" / "domains"

print("\n" + "=" * 80)
print("DOMAIN ANALYSIS EXECUTION SUMMARY")
print("=" * 80)

domains = ['service_deserts', 'demand_behavior', 'service_quality', 'temporal']

for domain in domains:
    domain_path = DOMAINS_DIR / domain
    if domain_path.exists():
        print(f"\n{domain.upper().replace('_', ' ')}:")
        
        # Count files
        csvs = list(domain_path.glob("*.csv"))
        pngs = list((BASE_DIR / "outputs" / "figures" / "domains" / domain).glob("*.png")) if (BASE_DIR / "outputs" / "figures" / "domains" /domain).exists() else []
        
        print(f"  CSV outputs: {len(csvs)}")
        print(f"  PNG figures: {len(pngs)}")
        
        # Check validation
        val_file = domain_path / f"validation_{domain}.csv"
        if val_file.exists():
            val_df = pd.read_csv(val_file)
            failures = val_df[val_df['result'] == 'FAIL']
            if len(failures) > 0:
                print(f"  ⚠ VALIDATION WARNINGS: {len(failures)} checks failed")
                for _, row in failures.iterrows():
                    print(f"    - {row['check_name']}: {row['details']}")
            else:
                print(f"  ✓ All validation checks PASSED")
        
        # Load metrics to check population
        metrics_file = domain_path / f"{domain}_metrics.csv"
        if metrics_file.exists() and domain == 'service_deserts':
            df = pd.read_csv(metrics_file)
            pop_issues = (df['population'] <= 0).sum()
            print(f"  Population coverage: {len(df) - pop_issues}/{len(df)} pincodes ({(1-pop_issues/len(df))*100:.1f}%)")
            if pop_issues == 0:
                print(f"  ✓ NO population failures after imputation")

# Policy simulator
policy_file = DOMAINS_DIR / "policy_recommendations.csv"
if policy_file.exists():
    print(f"\nPOLICY SIMULATOR:")
    print(f"  ✓ Generated: policy_recommendations.csv")
else:
    print(f"\nPOLICY SIMULATOR:")
    print(f"  ⚠ NOT generated (domain dependencies missing)")

print("\n" + "=" * 80)
print("EXECUTION STATUS: COMPLETE")
print("=" * 80)
