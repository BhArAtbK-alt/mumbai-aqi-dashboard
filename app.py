import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# Configure page layout
st.set_page_config(
    page_title="Mumbai Live AQI Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.title("🌬️ Mumbai Live Air Quality Index (AQI) Dashboard")
st.markdown("This interactive dashboard monitors real-time air quality metrics across the Mumbai Metropolitan Region.")

# Database connection & data loading
@st.cache_data(ttl=300)
def load_data_from_db():
    try:
        conn = psycopg2.connect(
            dbname="aqi_project",
            user="bharat"  
        )
        cursor = conn.cursor()
        
        # Query active records
        query = "SELECT location_name, latitude, longitude, pollutant, value, unit, recorded_at FROM readings;"
        cursor.execute(query)
        raw_data = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description]
        
        cursor.close()
        conn.close()
        
        return pd.DataFrame(raw_data, columns=columns)
    except Exception as e:
        st.error(f"Failed to connect to local PostgreSQL database: {e}")
        return pd.DataFrame()

# Load data
df = load_data_from_db()

if df.empty:
    st.warning("No data found in your PostgreSQL database. Run 'python scripts/extract_aqi.py' to fetch data first.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("📊 Filter Options")
pollutants = df['pollutant'].unique()
selected_pollutant = st.sidebar.selectbox("Select Pollutant to Visualize", pollutants, index=0)

# Filter the data based on selection
filtered_df = df[df['pollutant'] == selected_pollutant].sort_values(by="value", ascending=False)

unit = filtered_df['unit'].iloc[0] if not filtered_df.empty else "µg/m³"

# --- KEY PERFORMANCE METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="📍 Total Active Monitoring Stations", value=int(df['location_name'].nunique()))
with col2:
    avg_val = filtered_df['value'].mean() if not filtered_df.empty else 0.0
    st.metric(label=f"💨 Average {selected_pollutant.upper()} Concentration", value=f"{avg_val:.2f} {unit}")
with col3:
    if not filtered_df.empty:
        
        max_reading = filtered_df.iloc[0]
        st.metric(
            label="⚠️ Highest Pollution Hotspot", 
            value=max_reading['location_name'], 
            delta=f"{max_reading['value']} {unit}",
            delta_color="inverse"
        )
    else:
        st.metric(label="⚠️ Highest Pollution Hotspot", value="No data")

st.markdown("---")

# --- VISUALIZATIONS ---
left_col, right_col = st.columns(2)

with left_col:
    st.subheader(f"Top Locations by {selected_pollutant.upper()} Levels")
    if not filtered_df.empty:
        fig = px.bar(
            filtered_df.head(15), 
            x="value", 
            y="location_name", 
            orientation="h",
            labels={"value": f"Concentration ({unit})", "location_name": "Station Location"},
            color="value",
            color_continuous_scale="Reds",
            template="plotly_white"
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader("🗺️ Station Map Tracker")
    map_data = filtered_df[['latitude', 'longitude', 'location_name', 'value']].dropna()
    if not map_data.empty:
        st.map(map_data, latitude="latitude", longitude="longitude")
    else:
        st.info("No coordinates available to map.")

st.markdown("---")

# --- RAW DATA VIEW ---
st.subheader("📋 Live Database Table View")
st.dataframe(filtered_df[['location_name', 'pollutant', 'value', 'unit', 'recorded_at']], use_container_width=True)
