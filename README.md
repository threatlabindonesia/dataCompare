# Data Compare for Check The Same Key

## Overview
This tool extracts data from an origin file and compares it with files in a target folder based on a specific key (e.g., IP, domain, URL). It identifies non-matching data from the origin file and saves the results in your preferred output format (CSV, XLSX, or TXT).

## Features
- Supports CSV, XLSX, and TXT file formats.
- Validates data using regex patterns for IP addresses, domains, and URLs.
- Provides detailed logs and error handling.
- Saves results in a format of your choice.

---

## Requirements
Before using the tool, ensure you have the following installed:

- Python 3.7 or later
- Required Python packages:
  - pandas
  - openpyxl
  - tqdm

You can install the required packages using the command:

```bash
pip install pandas openpyxl tqdm
```

---

## Installation
1. Clone this repository or download the script:

```bash
git clone https://github.com/threatlabindonesia/dataCompare.git
cd dataCompare
```

2. Ensure you have the necessary Python environment set up (refer to the requirements section).

3. Verify the script permissions:

```bash
chmod +x dataCompare.py
```

---

## How to Use

### Command-Line Arguments
| Argument         | Description                                               |
|------------------|-----------------------------------------------------------|
| `--path-origin`  | Path to the origin file (CSV, XLSX, or TXT).               |
| `--path-target`  | Path to the folder containing files to compare against.    |
| `--output`       | Path to save the non-matching data (CSV, XLSX, or TXT).    |
| `--key`          | Key type for comparison (e.g., `ip`, `domain`, `url`).    |

### Example Command

```bash
python dataCompare.py \
    --path-origin data/origin.csv \
    --path-target data/target_folder \
    --output results/non_matching_data.csv \
    --key domain
```

### Example Output
Given the following inputs:

**Origin File (`origin.csv`):**
```
example.com
google.com
notfound.com
```

**Target Files in `target_folder`**:
- `file1.csv`:
  ```
  example.com
  anotherdomain.com
  ```
- `file2.csv`:
  ```
  google.com
  somedomain.net
  ```

**Result (`non_matching_data.csv`):**
```
Non-Matching Domain
notfound.com
```

---

## Author
This tool was developed by **Afif Hidayatullah**, a passionate software developer at **ITSEC Asia**.

### LinkedIn
Connect with me on LinkedIn: [Afif Hidayatullah](https://www.linkedin.com/in/afifhidayatullah)

### Organization
**ITSEC Asia** is a leading provider of cybersecurity and IT solutions. Learn more at [ITSEC Asia](https://www.itsec.asia).
