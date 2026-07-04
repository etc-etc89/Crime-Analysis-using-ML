import React, { useState } from 'react';
import { Search, AlertTriangle, Shield, Cpu, Brain, Zap } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface PredictionResult {
  status: string;
  predicted_threat_level: string;
  ai_confidence_score: string;
  confidence_raw: number;
  class_probabilities: Record<string, number>;
  inputs_analyzed: {
    age: number;
    base_risk_score: number;
    connections: number;
  };
  model_info: {
    algorithm: string;
    features: string[];
    classes: string[];
  };
}

export function AIThreatAnalyzer() {
  const [inputs, setInputs] = useState({ 
    age: 30, 
    base_risk_score: 50, 
    connections: 10 
  });
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // NOTE: Update this URL to your production backend URL when deploying
      const response = await fetch('http://127.0.0.1:8000/api/v1/predict-risk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputs)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Prediction failed');
      }

      const result = await response.json();
      setPrediction(result);
    } catch (err) {
      console.error("Failed to fetch AI prediction:", err);
      setError(err instanceof Error ? err.message : 'Failed to connect to AI service');
    } finally {
      setLoading(false);
    }
  };

  const getThreatColor = (level: string) => {
    switch (level) {
      case 'Critical': return 'text-red-500';
      case 'High': return 'text-orange-500';
      case 'Medium': return 'text-yellow-500';
      case 'Low': return 'text-green-500';
      default: return 'text-slate-500';
    }
  };

  const getThreatBgColor = (level: string) => {
    switch (level) {
      case 'Critical': return 'bg-red-900/20 border-red-500/50';
      case 'High': return 'bg-orange-900/20 border-orange-500/50';
      case 'Medium': return 'bg-yellow-900/20 border-yellow-500/50';
      case 'Low': return 'bg-green-900/20 border-green-500/50';
      default: return 'bg-slate-900/20 border-slate-500/50';
    }
  };

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/10 rounded-lg">
            <Brain className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <CardTitle className="text-lg font-bold text-slate-100 flex items-center gap-2">
              Live AI Threat Analyzer
              <Badge variant="outline" className="text-xs font-mono border-purple-500/50 text-purple-400">
                <Cpu className="w-3 h-3 mr-1" />
                ML-Powered
              </Badge>
            </CardTitle>
            <CardDescription className="text-slate-400">
              Enter suspect attributes to run real-time classification against the trained Random Forest model
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Input Form */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="age" className="text-xs font-mono text-slate-400 uppercase">
              Suspect Age
            </Label>
            <Input
              id="age"
              type="number"
              min="18"
              max="65"
              className="bg-slate-950 border-slate-700 text-slate-100"
              value={inputs.age}
              onChange={e => setInputs({...inputs, age: parseInt(e.target.value) || 18})}
            />
            <p className="text-xs text-slate-500">Range: 18-65 years</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="risk" className="text-xs font-mono text-slate-400 uppercase">
              Base Risk Score
            </Label>
            <Input
              id="risk"
              type="number"
              min="0"
              max="100"
              className="bg-slate-950 border-slate-700 text-slate-100"
              value={inputs.base_risk_score}
              onChange={e => setInputs({...inputs, base_risk_score: parseInt(e.target.value) || 0})}
            />
            <p className="text-xs text-slate-500">Range: 0-100</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="connections" className="text-xs font-mono text-slate-400 uppercase">
              Known Connections
            </Label>
            <Input
              id="connections"
              type="number"
              min="0"
              className="bg-slate-950 border-slate-700 text-slate-100"
              value={inputs.connections}
              onChange={e => setInputs({...inputs, connections: parseInt(e.target.value) || 0})}
            />
            <p className="text-xs text-slate-500">Network associations</p>
          </div>
        </div>

        {/* Predict Button */}
        <Button
          onClick={handlePredict}
          disabled={loading}
          className="w-full py-6 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold text-base transition-all"
        >
          {loading ? (
            <>
              <Zap className="w-4 h-4 mr-2 animate-pulse" />
              Analyzing Neural Pathways...
            </>
          ) : (
            <>
              <Brain className="w-4 h-4 mr-2" />
              Generate Threat Prediction
            </>
          )}
        </Button>

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-900/20 border border-red-500/50 rounded-lg">
            <p className="text-sm text-red-400">
              <strong>Error:</strong> {error}
            </p>
            <p className="text-xs text-red-300 mt-2">
              Make sure the backend server is running at http://127.0.0.1:8000
            </p>
          </div>
        )}

        {/* Results Panel */}
        {prediction && (
          <div className="space-y-4 animate-in fade-in duration-500">
            {/* Main Prediction */}
            <div className={`p-6 rounded-lg border-2 flex items-start gap-4 ${getThreatBgColor(prediction.predicted_threat_level)}`}>
              <AlertTriangle className={`w-10 h-10 ${getThreatColor(prediction.predicted_threat_level)} flex-shrink-0`} />
              <div className="flex-1">
                <p className="text-xs font-mono text-slate-400 mb-1">AI CLASSIFICATION</p>
                <h4 className={`text-3xl font-bold uppercase ${getThreatColor(prediction.predicted_threat_level)}`}>
                  {prediction.predicted_threat_level} THREAT
                </h4>
                <p className="text-sm mt-2 text-slate-300">
                  The Random Forest algorithm is{' '}
                  <strong className="text-white">{prediction.ai_confidence_score}</strong>{' '}
                  confident in this classification
                </p>
              </div>
            </div>

            {/* Probability Breakdown */}
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
              <h5 className="text-xs font-mono text-slate-400 uppercase mb-3 flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Probability Distribution
              </h5>
              <div className="space-y-2">
                {Object.entries(prediction.class_probabilities)
                  .sort((a, b) => b[1] - a[1])
                  .map(([className, probability]) => (
                    <div key={className} className="space-y-1">
                      <div className="flex justify-between items-center text-sm">
                        <span className={`font-medium ${getThreatColor(className)}`}>
                          {className}
                        </span>
                        <span className="text-slate-400 font-mono">
                          {probability.toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all duration-500 ${
                            className === 'Critical' ? 'bg-red-500' :
                            className === 'High' ? 'bg-orange-500' :
                            className === 'Medium' ? 'bg-yellow-500' :
                            'bg-green-500'
                          }`}
                          style={{ width: `${probability}%` }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            {/* Model Info */}
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
              <h5 className="text-xs font-mono text-slate-400 uppercase mb-3">Model Information</h5>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-slate-500 text-xs">Algorithm</p>
                  <p className="text-slate-200 font-medium">{prediction.model_info.algorithm}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs">Features Analyzed</p>
                  <p className="text-slate-200 font-medium">{prediction.model_info.features.length}</p>
                </div>
                <div className="col-span-2">
                  <p className="text-slate-500 text-xs mb-1">Input Values</p>
                  <div className="flex gap-2 flex-wrap">
                    <Badge variant="secondary" className="font-mono text-xs">
                      Age: {prediction.inputs_analyzed.age}
                    </Badge>
                    <Badge variant="secondary" className="font-mono text-xs">
                      Risk: {prediction.inputs_analyzed.base_risk_score}
                    </Badge>
                    <Badge variant="secondary" className="font-mono text-xs">
                      Connections: {prediction.inputs_analyzed.connections}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Quick Test Examples */}
        {!prediction && (
          <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
            <h5 className="text-xs font-mono text-slate-400 uppercase mb-3">Quick Test Examples</h5>
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setInputs({ age: 22, base_risk_score: 30, connections: 12 })}
                className="text-xs"
              >
                Low Risk Profile
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setInputs({ age: 35, base_risk_score: 75, connections: 45 })}
                className="text-xs"
              >
                High Risk Profile
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setInputs({ age: 42, base_risk_score: 92, connections: 120 })}
                className="text-xs"
              >
                Critical Threat
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setInputs({ age: 28, base_risk_score: 55, connections: 25 })}
                className="text-xs"
              >
                Medium Risk
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
