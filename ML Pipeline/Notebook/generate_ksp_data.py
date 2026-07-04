"""
Synthetic Data Generation for KSP Analytics Platform
Generates realistic crime data for Karnataka State Police analytics

Author: Lead Data Analyst
Date: June 17, 2026
"""

import pandas as pd
import numpy as np
import networkx as nx
from faker import Faker
import uuid
from datetime import datetime, timedelta
import random

# Initialize Faker with Indian locale
fake = Faker('en_IN')
np.random.seed(42)
random.seed(42)

# Configuration
NUM_CRIMINALS = 5000
NUM_INCIDENTS = 50000

# Crime types with weighted probabilities (more common crimes have higher weights)
CRIME_TYPES = {
    'Theft': 0.30,
    'Burglary': 0.20,
    'Assault': 0.15,
    'Vehicle Theft': 0.12,
    'Robbery': 0.10,
    'Fraud': 0.08,
    'Smuggling': 0.03,
    'Murder': 0.02
}

LINK_TYPES = ['Accomplice', 'Gang Member', 'Known Associate']

# Karnataka district centroids (actual coordinates)
DISTRICTS = [
    {'district_id': 'D-BLR', 'name': 'Bengaluru', 'base_lat': 12.9716, 'base_lon': 77.5946},
    {'district_id': 'D-MYS', 'name': 'Mysuru', 'base_lat': 12.2958, 'base_lon': 76.6394},
    {'district_id': 'D-MNG', 'name': 'Mangaluru', 'base_lat': 12.9141, 'base_lon': 74.8560},
    {'district_id': 'D-HUB', 'name': 'Hubballi', 'base_lat': 15.3647, 'base_lon': 75.1240},
    {'district_id': 'D-BEL', 'name': 'Belagavi', 'base_lat': 15.8497, 'base_lon': 74.4977}
]

# Karnataka boundaries
KARNATAKA_LAT_MIN = 11.5
KARNATAKA_LAT_MAX = 18.5
KARNATAKA_LON_MIN = 74.0
KARNATAKA_LON_MAX = 78.5


def generate_districts():
    """Generate districts dataframe"""
    print("Generating districts data...")
    df = pd.DataFrame(DISTRICTS)
    return df


def generate_criminals(num_criminals):
    """Generate criminals with right-skewed age distribution and risk scores"""
    print(f"Generating {num_criminals} criminals...")
    
    criminals = []
    for _ in range(num_criminals):
        # Right-skewed age distribution (more young criminals)
        age = int(np.random.gamma(shape=2, scale=12) + 18)
        age = min(age, 65)  # Cap at 65
        
        # Risk score: normal distribution centered at 50, capped at 100
        risk_score = int(np.random.normal(loc=50, scale=20))
        risk_score = max(0, min(risk_score, 100))  # Clamp between 0-100
        
        criminal = {
            'criminal_id': str(uuid.uuid4()),
            'name': fake.name(),
            'age': age,
            'base_risk_score': risk_score
        }
        criminals.append(criminal)
    
    return pd.DataFrame(criminals)


def generate_associations(criminals_df):
    """Generate criminal network using Barabási-Albert preferential attachment model"""
    print("Generating criminal network associations...")
    
    num_nodes = len(criminals_df)
    # BA model: m = number of edges to attach from new node (creates hubs)
    # Using m=2 means most criminals have 1-2 associates, but some become hubs
    G = nx.barabasi_albert_graph(num_nodes, m=2, seed=42)
    
    # Map graph nodes to criminal IDs
    criminal_ids = criminals_df['criminal_id'].tolist()
    
    associations = []
    for edge in G.edges():
        source_id = criminal_ids[edge[0]]
        target_id = criminal_ids[edge[1]]
        link_type = random.choice(LINK_TYPES)
        
        associations.append({
            'source_id': source_id,
            'target_id': target_id,
            'link_type': link_type
        })
    
    print(f"Generated {len(associations)} associations (scale-free network)")
    return pd.DataFrame(associations)


def generate_clustered_coordinates(district, std_dev=0.3):
    """
    Generate coordinates using 2D Gaussian distribution around district centroid
    Ensures coordinates stay within Karnataka boundaries
    """
    while True:
        lat = np.random.normal(loc=district['base_lat'], scale=std_dev)
        lon = np.random.normal(loc=district['base_lon'], scale=std_dev)
        
        # Ensure within Karnataka boundaries
        if (KARNATAKA_LAT_MIN <= lat <= KARNATAKA_LAT_MAX and 
            KARNATAKA_LON_MIN <= lon <= KARNATAKA_LON_MAX):
            return round(lat, 6), round(lon, 6)


def generate_incidents(criminals_df, districts_df, num_incidents):
    """
    Generate incidents with spatial clustering and temporal anomaly injection
    """
    print(f"Generating {num_incidents} incidents...")
    
    criminal_ids = criminals_df['criminal_id'].tolist()
    crime_types = list(CRIME_TYPES.keys())
    crime_weights = list(CRIME_TYPES.values())
    
    # Date range: Jan 1, 2024 to present (June 17, 2026)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 6, 17)
    date_range_days = (end_date - start_date).days
    
    incidents = []
    
    # Generate base incidents
    for i in range(num_incidents):
        # Random criminal
        criminal_id = random.choice(criminal_ids)
        
        # Weighted random crime type
        crime_type = random.choices(crime_types, weights=crime_weights, k=1)[0]
        
        # Random timestamp
        random_days = random.randint(0, date_range_days)
        random_seconds = random.randint(0, 86400)
        timestamp = start_date + timedelta(days=random_days, seconds=random_seconds)
        
        # Random district (weighted towards Bengaluru - largest city)
        district_weights = [0.40, 0.20, 0.15, 0.15, 0.10]  # Bengaluru gets 40%
        district = random.choices(DISTRICTS, weights=district_weights, k=1)[0]
        
        # Generate clustered coordinates around district centroid
        lat, lon = generate_clustered_coordinates(district)
        
        incident = {
            'incident_id': str(uuid.uuid4()),
            'criminal_id': criminal_id,
            'crime_type': crime_type,
            'timestamp': timestamp.isoformat(),
            'latitude': lat,
            'longitude': lon
        }
        incidents.append(incident)
    
    incidents_df = pd.DataFrame(incidents)
    
    # TEMPORAL ANOMALY INJECTION
    # Inject 400% spike in Vehicle Thefts in Bengaluru during October 2025
    print("Injecting temporal anomaly: Vehicle Theft spike in Bengaluru, October 2025...")
    
    anomaly_start = datetime(2025, 10, 1)
    anomaly_end = datetime(2025, 10, 31)
    bengaluru_district = DISTRICTS[0]  # Bengaluru
    
    # Calculate normal rate: count existing vehicle thefts in normal months
    normal_vehicle_thefts = len(incidents_df[
        (incidents_df['crime_type'] == 'Vehicle Theft') & 
        (pd.to_datetime(incidents_df['timestamp']).dt.month != 10)
    ])
    monthly_rate = normal_vehicle_thefts / 28  # Approximate months in dataset
    
    # 400% increase means 4x the normal rate
    anomaly_count = int(monthly_rate * 4)
    
    anomaly_incidents = []
    for _ in range(anomaly_count):
        criminal_id = random.choice(criminal_ids)
        
        # Random timestamp in October 2025
        random_days = random.randint(0, 30)
        random_seconds = random.randint(0, 86400)
        timestamp = anomaly_start + timedelta(days=random_days, seconds=random_seconds)
        
        # Clustered in Bengaluru
        lat, lon = generate_clustered_coordinates(bengaluru_district)
        
        anomaly_incident = {
            'incident_id': str(uuid.uuid4()),
            'criminal_id': criminal_id,
            'crime_type': 'Vehicle Theft',
            'timestamp': timestamp.isoformat(),
            'latitude': lat,
            'longitude': lon
        }
        anomaly_incidents.append(anomaly_incident)
    
    # Append anomaly incidents
    anomaly_df = pd.DataFrame(anomaly_incidents)
    incidents_df = pd.concat([incidents_df, anomaly_df], ignore_index=True)
    
    # Sort by timestamp
    incidents_df['timestamp_sort'] = pd.to_datetime(incidents_df['timestamp'])
    incidents_df = incidents_df.sort_values('timestamp_sort').drop('timestamp_sort', axis=1)
    incidents_df = incidents_df.reset_index(drop=True)
    
    print(f"Total incidents generated: {len(incidents_df)} (including {len(anomaly_df)} anomaly incidents)")
    
    return incidents_df


def main():
    """Main execution function"""
    print("=" * 60)
    print("KSP Synthetic Data Generation")
    print("Datathon 2026 - AI-Driven Crime Analytics Platform")
    print("=" * 60)
    print()
    
    # Generate all datasets
    districts_df = generate_districts()
    criminals_df = generate_criminals(NUM_CRIMINALS)
    associations_df = generate_associations(criminals_df)
    incidents_df = generate_incidents(criminals_df, districts_df, NUM_INCIDENTS)
    
    # Save to CSV files
    print()
    print("Saving datasets to CSV files...")
    districts_df.to_csv('districts.csv', index=False)
    criminals_df.to_csv('criminals.csv', index=False)
    associations_df.to_csv('associations.csv', index=False)
    incidents_df.to_csv('incidents.csv', index=False)
    
    # Print summary statistics
    print()
    print("=" * 60)
    print("GENERATION COMPLETE - Summary Statistics")
    print("=" * 60)
    print(f"Districts: {len(districts_df)}")
    print(f"Criminals: {len(criminals_df)}")
    print(f"Associations (Network Edges): {len(associations_df)}")
    print(f"Incidents: {len(incidents_df)}")
    print()
    print("Network Statistics:")
    num_nodes = len(criminals_df)
    num_edges = len(associations_df)
    avg_connections = (2 * num_edges) / num_nodes
    print(f"  Average connections per criminal: {avg_connections:.2f}")
    print()
    print("Crime Type Distribution:")
    crime_counts = incidents_df['crime_type'].value_counts()
    for crime_type, count in crime_counts.items():
        percentage = (count / len(incidents_df)) * 100
        print(f"  {crime_type}: {count} ({percentage:.1f}%)")
    print()
    print("Temporal Anomaly:")
    oct_2025_vehicle_thefts = len(incidents_df[
        (incidents_df['crime_type'] == 'Vehicle Theft') & 
        (pd.to_datetime(incidents_df['timestamp']).dt.year == 2025) &
        (pd.to_datetime(incidents_df['timestamp']).dt.month == 10)
    ])
    print(f"  Vehicle Thefts in Bengaluru, October 2025: {oct_2025_vehicle_thefts}")
    print()
    print("Output Files:")
    print("  - districts.csv")
    print("  - criminals.csv")
    print("  - associations.csv")
    print("  - incidents.csv")
    print()
    print("Ready for PostgreSQL/PostGIS import!")
    print("=" * 60)


if __name__ == "__main__":
    main()
