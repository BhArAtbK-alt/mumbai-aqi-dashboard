import pandas as pd
import psycopg2

conn = psycopg2.connect(dbname="aqi_project", user="bharat")

df = pd.read_sql_query("SELET * FROM readings;", conn)
conn.close()

df.to_csv("data/mumbai_aqi_data.csv", index=False)

