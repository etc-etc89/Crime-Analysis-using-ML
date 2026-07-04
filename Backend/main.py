from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import uvicorn
import math
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Initialize the FastAPI App
app = FastAPI(
    title="KSP Crime Analytics API",
    description="Backend API for the Datathon 2026 AI-Driven Analytics Platform",
    version="1.0.0"
)

# Enable CORS so the React frontend can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- IN-MEMORY DATABASE ---
# For the hackathon prototype, we will load the CSVs into Pandas DataFrames on startup.
# In a real production environment, these would be PostgreSQL/PostGIS queries.
DB = {}

# --- ML MODEL ---
# Random Forest model for threat prediction
rf_model = None

# --- PYDANTIC SCHEMAS ---
class SuspectProfile(BaseModel):
    age: int
    base_risk_score: int
    connections: int

@app.on_event("startup")
async def load_data():
    """Loads the enriched CSV files into memory when the server starts."""
    global rf_model
    
    print("Initializing In-Memory Database...")
    try:
        DB['districts'] = pd.read_csv('districts.csv')
        DB['associations'] = pd.read_csv('associations.csv')
        
        # Load the enriched files if they exist (generated from EDA), fallback to original if not
        try:
            DB['criminals'] = pd.read_csv('criminals_enriched.csv')
            print("✓ Loaded criminals_enriched.csv")
        except FileNotFoundError:
            DB['criminals'] = pd.read_csv('criminals.csv')
            print("⚠️  Warning: criminals_enriched.csv not found, falling back to criminals.csv")
            
        try:
            DB['incidents'] = pd.read_csv('incidents_time_engineered.csv')
            print("✓ Loaded incidents_time_engineered.csv")
        except FileNotFoundError:
            DB['incidents'] = pd.read_csv('incidents.csv')
            DB['incidents']['timestamp'] = pd.to_datetime(DB['incidents']['timestamp'])
            print("⚠️  Warning: incidents_time_engineered.csv not found, falling back to incidents.csv")

        print("✅ Database loaded successfully.")
    except Exception as e:
        print(f"❌ CRITICAL ERROR loading CSV files: {str(e)}")
        print("Please ensure your CSV files are in the same directory as main.py")
    
    # --- LOAD ML MODEL ---
    print("\n🧠 Loading Machine Learning Model...")
    try:
        rf_model = joblib.load('random_forest_model.joblib')
        print("✅ ML Risk Prediction Model loaded successfully.")
        print(f"   Model Type: Random Forest Classifier")
        print(f"   Features: age, base_risk_score, connections")
        print(f"   Classes: {rf_model.classes_}")
    except FileNotFoundError:
        rf_model = None
        print("⚠️  Warning: ML model not found. Did you run ml_pipeline.py?")
        print("   The /api/v1/predict-risk endpoint will not be available.")
    except Exception as e:
        rf_model = None
        print(f"❌ Error loading ML model: {str(e)}")


# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "operational", "node": "KRN-01", "service": "KSP Analytics API"}

@app.get("/api/v1/overview/stats")
def get_global_stats():
    """Returns high-level metrics for the overview dashboard."""
    if not DB: raise HTTPException(status_code=503, detail="Database not initialized")
    
    crime_counts = DB['incidents']['crime_type'].value_counts().to_dict()
    
    return {
        "total_incidents": len(DB['incidents']),
        "total_criminals": len(DB['criminals']),
        "total_associations": len(DB['associations']),
        "crime_breakdown": [{"name": k, "value": v} for k, v in crime_counts.items()]
    }

@app.get("/api/v1/analytics/timeline")
def get_anomaly_timeline():
    """
    Advanced Anomaly Detection using Isolation Forest ML Algorithm.
    Detects multidimensional anomalies in crime incident patterns over time.
    """
    if 'incidents' not in DB: 
        raise HTTPException(status_code=503, detail="Incidents data not available")
    
    df = DB['incidents'].copy()
    
    # Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
    # Group by Month (YYYY-MM) and extract temporal features
    df['month'] = df['timestamp'].dt.to_period('M')
    df['month_str'] = df['month'].astype(str)
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['hour'] = df['timestamp'].dt.hour
    
    # Create rich feature set for each month
    monthly_features = df.groupby('month_str').agg({
        'incident_id': 'count',  # Total incidents
        'day_of_week': ['mean', 'std'],  # Average day pattern
        'hour': ['mean', 'std'],  # Average hour pattern
        'crime_type': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]  # Most common crime type
    }).reset_index()
    
    # Flatten multi-level columns
    monthly_features.columns = ['month', 'incidents', 'avg_day', 'std_day', 'avg_hour', 'std_hour', 'dominant_crime']
    
    # Fill NaN standard deviations (for months with only 1 incident)
    monthly_features['std_day'] = monthly_features['std_day'].fillna(0)
    monthly_features['std_hour'] = monthly_features['std_hour'].fillna(0)
    
    # Prepare feature matrix for Isolation Forest
    feature_cols = ['incidents', 'avg_day', 'std_day', 'avg_hour', 'std_hour']
    X = monthly_features[feature_cols].values
    
    # Standardize features for better ML performance
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest (unsupervised ML anomaly detection)
    # contamination=0.1 means we expect ~10% of months to be anomalous
    iso_forest = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100
    )
    
    # Predict anomalies: -1 = anomaly, 1 = normal
    predictions = iso_forest.fit_predict(X_scaled)
    
    # Get anomaly scores (lower = more anomalous)
    anomaly_scores = iso_forest.score_samples(X_scaled)
    
    # Normalize anomaly scores to 0-100 scale (inverted: higher = more anomalous)
    min_score = anomaly_scores.min()
    max_score = anomaly_scores.max()
    normalized_scores = 100 * (1 - (anomaly_scores - min_score) / (max_score - min_score + 1e-10))
    
    # Build response
    results = []
    for idx, row in monthly_features.iterrows():
        results.append({
            "date": row['month'],
            "incidents": int(row['incidents']),
            "isAnomaly": bool(predictions[idx] == -1),
            "anomalyScore": round(float(normalized_scores[idx]), 2),
            "avgDayOfWeek": round(float(row['avg_day']), 2),
            "avgHour": round(float(row['avg_hour']), 2),
            "dominantCrime": str(row['dominant_crime'])
        })
        
    return sorted(results, key=lambda x: x['date'])

@app.get("/api/v1/geospatial/hotspots")
def get_map_hotspots(limit: int = 2000):
    """Returns a sampled list of coordinates for the ScatterChart Map."""
    if 'incidents' not in DB: raise HTTPException(status_code=503, detail="Incidents data not available")
    
    # We sample the data to prevent overwhelming the browser's rendering engine
    df = DB['incidents'].sample(n=min(limit, len(DB['incidents'])))
    
    # Filter out any NaN coordinates
    df = df.dropna(subset=['latitude', 'longitude'])
    
    return df[['longitude', 'latitude', 'crime_type']].rename(columns={'longitude': 'x', 'latitude': 'y', 'crime_type': 'type'}).to_dict('records')


@app.get("/api/v1/network/kingpins")
def get_network_kingpins(top_n: int = 10):
    """Calculates Degree Centrality to find the top targets."""
    if 'associations' not in DB or 'criminals' not in DB:
        raise HTTPException(status_code=503, detail="Network data not available")
    
    # Calculate degrees (connections) per criminal
    assoc_df = DB['associations']
    all_nodes = pd.concat([assoc_df['source_id'], assoc_df['target_id']])
    degree_counts = all_nodes.value_counts().to_dict()
    
    criminals_df = DB['criminals'].copy()
    
    # Map connections back to profiles
    criminals_df['connections'] = criminals_df['criminal_id'].map(degree_counts).fillna(0)
    
    # Sort and take top N
    kingpins = criminals_df.sort_values(by='connections', ascending=False).head(top_n)
    
    # Format for JSON response
    results = []
    for _, row in kingpins.iterrows():
        # Handle NaN values safely for JSON serialization
        risk_score = row.get('base_risk_score', 0)
        results.append({
            "id": str(row['criminal_id']),
            "name": str(row['name']),
            "age": int(row['age']) if not math.isnan(row.get('age', float('nan'))) else None,
            "base_risk_score": int(risk_score) if not math.isnan(risk_score) else 0,
            "threat_level": str(row.get('threat_level', 'Unknown')),
            "connections": int(row['connections'])
        })
        
    return results


@app.post("/api/v1/predict-risk")
def predict_suspect_risk(suspect: SuspectProfile):
    """
    🧠 AI-Powered Threat Prediction Endpoint
    
    Takes live suspect features and runs them through the Random Forest Classifier
    to predict their operational threat level.
    
    Features analyzed:
    - Age: Suspect's age
    - Base Risk Score: Initial risk assessment (0-100)
    - Connections: Number of known criminal associations
    
    Returns:
    - Predicted threat level (Critical, High, Medium, Low)
    - AI confidence score (0-100%)
    - Input features analyzed
    """
    if rf_model is None:
        raise HTTPException(
            status_code=503, 
            detail="Machine Learning model is not available. Please run ml_pipeline.py to train the model."
        )
    
    try:
        # Scikit-learn expects a 2D array: [[age, risk, connections]]
        features = np.array([[suspect.age, suspect.base_risk_score, suspect.connections]])
        
        # Run prediction
        prediction = rf_model.predict(features)[0]  # e.g., "Critical", "High", "Medium", "Low"
        
        # Calculate confidence score by extracting prediction probabilities
        probabilities = rf_model.predict_proba(features)[0]
        confidence = round(max(probabilities) * 100, 1)
        
        # Get all class probabilities for detailed analysis
        class_probabilities = {
            cls: round(prob * 100, 1) 
            for cls, prob in zip(rf_model.classes_, probabilities)
        }
        
        return {
            "status": "success",
            "predicted_threat_level": prediction,
            "ai_confidence_score": f"{confidence}%",
            "confidence_raw": confidence,
            "class_probabilities": class_probabilities,
            "inputs_analyzed": suspect.dict(),
            "model_info": {
                "algorithm": "Random Forest Classifier",
                "features": ["age", "base_risk_score", "connections"],
                "classes": list(rf_model.classes_)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    print("Starting KSP Analytics API Server...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)