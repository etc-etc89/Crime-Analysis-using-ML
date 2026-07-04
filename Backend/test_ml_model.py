"""
ML Model Testing Script
Tests the Random Forest model with sample predictions
"""

import joblib
import pandas as pd
import numpy as np

print("="*70)
print("🧪 Testing Random Forest Threat Prediction Model")
print("="*70)

# Load the trained model
print("\n📦 Loading model...")
try:
    model = joblib.load('random_forest_model.joblib')
    print("✅ Model loaded successfully!")
except FileNotFoundError:
    print("❌ Error: random_forest_model.joblib not found!")
    print("   Run 'python ml_pipeline.py' first to train the model.")
    exit(1)

# Test cases - various criminal profiles
test_cases = [
    {"name": "Low Risk Offender", "age": 25, "base_risk_score": 15, "connections": 5},
    {"name": "Medium Risk Offender", "age": 35, "base_risk_score": 45, "connections": 20},
    {"name": "High Risk Offender", "age": 42, "base_risk_score": 75, "connections": 50},
    {"name": "Critical Risk Offender", "age": 38, "base_risk_score": 92, "connections": 120},
    {"name": "Young Low Connections", "age": 21, "base_risk_score": 30, "connections": 3},
    {"name": "Senior High Connections", "age": 55, "base_risk_score": 60, "connections": 85},
]

print("\n🎯 Running Predictions on Test Cases:")
print("-" * 70)

for i, test_case in enumerate(test_cases, 1):
    # Prepare features
    features = pd.DataFrame([[
        test_case['age'],
        test_case['base_risk_score'],
        test_case['connections']
    ]], columns=['age', 'base_risk_score', 'connections'])
    
    # Make prediction
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    confidence = probabilities.max() * 100
    
    # Get all class probabilities
    classes = model.classes_
    prob_dict = {cls: prob * 100 for cls, prob in zip(classes, probabilities)}
    
    print(f"\n{i}. {test_case['name']}")
    print(f"   Input: Age={test_case['age']}, Risk={test_case['base_risk_score']}, Connections={test_case['connections']}")
    print(f"   ⚠️  Predicted Threat Level: {prediction}")
    print(f"   📊 Confidence: {confidence:.1f}%")
    print(f"   📈 Probabilities:")
    for cls in sorted(classes):
        bar = "█" * int(prob_dict[cls] / 5)
        print(f"      {cls:8s}: {prob_dict[cls]:5.1f}% {bar}")

# Load actual data for validation
print("\n" + "="*70)
print("✅ Validation Against Actual Data")
print("="*70)

try:
    # Load criminals data
    criminals_df = pd.read_csv('criminals_enriched.csv')
    associations_df = pd.read_csv('associations.csv')
    
    # Calculate connections
    source_counts = associations_df['source_id'].value_counts()
    target_counts = associations_df['target_id'].value_counts()
    total_connections = source_counts.add(target_counts, fill_value=0)
    criminals_df['connections'] = criminals_df['criminal_id'].map(total_connections).fillna(0).astype(int)
    
    # Sample 5 random criminals
    sample = criminals_df.sample(5, random_state=42)
    
    print("\n🔍 Random Sample Predictions vs Actual:")
    print("-" * 70)
    
    correct = 0
    for idx, row in sample.iterrows():
        features = pd.DataFrame([[
            row['age'],
            row['base_risk_score'],
            row['connections']
        ]], columns=['age', 'base_risk_score', 'connections'])
        
        prediction = model.predict(features)[0]
        actual = row['threat_level']
        match = "✅" if prediction == actual else "❌"
        
        print(f"\n{match} Criminal: {row['name']}")
        print(f"   Age: {row['age']}, Risk: {row['base_risk_score']}, Connections: {row['connections']}")
        print(f"   Predicted: {prediction} | Actual: {actual}")
        
        if prediction == actual:
            correct += 1
    
    accuracy = (correct / len(sample)) * 100
    print(f"\n📊 Sample Accuracy: {correct}/{len(sample)} ({accuracy:.0f}%)")
    
except FileNotFoundError as e:
    print(f"\n⚠️  Could not load data files for validation: {e}")

print("\n" + "="*70)
print("✅ MODEL TESTING COMPLETE")
print("="*70)
print("\n💡 Next Steps:")
print("   1. Integrate this model into FastAPI backend")
print("   2. Create /predict-threat endpoint")
print("   3. Use for real-time threat assessment")
print("="*70)
