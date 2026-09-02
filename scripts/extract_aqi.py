import json
import requests
import psycopg2
from datetime import datetime

# Load OpenAQ API Key from secrets.json
try:
    with open('secrets.json', 'r') as f:
        secrets = json.load(f)
    api_key = secrets.get("open_aq_key")
except FileNotFoundError:
    print("Error: secrets.json file not found. Please create it in the root folder.")
    exit(1)

try:
    conn = psycopg2.connect(
        dbname="aqi_project",
        user="bharat" 
    )
    cursor = conn.cursor()
except Exception as e:
    print(f"Database Connection Error: {e}")
    exit(1)

# Configure the OpenAQ API 

locations_url = "https://api.openaq.org/v3/locations"
headers = {
    "X-API-Key": api_key,
    "Accept": "application/json"
}
params = {
    "coordinates": "19.0760,72.8777",
    "radius": 25000,  
    "limit": 100
}

print("Searching for Mumbai monitoring locations (OpenAQ v3)...")
try:
    response = requests.get(locations_url, headers=headers, params=params)
    
    if response.status_code == 200:
        locations_data = response.json().get('results', [])
        print(f"Found {len(locations_data)} active stations near Mumbai.")
        
        inserted_records = 0
        
        # Loop through each location found
        for loc in locations_data:
            loc_id = loc.get('id')
            loc_name = loc.get('name')
            coordinates = loc.get('coordinates', {})
            latitude = coordinates.get('latitude')
            longitude = coordinates.get('longitude')
            
          
            sensor_map = {}
            for sensor in loc.get('sensors', []):
                s_id = sensor.get('id')
                param_data = sensor.get('parameter', {})
                param_name = param_data.get('name')
                param_unit = param_data.get('units')
                if s_id and param_name:
                    sensor_map[s_id] = {
                        "name": param_name,
                        "unit": param_unit
                    }
            
            if not sensor_map:
                continue
                
            # Fetch the latest measurements for this location
            latest_url = f"https://api.openaq.org/v3/locations/{loc_id}/latest"
            latest_response = requests.get(latest_url, headers=headers)
            
            if latest_response.status_code == 200:
                latest_data = latest_response.json().get('results', [])
                
                for record in latest_data:
                    sensor_id = record.get('sensorsId')
                    val = record.get('value')
                    
                    # Look up pollutant name and unit using our map
                    poll_info = sensor_map.get(sensor_id)
                    if not poll_info or val is None or val < 0:
                        continue
                        
                    pollutant = poll_info["name"]
                    unit = poll_info["unit"]
                    
 
                    if pollutant not in ["pm25", "pm10", "no2"]:
                        continue
                        
                    utc_time_str = record.get('datetime', {}).get('utc')
                    if utc_time_str:
                        # Clean trailing 'Z' and parse robustly
                        clean_time = utc_time_str.replace("Z", "")
                        try:
                            recorded_at = datetime.fromisoformat(clean_time)
                        except ValueError:
                            # Fallback parser
                            recorded_at = datetime.strptime(clean_time.split(".")[0], "%Y-%m-%dT%H:%M:%S")
                    else:
                        recorded_at = None
                        
                    insert_query = """
                    INSERT INTO readings (location_name, latitude, longitude, pollutant, value, unit, recorded_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """
                    
                    cursor.execute(insert_query, (loc_name, latitude, longitude, pollutant, val, unit, recorded_at))
                    inserted_records += 1
            else:
                print(f"Skipping readings for {loc_name} (Latest API check failed with {latest_response.status_code})")
                
        # Commit the transaction to save all insertions
        conn.commit()
        print(f"Successfully processed and saved {inserted_records} active entries into your PostgreSQL database!")
        
    else:
        print(f"API Error: Server returned status code {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"An error occurred during pipeline execution: {e}")
    conn.rollback()

finally:
    # Safely close connections
    cursor.close()
    conn.close()
    print("Database connection safely closed.")
