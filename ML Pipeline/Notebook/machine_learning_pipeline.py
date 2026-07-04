"""
🧠 Machine Learning Pipeline Engine
KSP Datathon 2026 - AI-Driven Crime Analytics Platform
Challenge 2: AI/ML-based Pattern Detection & Predictive Risk Scoring

This script implements three core ML algorithms:
1. Random Forest Classifier - Predictive Risk Scoring
2. Isolation Forest - Advanced Anomaly Detection
3. DBSCAN - Geospatial Hotspot Clustering
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# Configure paths relative to project structure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', '..', 'Backend')
OUTPUT_DIR = DATA_DIR

print("="*70)
print("🧠 INITIALIZING KSP MACHINE LEARNING PIPELINE")
print("="*70)
print(f"📂 Data Directory: {DATA_DIR}")
print(f"📂 Output Directory: {OUTPUT_DIR}")
print("="*70)


def load_and_enrich_criminals():
    """
    Load criminals data and calculate network connections from associations.
    Returns enriched dataframe with 'connections' column.
    """
    # Load criminals and associations
    criminals_path = os.path.join(DATA_DIR, 'criminals_enriched.csv')
    associations_path = os.path.join(DATA_DIR, 'associations.csv')
    
    criminals_df = pd.read_csv(criminals_path)
    associations_df = pd.read_csv(associations_path)
    
    # Calculate connections for each criminal from the network graph
    source_counts = associations_df['source_id'].value_counts()
    target_counts = associations_df['target_id'].value_counts()
    total_connections = source_counts.add(target_counts, fill_value=0)
    
    # Map connections to criminals dataframe
    criminals_df['connections'] = criminals_df['criminal_id'].map(total_connections).fillna(0).astype(int)
    
    return criminals_df


def train_risk_classifier():
    """
    ALGORITHM 1: Random Forest Classifier (Supervised Learning)
    ============================================================
    Type: Classification
    Objective: Predict threat_level (Low, Medium, High, Critical) of offenders
    
    Features (X): age, base_risk_score, connections (from network graph)
    Target (y): threat_level
    
    How it works: A Random Forest builds multiple decision trees during training
    and merges them together to get a more accurate and stable prediction.
    
    Hackathon Value: Instead of relying on static police records, this allows
    the system to instantly classify the threat level of a newly arrested suspect
    based on historical patterns.
    """
    print("\n[1/3] 🎯 Training Random Forest Threat Classifier...")
    print("-" * 70)
    
    try:
        # Load and enrich criminals data with network connections
        criminals_df = load_and_enrich_criminals()
        print(f"✓ Loaded {len(criminals_df)} criminal records")
        
    except FileNotFoundError as e:
        print(f"❌ Error: Required data files not found - {e}")
        return None

    # Define features and target
    features = ['age', 'base_risk_score', 'connections']
    target = 'threat_level'
    
    # Clean data - remove any rows with missing values
    df_clean = criminals_df.dropna(subset=features + [target])
    print(f"✓ Cleaned dataset: {len(df_clean)} records ready for training")
    
    # Display feature statistics
    print(f"\n📊 Feature Statistics:")
    print(f"   Age range: {df_clean['age'].min():.0f} - {df_clean['age'].max():.0f}")
    print(f"   Risk score range: {df_clean['base_risk_score'].min():.0f} - {df_clean['base_risk_score'].max():.0f}")
    print(f"   Connections range: {df_clean['connections'].min():.0f} - {df_clean['connections'].max():.0f}")
    print(f"\n🎯 Target Distribution:")
    print(df_clean[target].value_counts().to_string())

    # Prepare features and target
    X = df_clean[features]
    y = df_clean[target]

    # Split into training and testing sets (80/20 split)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\n✓ Data split: {len(X_train)} training, {len(X_test)} testing samples")

    # Initialize and Train Random Forest Model
    # n_estimators=100: Build 100 decision trees
    # class_weight='balanced': Handle imbalanced threat levels
    print(f"\n🌲 Training Random Forest (100 trees)...")
    rf_model = RandomForestClassifier(
        n_estimators=100, 
        random_state=42, 
        class_weight='balanced',
        max_depth=10,
        min_samples_split=5
    )
    rf_model.fit(X_train, y_train)

    # Evaluate Model Performance
    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n📈 Model Performance:")
    print(f"   Accuracy: {accuracy:.2%}")
    print("\n📊 Detailed Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature Importance
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    print("🔍 Feature Importance:")
    for _, row in feature_importance.iterrows():
        print(f"   {row['feature']}: {row['importance']:.3f}")

    # Save the trained model
    model_path = os.path.join(OUTPUT_DIR, 'random_forest_model.joblib')
    joblib.dump(rf_model, model_path)
    print(f"\n✅ Model saved to: {model_path}")
    print("   → Ready for FastAPI integration!")
    
    return rf_model


def detect_temporal_anomalies():
    """
    ALGORITHM 2: Isolation Forest (Unsupervised Learning)
    =====================================================
    Type: Anomaly Detection
    Objective: Detect statistically significant spikes in crime volumes over time
    
    Features: Daily incident counts
    
    How it works: Unlike standard Z-scores that look at bell curves, the Isolation
    Forest explicitly isolates anomalies by randomly selecting a feature and split
    value. Anomalies (like a massive spike in Vehicle Thefts) require fewer splits
    to be isolated than normal daily crime rates.
    
    Hackathon Value: It adapts to non-linear data and multidimensional trends,
    providing a robust "Predictive Early Warning" system for the KSP.
    """
    print("\n[2/3] 🚨 Running Isolation Forest Anomaly Detection...")
    print("-" * 70)
    
    try:
        incidents_path = os.path.join(DATA_DIR, 'incidents_time_engineered.csv')
        incidents_df = pd.read_csv(incidents_path)
        print(f"✓ Loaded {len(incidents_df)} incident records")
        
    except FileNotFoundError as e:
        print(f"❌ Error: incidents_time_engineered.csv not found - {e}")
        return

    # Prepare Time-Series Data
    incidents_df['timestamp'] = pd.to_datetime(incidents_df['timestamp'])
    incidents_df['date'] = incidents_df['timestamp'].dt.date
    
    # Group by date to get daily crime volume
    daily_volume = incidents_df.groupby('date').size().reset_index(name='incident_count')
    print(f"✓ Analyzed {len(daily_volume)} days of crime data")
    print(f"   Date range: {daily_volume['date'].min()} to {daily_volume['date'].max()}")
    print(f"   Average daily incidents: {daily_volume['incident_count'].mean():.1f}")
    print(f"   Peak daily incidents: {daily_volume['incident_count'].max()}")

    # Initialize Isolation Forest
    # contamination=0.05: Assume ~5% of days might be anomalous spikes
    print(f"\n🌲 Training Isolation Forest (contamination=0.05)...")
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    
    # Fit and Predict
    # IsolationForest requires 2D array
    daily_volume['anomaly_label'] = iso_forest.fit_predict(daily_volume[['incident_count']])
    
    # Convert labels: -1 = anomaly, 1 = normal
    daily_volume['is_anomaly'] = daily_volume['anomaly_label'] == -1
    
    # Extract anomalies
    anomalies_detected = daily_volume[daily_volume['is_anomaly'] == True].copy()
    anomalies_detected = anomalies_detected.sort_values('incident_count', ascending=False)
    
    print(f"\n✅ Isolation Forest complete!")
    print(f"   🚨 Detected {len(anomalies_detected)} anomalous days ({len(anomalies_detected)/len(daily_volume)*100:.1f}%)")
    
    if not anomalies_detected.empty:
        print(f"\n🔥 Top 5 Anomalous Crime Spikes:")
        for idx, row in anomalies_detected.head(5).iterrows():
            print(f"   {row['date']}: {row['incident_count']} incidents")
    
    # Save anomaly results
    anomaly_path = os.path.join(OUTPUT_DIR, 'anomalies_detected.csv')
    daily_volume.to_csv(anomaly_path, index=False)
    print(f"\n💾 Anomaly results saved to: {anomaly_path}")


def cluster_geospatial_hotspots():
    """
    ALGORITHM 3: DBSCAN (Unsupervised Learning)
    ===========================================
    Type: Clustering
    Objective: Mathematically group geographic coordinates into distinct
    "Crime Hotspots" rather than just plotting random points on a map
    
    Parameters: eps=0.05 (roughly 5km radius), min_samples=50
    
    How it works: Density-Based Spatial Clustering of Applications with Noise
    (DBSCAN) groups together points that are closely packed together (points
    with many nearby neighbors), marking points in low-density regions as
    outliers (noise).
    
    Hackathon Value: The frontend map can use the output cluster_id to draw
    polygon boundaries around high-risk zones, isolating organized crime
    operations from random, isolated incidents.
    """
    print("\n[3/3] 🗺️  Running DBSCAN Geospatial Clustering...")
    print("-" * 70)
    
    try:
        incidents_path = os.path.join(DATA_DIR, 'incidents_time_engineered.csv')
        incidents_df = pd.read_csv(incidents_path)
        print(f"✓ Loaded {len(incidents_df)} incident records")
        
    except FileNotFoundError as e:
        print(f"❌ Error: incidents_time_engineered.csv not found - {e}")
        return

    # Clean data - remove any rows with missing coordinates
    incidents_clean = incidents_df.dropna(subset=['latitude', 'longitude']).copy()
    print(f"✓ Cleaned dataset: {len(incidents_clean)} records with valid coordinates")
    
    # For performance, sample data if dataset is very large
    if len(incidents_clean) > 50000:
        print(f"⚡ Sampling 50,000 incidents for clustering (performance optimization)")
        sample_df = incidents_clean.sample(n=50000, random_state=42)
    else:
        sample_df = incidents_clean
    
    coordinates = sample_df[['latitude', 'longitude']].values
    print(f"📍 Coordinate range:")
    print(f"   Latitude: {coordinates[:, 0].min():.4f} to {coordinates[:, 0].max():.4f}")
    print(f"   Longitude: {coordinates[:, 1].min():.4f} to {coordinates[:, 1].max():.4f}")

    # Initialize DBSCAN
    # eps=0.05: Roughly 5km radius in degrees (~0.05 degrees ≈ 5.5 km)
    # min_samples=50: Need 50 crimes in radius to form a hotspot
    print(f"\n🎯 Running DBSCAN (eps=0.05, min_samples=50)...")
    dbscan = DBSCAN(eps=0.05, min_samples=50)
    
    # Fit the model and get cluster labels
    sample_df['cluster_id'] = dbscan.fit_predict(coordinates)
    
    # Analyze results
    # cluster_id = -1 means "noise" (isolated crimes)
    # cluster_id >= 0 means part of a dense hotspot
    hotspots = sample_df[sample_df['cluster_id'] != -1]
    noise = sample_df[sample_df['cluster_id'] == -1]
    
    num_clusters = len(set(hotspots['cluster_id']))
    
    print(f"\n✅ DBSCAN Clustering Complete!")
    print(f"   🔴 Identified {num_clusters} distinct geographical hotspots")
    print(f"   📊 Hotspot incidents: {len(hotspots)} ({len(hotspots)/len(sample_df)*100:.1f}%)")
    print(f"   📊 Isolated/Noise incidents: {len(noise)} ({len(noise)/len(sample_df)*100:.1f}%)")
    
    # Cluster statistics
    if num_clusters > 0:
        cluster_sizes = hotspots['cluster_id'].value_counts().sort_values(ascending=False)
        print(f"\n🗺️  Top 5 Largest Hotspots:")
        for cluster_id, size in cluster_sizes.head(5).items():
            cluster_data = hotspots[hotspots['cluster_id'] == cluster_id]
            center_lat = cluster_data['latitude'].mean()
            center_lon = cluster_data['longitude'].mean()
            print(f"   Hotspot #{cluster_id}: {size} incidents at ({center_lat:.4f}, {center_lon:.4f})")
    
    # Save the clustered data for map visualization
    output_path = os.path.join(OUTPUT_DIR, 'incidents_clustered.csv')
    sample_df.to_csv(output_path, index=False)
    print(f"\n💾 Clustered data saved to: {output_path}")
    print("   → Ready for frontend map visualization!")


if __name__ == "__main__":
    print("\n🚀 Starting ML Pipeline Execution...\n")
    
    # Execute all three ML algorithms
    train_risk_classifier()
    detect_temporal_anomalies()
    cluster_geospatial_hotspots()
    
    print("\n" + "="*70)
    print("✅ ML PIPELINE EXECUTION COMPLETE")
    print("="*70)
    print("\n📦 Generated Outputs:")
    print("   1. random_forest_model.joblib - Threat prediction model")
    print("   2. anomalies_detected.csv - Temporal crime spikes")
    print("   3. incidents_clustered.csv - Geospatial hotspots")
    print("\n🔗 Next Steps:")
    print("   → Integrate random_forest_model.joblib into FastAPI backend")
    print("   → Use anomalies_detected.csv for early warning dashboard")
    print("   → Visualize incidents_clustered.csv on frontend map")
    print("="*70)