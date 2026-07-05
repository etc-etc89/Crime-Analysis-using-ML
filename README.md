# 🚨 KSP Crime Analytics Platform

<div align="center">

**AI-Driven Crime Analytics & Intelligence System**

*KSP Datathon 2026 - Challenge 2: AI/ML-based Pattern Detection & Predictive Risk Scoring*

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![React](https://img.shields.io/badge/React-19.2-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-blue.svg)
![Machine Learning](https://img.shields.io/badge/ML-scikit--learn-orange.svg)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Machine Learning Algorithms](#-machine-learning-algorithms)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [API Documentation](#-api-documentation)
- [Usage Guide](#-usage-guide)
- [Contributing](#-contributing)

---

## 🎯 Overview

The **KSP Crime Analytics Platform** is an advanced AI-powered intelligence system designed for the Karnataka State Police. It leverages cutting-edge machine learning algorithms to detect crime patterns, predict threat levels, identify geographical hotspots, and analyze criminal networks.

This platform transforms raw crime data into actionable intelligence, enabling law enforcement to:
- 🎯 **Predict** offender threat levels in real-time
- 🚨 **Detect** anomalous crime spikes automatically
- 🗺️ **Identify** geographical crime hotspots
- 🔗 **Map** criminal network connections
- 📊 **Visualize** comprehensive crime analytics

### 🏆 Hackathon Challenge

Built for the **KSP Datathon 2026**, this solution addresses Challenge 2's requirements:
- **AI/ML Pattern Detection**: Advanced unsupervised and supervised learning algorithms
- **Predictive Risk Scoring**: Real-time threat level classification
- **Interactive Dashboard**: Modern, responsive web interface
- **RESTful API**: Scalable backend architecture

---

## ✨ Key Features

### 🧠 Machine Learning Capabilities

1. **Predictive Threat Scoring**
   - Random Forest Classifier for real-time offender risk assessment
   - Analyzes age, base risk score, and network connections
   - Classifies threats into: Low, Medium, High, Critical
   - 80%+ prediction accuracy

2. **Anomaly Detection**
   - Isolation Forest algorithm for temporal crime spike detection
   - Identifies unusual crime volume patterns
   - ML-driven early warning system
   - Adapts to non-linear trends

3. **Geospatial Hotspot Clustering**
   - DBSCAN algorithm for crime density analysis
   - Automatically identifies high-crime zones
   - Distinguishes organized crime areas from isolated incidents
   - Map-ready polygon boundaries

### 📊 Analytics Dashboard

- **Executive Overview**: Real-time KPIs and crime statistics
- **Timeline Analysis**: 24-month incident trends with ML anomaly overlay
- **Interactive Maps**: Geospatial visualization with 2000+ hotspot coordinates
- **Network Intelligence**: Criminal association graphs and kingpin identification
- **AI Threat Analyzer**: Live threat prediction interface

### 🔧 Technical Features

- **RESTful API**: FastAPI backend with automatic documentation
- **Real-time Processing**: Sub-second response times
- **Mock Data Fallback**: Fully functional UI even without backend
- **Responsive Design**: Modern UI with Radix UI components
- **Type-Safe**: Full TypeScript implementation
- **CORS Enabled**: Seamless frontend-backend integration

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Dashboard   │  │  Analytics   │  │  Geospatial  │    │
│  │              │  │              │  │              │    │
│  │  - KPIs      │  │  - Timeline  │  │  - Hotspots  │    │
│  │  - Charts    │  │  - Anomalies │  │  - Clusters  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────────────────────────┐   │
│  │  Network     │  │  AI Threat Analyzer              │   │
│  │              │  │                                  │   │
│  │  - Kingpins  │  │  - Live Risk Prediction          │   │
│  │  - Assoc.    │  │  - ML Model Integration          │   │
│  └──────────────┘  └──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI + Python)             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    API Endpoints                     │  │
│  │  • /api/v1/overview/stats                           │  │
│  │  • /api/v1/analytics/timeline                       │  │
│  │  • /api/v1/geospatial/hotspots                      │  │
│  │  • /api/v1/network/kingpins                         │  │
│  │  • /api/v1/predict-risk                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ML Models & Algorithms                  │  │
│  │  • Random Forest Classifier (Threat Prediction)     │  │
│  │  • Isolation Forest (Anomaly Detection)             │  │
│  │  • DBSCAN (Geospatial Clustering)                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer (CSV Files)                   │
│  • criminals_enriched.csv                                   │
│  • incidents_time_engineered.csv                            │
│  • associations.csv                                         │
│  • districts.csv                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Machine Learning Algorithms

### 1. Random Forest Classifier (Supervised Learning)

**Purpose**: Predictive threat level classification

**Features**:
- Age of offender
- Base risk score (0-100)
- Number of criminal connections

**Output**: Threat Level (Low, Medium, High, Critical)

**Performance**: 80%+ accuracy with balanced class weights

**Implementation**:
```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    class_weight='balanced',
    random_state=42
)
```

**Use Case**: Instantly classify newly arrested suspects without manual profiling

---

### 2. Isolation Forest (Unsupervised Learning)

**Purpose**: Temporal anomaly detection in crime volumes

**Features**:
- Daily incident counts
- Day of week patterns
- Hour of day patterns
- Crime type distribution

**Output**: Anomaly score (0-100) and binary anomaly flag

**Contamination**: 10% (expects ~10% of time periods to be anomalous)

**Implementation**:
```python
IsolationForest(
    contamination=0.1,
    n_estimators=100,
    random_state=42
)
```

**Use Case**: Early warning system for crime spikes and unusual patterns

---

### 3. DBSCAN (Unsupervised Learning)

**Purpose**: Geospatial crime hotspot identification

**Features**:
- Latitude coordinates
- Longitude coordinates

**Parameters**:
- `eps=0.05` (≈5.5 km radius)
- `min_samples=50` (minimum 50 incidents to form a cluster)

**Output**: Cluster IDs for hotspot zones, noise classification for isolated incidents

**Implementation**:
```python
DBSCAN(
    eps=0.05,
    min_samples=50
)
```

**Use Case**: Identify organized crime zones vs. random isolated incidents

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.11
- **ML Libraries**: 
  - scikit-learn 1.3.2 (Random Forest, Isolation Forest, DBSCAN)
  - pandas 2.0.3 (Data manipulation)
  - numpy 1.25.2 (Numerical computing)
- **Model Persistence**: joblib
- **Server**: Uvicorn 0.24.0

### Frontend
- **Framework**: React 19.2 with TanStack Start
- **Language**: TypeScript 5.8
- **Routing**: TanStack Router 1.168
- **State Management**: TanStack Query 5.83
- **UI Components**: Radix UI
- **Styling**: Tailwind CSS 4.2
- **Charts**: Recharts 2.15
- **Build Tool**: Vite 8.0

### ML Pipeline
- **Data Processing**: pandas, numpy
- **Visualization**: matplotlib, seaborn
- **Network Analysis**: networkx
- **Data Generation**: Faker (for synthetic datasets)

---

## 📁 Project Structure

```
Crime-Analysis-using-ML-main/
├── Backend/
│   ├── main.py                          # FastAPI application
│   ├── ml_pipeline.py                   # ML pipeline launcher
│   ├── test_ml_model.py                 # Model testing script
│   ├── requirements.txt                 # Python dependencies
│   ├── random_forest_model.joblib       # Trained ML model
│   ├── criminals_enriched.csv           # Criminal profiles data
│   ├── incidents_time_engineered.csv    # Incident records with temporal features
│   ├── associations.csv                 # Criminal network connections
│   ├── districts.csv                    # District information
│   ├── incidents_clustered.csv          # Geospatial cluster results
│   └── anomalies_detected.csv           # Temporal anomaly results
│
├── Frontend/
│   ├── src/
│   │   ├── routes/
│   │   │   ├── index.tsx                # Dashboard page
│   │   │   ├── analytics.tsx            # Timeline & anomaly analysis
│   │   │   ├── geospatial.tsx           # Map visualization
│   │   │   ├── network.tsx              # Criminal network graph
│   │   │   ├── criminals.tsx            # AI threat analyzer
│   │   │   └── __root.tsx               # Root layout
│   │   ├── components/
│   │   │   ├── app-sidebar.tsx          # Navigation sidebar
│   │   │   ├── kpi-card.tsx             # KPI display component
│   │   │   ├── ai-threat-analyzer.tsx   # ML prediction interface
│   │   │   └── ui/                      # Radix UI components
│   │   ├── lib/
│   │   │   └── api.ts                   # API client with mock fallback
│   │   └── styles.css                   # Global styles
│   ├── package.json
│   └── vite.config.ts
│
└── ML Pipeline/
    ├── Notebook/
    │   ├── machine_learning_pipeline.py  # Core ML algorithms
    │   ├── generate_ksp_data.py         # Synthetic data generator
    │   ├── network_eda_analysis.py      # Network analysis
    │   ├── Criminals_EDA.ipynb          # Criminal data analysis
    │   ├── Incidents_EDA.ipynb          # Incident data analysis
    │   ├── Districts_EDA.ipynb          # District data analysis
    │   └── Network_EDA_Associations.ipynb # Network EDA
    ├── Data/                            # Raw data files
    ├── Output/                          # Analysis outputs
    └── requirements.txt                 # ML pipeline dependencies
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **npm** or **bun**: Latest version

### Backend Setup

1. **Navigate to Backend directory**:
   ```bash
   cd Backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Train ML models** (if not already trained):
   ```bash
   python ml_pipeline.py
   ```
   This generates:
   - `random_forest_model.joblib`
   - `anomalies_detected.csv`
   - `incidents_clustered.csv`

5. **Start the API server**:
   ```bash
   python main.py
   ```
   Server runs at: `http://localhost:8000`
   
   API docs available at: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to Frontend directory**:
   ```bash
   cd Frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or
   bun install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   # or
   bun run dev
   ```
   Frontend runs at: `http://localhost:3000` (default Vite port)

4. **Build for production**:
   ```bash
   npm run build
   npm run preview
   ```

### ML Pipeline Setup (Optional)

1. **Navigate to ML Pipeline directory**:
   ```bash
   cd "ML Pipeline"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run ML pipeline**:
   ```bash
   cd Notebook
   python machine_learning_pipeline.py
   ```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. **Health Check**
```http
GET /
```
**Response**:
```json
{
  "status": "operational",
  "node": "KRN-01",
  "service": "KSP Analytics API"
}
```

---

#### 2. **Overview Statistics**
```http
GET /api/v1/overview/stats
```
**Description**: Returns high-level crime metrics and breakdown by type

**Response**:
```json
{
  "total_incidents": 15243,
  "total_criminals": 8517,
  "total_associations": 12089,
  "crime_breakdown": [
    {"name": "Theft", "value": 6450},
    {"name": "Vehicle Theft", "value": 4500}
  ]
}
```

---

#### 3. **Timeline with Anomaly Detection**
```http
GET /api/v1/analytics/timeline
```
**Description**: Returns monthly incident trends with ML-detected anomalies

**Response**:
```json
[
  {
    "date": "2023-01",
    "incidents": 145,
    "isAnomaly": false,
    "anomalyScore": 23.45,
    "avgDayOfWeek": 3.2,
    "avgHour": 14.5,
    "dominantCrime": "Theft"
  }
]
```

---

#### 4. **Geospatial Hotspots**
```http
GET /api/v1/geospatial/hotspots?limit=2000
```
**Parameters**:
- `limit` (optional, default: 2000): Maximum number of coordinates to return

**Response**:
```json
[
  {
    "x": 77.5946,
    "y": 12.9716,
    "type": "Vehicle Theft"
  }
]
```

---

#### 5. **Network Kingpins**
```http
GET /api/v1/network/kingpins?top_n=10
```
**Parameters**:
- `top_n` (optional, default: 10): Number of top criminals to return

**Response**:
```json
[
  {
    "id": "crim-0042",
    "name": "Manan Shankar",
    "age": 38,
    "base_risk_score": 92,
    "threat_level": "High",
    "connections": 127
  }
]
```

---

#### 6. **AI Threat Prediction** 🧠
```http
POST /api/v1/predict-risk
```
**Description**: Predicts threat level using Random Forest ML model

**Request Body**:
```json
{
  "age": 35,
  "base_risk_score": 75,
  "connections": 50
}
```

**Response**:
```json
{
  "status": "success",
  "predicted_threat_level": "High",
  "ai_confidence_score": "87.3%",
  "confidence_raw": 87.3,
  "class_probabilities": {
    "Low": 2.1,
    "Medium": 10.6,
    "High": 87.3,
    "Critical": 0.0
  },
  "inputs_analyzed": {
    "age": 35,
    "base_risk_score": 75,
    "connections": 50
  },
  "model_info": {
    "algorithm": "Random Forest Classifier",
    "features": ["age", "base_risk_score", "connections"],
    "classes": ["Low", "Medium", "High", "Critical"]
  }
}
```

---

## 📖 Usage Guide

### Testing the ML Model

Run the test script to validate the trained Random Forest model:

```bash
cd Backend
python test_ml_model.py
```

This will:
- Load the trained model
- Run predictions on 6 test cases
- Validate against actual criminal data
- Display feature importance and accuracy metrics

### Using the AI Threat Analyzer

1. Navigate to the **Criminals** page in the frontend
2. Enter suspect details:
   - **Age**: Offender's age (e.g., 35)
   - **Base Risk Score**: Initial assessment (0-100)
   - **Connections**: Number of known criminal associations
3. Click **Analyze Threat**
4. View the ML prediction with confidence scores

### Viewing Anomalies

1. Navigate to the **Analytics** page
2. View the timeline chart
3. Red markers indicate ML-detected anomalous crime spikes
4. Hover over data points for detailed statistics

### Exploring Hotspots

1. Navigate to the **Geospatial** page
2. View the interactive map with 2000+ crime coordinates
3. Color-coded by crime type
4. Identify dense clusters (hotspots)

### Analyzing Criminal Networks

1. Navigate to the **Network** page
2. View top kingpins ranked by network connections
3. Analyze threat levels and risk scores
4. Identify high-priority targets

---

## 🔒 Security Considerations

### Production Deployment

⚠️ **Important**: The current configuration uses permissive CORS settings for development:

```python
allow_origins=["*"]  # In production, restrict this!
```

**For production**:
```python
allow_origins=[
    "https://your-frontend-domain.com",
    "https://ksp-analytics.gov.in"
]
```

### API Security Recommendations

1. **Authentication**: Implement JWT or API key authentication
2. **Rate Limiting**: Add request throttling to prevent abuse
3. **HTTPS Only**: Enforce TLS/SSL in production
4. **Input Validation**: Add Pydantic validators for all endpoints
5. **Database**: Migrate from CSV to PostgreSQL with encryption

---

## 🧪 Testing

### Backend Tests

```bash
cd Backend
python test_ml_model.py
```

### ML Pipeline Tests

```bash
cd "ML Pipeline/Notebook"
python machine_learning_pipeline.py
```

### Frontend Tests

```bash
cd Frontend
npm run lint
npm run format
```

---

## 📊 Data Sources

The platform uses enriched crime datasets including:

- **Criminals Database**: 8,500+ profiles with age, risk scores, and threat levels
- **Incident Records**: 15,000+ crime incidents with timestamps and coordinates
- **Association Network**: 12,000+ criminal connections
- **District Data**: Geographic boundary information

### Data Schema

**criminals_enriched.csv**:
```
criminal_id, name, age, base_risk_score, threat_level, connections
```

**incidents_time_engineered.csv**:
```
incident_id, timestamp, latitude, longitude, crime_type, district_id, hour, day_of_week, month
```

**associations.csv**:
```
source_id, target_id, relationship_type, strength
```

---

## 🚀 Future Enhancements

- [ ] Real-time streaming data integration
- [ ] Deep learning models (LSTM for time-series forecasting)
- [ ] Graph Neural Networks for network analysis
- [ ] Natural Language Processing for crime report analysis
- [ ] Mobile application (React Native)
- [ ] PostgreSQL/PostGIS database integration
- [ ] Advanced visualization (3D crime heatmaps)
- [ ] Automated report generation
- [ ] Multi-language support
- [ ] Role-based access control (RBAC)

---

## 🤝 Contributing

This project was developed for the **KSP Datathon 2026**. Contributions, issues, and feature requests are welcome!

### Development Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is developed for the Karnataka State Police Datathon 2026.

---

## 👥 Authors

Built with ❤️ for the **KSP Datathon 2026**

---

## 🙏 Acknowledgments

- Karnataka State Police for the challenge and dataset
- Lovable.dev for frontend development platform
- FastAPI and scikit-learn communities
- TanStack for modern React tooling

---

## 📞 Support

For questions or support regarding this project:

1. Check the [API Documentation](#-api-documentation)
2. Review the [Usage Guide](#-usage-guide)
3. Open an issue in the repository

---

<div align="center">

**Built for KSP Datathon 2026** 🚨

*Transforming Crime Data into Actionable Intelligence*

</div>
