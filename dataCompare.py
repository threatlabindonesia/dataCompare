import os
import re
import pandas as pd
from tqdm import tqdm
import argparse

BANNER = """
-------------------------------------------------------------------------------
                      Data Compare for Check The Same Key 

 Description: This tool compares data (IP, domain, or URL) in target files with
              an origin file. It identifies non-matching rows from the origin
              file and saves the results in your preferred output format.

 Author: Afif Hidayatullah
 Organization: ITSEC Asia
-------------------------------------------------------------------------------
"""

# Regex patterns for validation
REGEX_PATTERNS = {
    "ip": r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",
    "domain": r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$",
    "url": r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"
}

def load_data(file_path):
    """
    Load data from CSV, XLSX, TXT, or JSON files.
    """
    _, file_extension = os.path.splitext(file_path)
    try:
        if file_extension.lower() == ".csv":
            return pd.read_csv(file_path)
        elif file_extension.lower() in [".xls", ".xlsx"]:
            return pd.read_excel(file_path)
        elif file_extension.lower() == ".txt":
            with open(file_path, 'r') as file:
                lines = file.readlines()
                return pd.DataFrame(lines, columns=["Data"])
        elif file_extension.lower() == ".json":
            return pd.read_json(file_path, lines=True)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    except Exception as e:
        print(f"[ERROR] Could not load file {file_path}: {e}")
        return pd.DataFrame()

def extract_valid_data(dataframe, key):
    """
    Extract valid data from a dataframe using regex based on the key.
    """
    if key.lower() not in REGEX_PATTERNS:
        raise ValueError(f"Unsupported key: {key}")

    regex = REGEX_PATTERNS[key.lower()]
    valid_data = pd.Series(dtype="object")

    for column in dataframe.columns:
        extracted = dataframe[column].astype(str).str.extract(f"({regex})")[0]
        valid_data = pd.concat([valid_data, extracted], axis=0)

    valid_data = valid_data.dropna().str.strip().drop_duplicates()

    return valid_data.reset_index(drop=True)

def extract_values_from_target(folder_path, key):
    """
    Extract all valid values (IP, domain, or URL) from files in the target folder.
    """
    folder_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    target_values = set()

    print(f"[INFO] Extracting {key.upper()}s from target path...")
    for file_name in tqdm(folder_files, desc="[PROCESSING FILES]", unit="file"):
        file_path = os.path.join(folder_path, file_name)
        target_data = load_data(file_path)
        if not target_data.empty:
            valid_target_data = extract_valid_data(target_data, key)
            if not valid_target_data.empty:
                target_values.update(valid_target_data.unique())

    print(f"[INFO] Total unique {key.upper()}s in target path: {len(target_values)}")
    return target_values

def compare_with_origin(origin_file, target_values, key):
    """
    Compare target values (IP, domain, or URL) with origin file and find non-matching rows.
    """
    print("[INFO] Loading origin file...")
    origin_data = load_data(origin_file)
    if origin_data.empty:
        raise ValueError("[ERROR] Origin file could not be loaded or is empty.")

    print(f"[INFO] Comparing target {key.upper()}s with origin...")
    origin_data["Match"] = origin_data.apply(
        lambda row: any(str(val).strip() in target_values for val in row.astype(str)), axis=1
    )

    matching_rows = origin_data[origin_data["Match"]]
    non_matching_rows = origin_data[~origin_data["Match"]].drop(columns=["Match"])

    # Reporting
    print(f"[INFO] Total rows in origin: {len(origin_data)}")
    print(f"[INFO] Total matching rows: {len(matching_rows)}")
    print(f"[INFO] Total non-matching rows: {len(non_matching_rows)}")

    return non_matching_rows, matching_rows

def save_output(dataframe, output_path):
    """
    Save the resulting dataframe to the specified output format.
    """
    _, file_extension = os.path.splitext(output_path)
    file_extension = file_extension.lower()

    try:
        if file_extension == ".csv":
            dataframe.to_csv(output_path, index=False)
        elif file_extension in [".xls", ".xlsx"]:
            dataframe.to_excel(output_path, index=False)
        elif file_extension == ".txt":
            with open(output_path, "w") as file:
                for row in dataframe.itertuples(index=False):
                    file.write("\t".join(map(str, row)) + "\n")
        elif file_extension == ".json":
            dataframe.to_json(output_path, orient="records", lines=True)
        else:
            raise ValueError(f"Unsupported output file format: {file_extension}")
        print(f"[INFO] Output saved to {output_path}")
    except Exception as e:
        print(f"[ERROR] Could not save output to {output_path}: {e}")

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="Compare data in target files with origin file.")
    parser.add_argument("--path-origin", required=True, help="Path to the origin file (CSV, XLSX, TXT, JSON).")
    parser.add_argument("--path-target", required=True, help="Path to the folder containing files to compare against.")
    parser.add_argument("--output", required=True, help="Path to save the non-matching data (CSV, XLSX, TXT, JSON).")
    parser.add_argument("--key", required=True, choices=["ip", "domain", "url"], help="Key type to compare (IP, domain, URL).")
    args = parser.parse_args()

    if not os.path.isfile(args.path_origin):
        print("[ERROR] The origin file path is invalid.")
        return
    if not os.path.isdir(args.path_target):
        print("[ERROR] The target folder path is invalid.")
        return

    try:
        target_values = extract_values_from_target(args.path_target, args.key)
        non_matching_rows, matching_rows = compare_with_origin(args.path_origin, target_values, args.key)
        if non_matching_rows.empty:
            print("[INFO] No non-matching data found. Output file will be empty.")
        else:
            save_output(non_matching_rows, args.output)
    except ValueError as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
