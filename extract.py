import shutil
import re
from pathlib import Path

import pandas as pd

def process_files(folder_path):
    uploaded_dir_path = Path(folder_path)
    uploaded_files = list(uploaded_dir_path.glob('Demanda Real Balance*.csv'))
    
    regex_pattern = r"Demanda Real Balance_(\d+)(_v(\d+))? Dia Operacion (\d{4}-\d{2}-\d{2}) v(\d{4} \d{2} \d{2}_\d{2} \d{2} \d{2})"
    
    file_info = []
    for file_path in uploaded_files:
        match = re.search(regex_pattern, file_path.name)
        if match:
            version_int = int(match.group(1))
            version_optional = int(match.group(3)) if match.group(3) else 0  # Default to 0 if no optional version
            assessed_date = match.group(4)
            published_datetime = match.group(5).replace(" ", "")
            file_info.append((file_path, version_int, version_optional, assessed_date, published_datetime))
    
    sorted_files = sorted(file_info, key=lambda x: (x[3], -x[1], -x[2], -int(x[4])))
    filtered_files = {}
    for file, version_int, version_optional, assessed_date, published_datetime in sorted_files:
        if assessed_date not in filtered_files or version_int < filtered_files[assessed_date][1]:
            filtered_files[assessed_date] = (file, version_int, version_optional)
    
    return filtered_files

def read_files(filtered_files):
    dfs = []
    for date, file_info in filtered_files.items():
        file_path = file_info[0]
        df = pd.read_csv(file_path, skiprows=8)
        df['Date'] = date
        dfs.append(df)
    
    merged_df = pd.concat(dfs, ignore_index=True, sort=False)
    return merged_df

def extract(folder_path):
    filtered_files = process_files(folder_path)
    merged_df = read_files(filtered_files)
    return merged_df

print(extract('data'))