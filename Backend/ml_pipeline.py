"""
ML Pipeline Launcher - KSP Datathon 2026
Quick execution wrapper for the Machine Learning Pipeline

Usage: python ml_pipeline.py
"""

import sys
import os

# Add the notebook directory to path
notebook_dir = os.path.join(os.path.dirname(__file__), '..', 'ML Pipeline', 'Notebook')
sys.path.insert(0, notebook_dir)

# Import and execute the main pipeline
from machine_learning_pipeline import train_risk_classifier, detect_temporal_anomalies, cluster_geospatial_hotspots

if __name__ == "__main__":
    print("="*70)
    print("🧠 KSP ML PIPELINE - Quick Launcher")
    print("="*70)
    
    # Execute all three algorithms
    train_risk_classifier()
    detect_temporal_anomalies()
    cluster_geospatial_hotspots()
    
    print("\n" + "="*70)
    print("✅ EXECUTION COMPLETE")
    print("="*70)
