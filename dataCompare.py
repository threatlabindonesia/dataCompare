import os
import re
import pandas as pd
from tqdm import tqdm
import argparse

BANNER = """
----------------------------------------------------------------------------
                      Data Compare for Check The Same Key 

 Description: This tool extracts data from an origin file and compares it
              with files in a target folder based on a specific key
              (e.g., IP, domain, URL). It identifies non-matching data from
              the origin file and saves the results in your preferred output
              format (CSV, XLSX, or TXT).

 Author: Afif Hidayatullah
 Organization: ITSEC Asia
----------------------------------------------------------------------------
"""

# Regex patterns for validation
REGEX_PATTERNS = {
    "ip": r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",
    "domain": r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$",
    "url": r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"
}

def load_data(file_path):
    """
    Load data from CSV, XLSX, or TXT files.
    """
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == ".csv":
        return pd.read_csv(file_path, header=None, names=["Data"])
    elif file_extension.lower() in [".xls", ".xlsx"]:
        return pd.read_excel(file_path, header=None, names=["Data"])
    elif file_extension.lower() == ".txt":
        with open(file_path, 'r') as file:
            return pd.DataFrame(file.readlines(), columns=["Data"])
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def extract_valid_data(dataframe, key):
    """
    Extract valid data from a dataframe using regex based on the key.
    """
    if key.lower() not in REGEX_PATTERNS:
        raise ValueError(f"Unsupported key: {key}")

    # Extract data matching the regex
    regex = REGEX_PATTERNS[key.lower()]
    extracted = dataframe["Data"].astype(str).str.extract(f"({regex})", expand=False)
    return extracted.dropna().str.strip().unique()

def find_unique_from_origin(origin_file, folder_path, key):
    """
    Compare data from the origin file with validated data in the target folder.
    """
    print("[INFO] Loading origin file...")
    origin_data = load_data(origin_file)
    origin_values = set(extract_valid_data(origin_data, key))  # Valid data from origin
    print(f"[DEBUG] Origin values: {origin_values}")

    # Process files in the folder
    folder_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    print(f"[INFO] Found {len(folder_files)} files in the target folder.")

    matched_values = set()
    for file_name in tqdm(folder_files, desc="[PROCESSING FILES]", unit="file"):
        file_path = os.path.join(folder_path, file_name)
        try:
            # Load and validate data in target file
            target_data = load_data(file_path)
            valid_target_values = set(extract_valid_data(target_data, key))
            print(f"[DEBUG] Valid target values from {file_name}: {valid_target_values}")

            # Add valid values to matched_values
            matched_values.update(valid_target_values)
        except Exception as e:
            print(f"[ERROR] Could not process file {file_name}: {e}")

    # Calculate unique values from origin that are not in target
    non_matching_values = origin_values - matched_values
    print(f"[DEBUG] Non-matching values: {non_matching_values}")

    return pd.DataFrame(list(non_matching_values), columns=[f"Non-Matching {key.title()}"])

def save_output(dataframe, output_path):
    """
    Save the resulting dataframe to the specified output format.
    """
    _, file_extension = os.path.splitext(output_path)
    file_extension = file_extension.lower()
    if file_extension == ".csv":
        dataframe.to_csv(output_path, index=False)
    elif file_extension in [".xls", ".xlsx"]:
        dataframe.to_excel(output_path, index=False)
    elif file_extension == ".txt":
        with open(output_path, "w") as file:
            for row in dataframe.iloc[:, 0]:
                file.write(f"{row}\n")
    else:
        raise ValueError(f"Unsupported output file format: {file_extension}")
    print(f"[INFO] Output saved to {output_path}")

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="Compare data in an origin file with files in a folder.")
    parser.add_argument("--path-origin", required=True, help="Path to the origin file (CSV, XLSX, or TXT).")
    parser.add_argument("--path-target", required=True, help="Path to the folder containing files to compare against.")
    parser.add_argument("--output", required=True, help="Path to save the non-matching data (CSV, XLSX, or TXT).")
    parser.add_argument("--key", required=True, help="Key type to compare (e.g., IP, domain, url).")
    args = parser.parse_args()

    # Ensure paths exist
    if not os.path.isfile(args.path_origin):
        print("[ERROR] The origin file path is invalid.")
        return
    if not os.path.isdir(args.path_target):
        print("[ERROR] The target folder path is invalid.")
        return

    # Process data
    print(f"[INFO] Starting data comparison based on key: {args.key}...")
    try:
        result = find_unique_from_origin(args.path_origin, args.path_target, args.key)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    # Save the results
    save_output(result, args.output)

if __name__ == "__main__":
    main()
