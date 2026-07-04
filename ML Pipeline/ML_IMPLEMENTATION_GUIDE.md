# 🧠 Machine Learning Implementation Guide

**Project:** KSP Datathon 2026 - AI-Driven Crime Analytics Platform  
**Challenge 2:** AI/ML-based Pattern Detection & Predictive Risk Scoring

This document details the three core Machine Learning algorithms integrated into the platform to fulfill the "AI/ML-based pattern detection" and "Predictive risk scoring" requirements.

---

## 📊 Algorithms Overview

### 1. Predictive Risk Scoring (Random Forest Classifier)

**Algorithm:** `sklearn.ensemble.RandomForestClassifier`  
**Type:** Supervised Learning (Classification)

#### Objective
Predict the `threat_level` (Low, Medium, High, Critical) of an offender based on their profile and network connections.

#### How it Works
A Random Forest builds multiple decision trees during training and merges them together to get a more accurate and stable prediction.

#### Features Used (X)
- `age` - Age of the criminal
- `base_risk_score` - Initial risk assessment score (0-100)
- `connections` - Number of network connections from the associations graph

#### Target Label (y)
- `threat_level` - Classification: Low, Medium, High, or Critical

#### Hackathon Value
Instead of relying on static police records, this allows the system to instantly classify the threat level of a newly arrested suspect based on historical patterns.

#### Model Performance
- **Accuracy:** 100% on test set
- **Feature Importance:**
  - base_risk_score: 95.8%
  - age: 2.4%
  - connections: 1.8%

---

### 2. Advanced Anomaly Detection (Isolation Forest)

**Algorithm:** `sklearn.ensemble.IsolationForest`  
**Type:** Unsupervised Learning (Anomaly Detection)

#### Objective
Detect statistically significant spikes in crime volumes over time.

#### How it Works
Unlike standard Z-scores that look at bell curves, the Isolation Forest explicitly isolates anomalies by randomly selecting a feature and randomly selecting a split value. Anomalies (like a massive spike in Vehicle Thefts) require fewer splits to be isolated than normal daily crime rates.

#### Features Used
- Daily incident counts aggregated from timestamp data

#### Parameters
- `contamination=0.05` - Assumes ~5% of days may be anomalous

#### Hackathon Value
It adapts to non-linear data and multidimensional trends, providing a robust "Predictive Early Warning" system for the KSP.

#### Detection Results
- **Days Analyzed:** 899 days (2024-01-01 to 2026-06-17)
- **Average Daily Incidents:** 56.5
- **Peak Daily Incidents:** 105
- **Anomalies Detected:** 44 days (4.9%)
- **Top Anomaly Date:** 2025-10-19 with 105 incidents

---

### 3. Geospatial Hotspot Clustering (DBSCAN)

**Algorithm:** `sklearn.cluster.DBSCAN`  
**Type:** Unsupervised Learning (Clustering)

#### Objective
Mathematically group geographic coordinates into distinct "Crime Hotspots" rather than just plotting random points on a map.

#### How it Works
Density-Based Spatial Clustering of Applications with Noise (DBSCAN) groups together points that are closely packed together (points with many nearby neighbors), marking points that lie alone in low-density regions as outliers (noise).

#### Parameters Used
- `eps=0.05` - Roughly a 5km radius in degrees (~0.05° ≈ 5.5 km)
- `min_samples=50` - Minimum 50 crimes in radius to form a hotspot

#### Hackathon Value
The frontend map can use the output `cluster_id` to draw polygon boundaries around high-risk zones, isolating organized crime operations from random, isolated incidents.

#### Clustering Results
- **Incidents Analyzed:** 50,000 (sampled for performance)
- **Hotspots Identified:** 6 distinct geographical clusters
- **Hotspot Coverage:** 79.4% of incidents
- **Isolated Incidents:** 20.6% marked as noise
- **Largest Hotspot:** Cluster #0 with 25,964 incidents at (12.7748, 77.3132)

---

## 🚀 Execution Instructions

### Prerequisites
Ensure you have the required Python packages installed:
```bash
pip install pandas numpy scikit-learn joblib
```

### Required Data Files
The pipeline requires the following CSV files in the `Backend` directory:
- `criminals_enriched.csv` - Criminal profiles with threat levels
- `associations.csv` - Network connections between criminals
- `incidents_time_engineered.csv` - Incident records with timestamps and coordinates

### Running the Pipeline

**Option 1: Direct Execution**
```bash
cd "e:\Police\ML Pipeline\Notebook"
python machine_learning_pipeline.py
```

**Option 2: Backend Launcher**
```bash
cd "e:\Police\Backend"
python ml_pipeline.py
```

### Expected Outputs

The pipeline generates three files in the `Backend` directory:

1. **`random_forest_model.joblib`** (1.2 MB)
   - Trained Random Forest model for threat prediction
   - Load in FastAPI: `model = joblib.load('random_forest_model.joblib')`
   - Use for predictions: `model.predict([[age, risk_score, connections]])`

2. **`anomalies_detected.csv`** (20 KB)
   - Daily incident counts with anomaly flags
   - Columns: `date`, `incident_count`, `anomaly_label`, `is_anomaly`
   - Use for early warning dashboard

3. **`incidents_clustered.csv`** (7.3 MB)
   - Incident records with assigned cluster IDs
   - Columns: All incident fields + `cluster_id`
   - `cluster_id=-1` means isolated/noise
   - `cluster_id>=0` means part of a hotspot
   - Use for map visualization

---

## 🔗 FastAPI Integration

### Loading the Model

```python
import joblib
import pandas as pd
from fastapi import FastAPI

app = FastAPI()

# Load model at startup
model = joblib.load('random_forest_model.joblib')

@app.post("/predict-threat")
async def predict_threat(age: int, base_risk_score: int, connections: int):
    """Predict threat level for a criminal profile"""
    features = pd.DataFrame([[age, base_risk_score, connections]], 
                           columns=['age', 'base_risk_score', 'connections'])
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0].max()
    
    return {
        "threat_level": prediction,
        "confidence": float(probability)
    }
```

### Using Anomaly Detection Results

```python
@app.get("/anomalies")
async def get_anomalies():
    """Get detected crime spike anomalies"""
    anomalies_df = pd.read_csv('anomalies_detected.csv')
    anomaly_dates = anomalies_df[anomalies_df['is_anomaly'] == True]
    
    return {
        "anomalies": anomaly_dates.to_dict(orient='records'),
        "total_anomalies": len(anomaly_dates)
    }
```

### Using Cluster Data for Maps

```python
@app.get("/hotspots")
async def get_hotspots():
    """Get crime hotspot clusters"""
    clustered_df = pd.read_csv('incidents_clustered.csv')
    
    # Get hotspot centers
    hotspots = clustered_df[clustered_df['cluster_id'] != -1]
    cluster_centers = hotspots.groupby('cluster_id').agg({
        'latitude': 'mean',
        'longitude': 'mean',
        'incident_id': 'count'
    }).reset_index()
    
    return {
        "hotspots": cluster_centers.to_dict(orient='records')
    }
```

---

## 📈 Model Validation & Metrics

### Random Forest Classifier
- **Training Samples:** 4,000
- **Test Samples:** 1,000
- **Accuracy:** 100.00%
- **Precision (Weighted):** 1.00
- **Recall (Weighted):** 1.00
- **F1-Score (Weighted):** 1.00

### Isolation Forest
- **Contamination Rate:** 5%
- **Days Analyzed:** 899
- **Anomalies Found:** 44 (4.9%)
- **Method:** Unsupervised isolation-based detection

### DBSCAN Clustering
- **Radius (eps):** 0.05° (~5.5 km)
- **Min Samples:** 50
- **Clusters Found:** 6
- **Clustering Rate:** 79.4%
- **Noise Rate:** 20.6%

---

## 🎯 Next Steps for Integration

1. **Backend Integration**
   - ✅ Load `random_forest_model.joblib` in FastAPI `main.py`
   - ✅ Create `/predict-threat` endpoint
   - ✅ Create `/anomalies` endpoint for early warnings
   - ✅ Create `/hotspots` endpoint for map data

2. **Frontend Visualization**
   - Use cluster_id from `incidents_clustered.csv` to draw hotspot polygons
   - Display anomaly alerts from `anomalies_detected.csv`
   - Show threat predictions in criminal profiles

3. **Real-time Predictions**
   - When a new criminal is added, calculate their connections
   - Use the model to predict threat_level instantly
   - Display confidence scores

---

## 📚 Technical Documentation

### Dependencies
```txt
pandas>=1.5.0
numpy>=1.23.0
scikit-learn>=1.3.0
joblib>=1.3.0
```

### System Requirements
- Python 3.8+
- 4GB RAM minimum (8GB recommended for full dataset)
- 100MB disk space for model and outputs

### Performance Notes
- Random Forest training: ~2 seconds
- Isolation Forest: ~1 second
- DBSCAN clustering: ~5-10 seconds (with 50K sample)
- Full pipeline execution: ~15 seconds

---

## 🛠️ Troubleshooting

### Issue: FileNotFoundError
**Solution:** Ensure all CSV files are in the `Backend` directory:
- criminals_enriched.csv
- associations.csv
- incidents_time_engineered.csv

### Issue: Memory Error during DBSCAN
**Solution:** The script automatically samples to 50,000 incidents. If still experiencing issues, reduce the sample size in the code.

### Issue: Model predictions seem incorrect
**Solution:** Ensure input features match the training data format:
- age: integer (18-65)
- base_risk_score: integer (0-100)
- connections: integer (0+)

---

## 📞 Support

For questions or issues with the ML pipeline:
- Review the console output for detailed logs
- Check that all CSV files have the expected columns
- Verify scikit-learn version compatibility

---

**Last Updated:** June 22, 2026  
**Version:** 1.0  
**Author:** KSP Datathon 2026 Team
