import os
import zipfile
import pandas as pd

# ------------- USER CONFIGURATION -------------
ZIP_PATH    = r"C:\Users\Lenovo\OneDrive\Desktop\YT.zip"
EXTRACT_DIR = r"C:\Users\Lenovo\OneDrive\Desktop\yt"
OUTPUT_CSV  = r"C:\Users\Lenovo\OneDrive\Desktop\merged.csv"
# ----------------------------------------------

# 1) Unzip into EXTRACT_DIR
if not os.path.isdir(EXTRACT_DIR):
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extractall(EXTRACT_DIR)

# 2) Find all CSV files under EXTRACT_DIR
csv_files = []
for root, dirs, files in os.walk(EXTRACT_DIR):
    for fname in files:
        if fname.lower().endswith(".csv"):
            csv_files.append(os.path.join(root, fname))

if len(csv_files) == 0:
    raise FileNotFoundError(f"No CSV files found under '{EXTRACT_DIR}'")

print(f"Found {len(csv_files)} CSV files. They will be concatenated...")

# 3) Read each CSV into a DataFrame, trying UTF-8 first, then Latin-1 if it fails
df_list = []
for path in csv_files:
    print(f"  ▶ Loading {path} ...", end=" ")
    try:
        df = pd.read_csv(path, sep=",", dtype=str)  # UTF-8 is default
        print("(decoded as UTF-8)")
    except UnicodeDecodeError:
        # fallback to Latin-1 if UTF-8 fails
        df = pd.read_csv(path, sep=",", encoding="latin-1", dtype=str)
        print("(decoded as latin-1)")
    df_list.append(df)

# 4) Concatenate them
merged_df = pd.concat(df_list, axis=0, ignore_index=True)

# 5) (Optional) Check total row count
total_rows = len(merged_df)
print(f"Total rows after merging: {total_rows}")

# 6) Write out to OUTPUT_CSV (with header only once)
merged_df.to_csv(OUTPUT_CSV, index=False)
print(f"🚀 Written merged CSV to '{OUTPUT_CSV}'")
