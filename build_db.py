import sqlite3
import pandas as pd

print("Creating database...")

# Create database
conn = sqlite3.connect('realtyxperience_knowledge.db')

# You need to have your CSV files here
# If you don't have them, you'll need to export them from Snowflake first

try:
    # Load CSV files
    property_df = pd.read_csv('nigeria_property_knowledge.csv')
    land_df = pd.read_csv('nigeria_land_knowledge.csv')
    
    # Create tables with uppercase names to match your code
    property_df.to_sql('PROPERTY_KNOWLEDGE', conn, if_exists='replace', index=False)
    land_df.to_sql('LAND_KNOWLEDGE', conn, if_exists='replace', index=False)
    
    print(f"✅ Created PROPERTY_KNOWLEDGE with {len(property_df)} rows")
    print(f"✅ Created LAND_KNOWLEDGE with {len(land_df)} rows")
    print("✅ Database created successfully!")
    
except FileNotFoundError as e:
    print(f"❌ CSV files not found: {e}")
    print("Make sure you have:")
    print("  - nigeria_property_knowledge.csv")
    print("  - nigeria_land_knowledge.csv")
    print("in the same folder as this script")

conn.close()
