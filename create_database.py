import sqlite3
import pandas as pd

# Create database
conn = sqlite3.connect('realtyxperience_knowledge.db')

# Load your CSV files
print("Loading property knowledge...")
property_df = pd.read_csv('nigeria_property_knowledge.csv')
print(f"Loaded {len(property_df)} property records")

print("Loading land knowledge...")
land_df = pd.read_csv('nigeria_land_knowledge.csv')
print(f"Loaded {len(land_df)} land records")

# Create tables
property_df.to_sql('PROPERTY_KNOWLEDGE', conn, if_exists='replace', index=False)
land_df.to_sql('LAND_KNOWLEDGE', conn, if_exists='replace', index=False)

print("Database created successfully!")
conn.close()
