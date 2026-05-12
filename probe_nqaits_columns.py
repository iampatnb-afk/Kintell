import pandas as pd
NQS_FILE = "abs_data/NQAITS Quarterly Data Splits (Q3 2013 - Q4 2025).xlsx"
df = pd.read_excel(NQS_FILE, sheet_name="Q42025data", dtype=str, nrows=5)
print("=== NQAITS Q42025data columns ===")
for i, c in enumerate(df.columns):
    print(f"  [{i:>2}] {c!r}")
print()
print("=== Subtype-flag-looking columns + value distributions (first 200 rows) ===")
df_full = pd.read_excel(NQS_FILE, sheet_name="Q42025data", dtype=str, nrows=200)
for c in df_full.columns:
    cl = c.lower()
    if any(k in cl for k in ["long day", "out of", "preschool", "occasional", "family", "vacation", "type"]):
        print(f"  COLUMN: {c!r}")
        vals = df_full[c].astype(str).str.strip().value_counts(dropna=False)
        for v, n in vals.head(8).items():
            print(f"      {v!r}: {n}")
        print()
