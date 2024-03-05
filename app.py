from flask import Flask
import pandas as pd

app = Flask(__name__)

df = pd.read_csv('df.csv')

import pandas as pd

df = pd.read_csv('df.csv')
# Assume `df` is your initial DataFrame
sistema_df = pd.DataFrame(df['Sistema'].unique(), columns=['SistemaName'])
sistema_df.insert(0, 'SistemaID', range(1, len(sistema_df) + 1))

area_sistema_df = df[[' Area', 'Sistema']].drop_duplicates().reset_index(drop=True)
area_sistema_df = area_sistema_df.merge(sistema_df, left_on='Sistema', right_on='SistemaName')
area_df = area_sistema_df[[' Area', 'SistemaID']].rename(columns={' Area': 'AreaName'})
area_df.insert(0, 'AreaID', range(1, len(area_df) + 1))

# Prepare the mapping from AreaName to AreaID
area_name_to_id = dict(zip(area_df['AreaName'], area_df['AreaID']))

# Map the Area names to IDs in the original df
df['AreaID'] = df[' Area'].map(area_name_to_id)

# Select required columns and rename appropriately
hourly_data_df = df[['Date', ' Hora', ' Generacion (MWh)', 'AreaID']].copy()
# Initialize an empty dictionary to hold the nested structure
hourly_data_by_area = {}

# Iterate through each row of the hourly_data_df to populate the dictionary
for index, row in hourly_data_df.iterrows():
    area_id = row['AreaID']
    date = row['Date']
    generacion = row[' Generacion (MWh)']
    
    # Check if the area_id is already in the dictionary
    if area_id not in hourly_data_by_area:
        hourly_data_by_area[area_id] = {}
    
    # Assuming 'Date' and 'Hora' uniquely identify each record, you can concatenate them for a unique key
    # If 'Hora' is not needed or 'Date' is already unique, you can skip concatenating 'Hora'
    date_hour = f"{date} {row[' Hora']}".strip()  # Adjust based on whether you need to include hour or not
    
    # Assign generacion value to the corresponding date in the area's dictionary
    hourly_data_by_area[area_id][date_hour] = generacion

# Note: This structure assumes that each date (and hour, if included) combination is unique per area.
# If there are multiple entries for a single date (and hour), this will need adjustment to aggregate or handle those duplicates.


# Convert DataFrames to dictionaries
sistema_dict = sistema_df.to_dict(orient='records')
area_dict = area_df.to_dict(orient='records')

@app.route('/sistemas', methods=['GET'])
def get_sistemas():
    return sistema_dict

@app.route('/areas', methods=['GET'])
def get_areas():
    return area_dict

@app.route('/hour', methods=['GET'])
def get_hourly_data():
    return hourly_data_by_area

# print(sistemas_table)
