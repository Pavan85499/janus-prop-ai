import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  BarChart3, 
  Target,
  Users,
  Brain,
  Activity,
  Star,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

interface LearningMetrics {
  agent_id: string;
  metric_date: string;
  total_predictions: number;
  accurate_predictions: number;
  accuracy_rate: number;
  average_confidence: number;
  user_satisfaction_score: number;
  improvement_trend: string;
  top_insight_types: Array<{
    insight_type: string;
    count: number;
    average_accuracy: number;
  }>;
  areas_for_improvement: string[];
}

interface UserFeedback {
  feedback_id: string;
  feedback_type: string;
  rating: number;
  timestamp: string;
  comment?: string;
}

interface LearningMetricsDashboardProps {
  onExportData: () => void;
  onGenerateReport: () => void;
}

const LearningMetricsDashboard: React.FC<LearningMetricsDashboardProps> = ({ 
  onExportData, 
  onGenerateReport 
}) => {
  const [metrics, setMetrics] = useState<LearningMetrics>({
    agent_id: "all",
    metric_date: new Date().toISOString(),
    total_predictions: 15420,
    accurate_predictions: 14250,
    accuracy_rate: 92.4,
    average_confidence: 0.78,
    user_satisfaction_score: 4.2,
    improvement_trend: "improving",
    top_insight_types: [
      { insight_type: "market_opportunity", count: 5230, average_accuracy: 0.89 },
      { insight_type: "investment_potential", count: 4890, average_accuracy: 0.85 },
      { insight_type: "risk_assessment", count: 4120, average_accuracy: 0.91 },
      { insight_type: "financing_analysis", count: 2180, average_accuracy: 0.76 }
    ],
    areas_for_improvement: [
      "Financing analysis predictions need improvement",
      "Confidence calibration needs adjustment",
      "Market timing predictions show lower accuracy"
    ]
  });

  const [recentFeedback, setRecentFeedback] = useState<UserFeedback[]>([
    { feedback_id: "1", feedback_type: "accuracy", rating: 5, timestamp: "2024-01-15T10:30:00Z" },
    { feedback_id: "2", feedback_type: "usefulness", rating: 4, timestamp: "2024-01-15T09:15:00Z" },
    { feedback_id: "3", feedback_type: "accuracy", rating: 3, timestamp: "2024-01-15T08:45:00Z" },
    { feedback_id: "4", feedback_type: "action_taken", rating: 5, timestamp: "2024-01-15T07:30:00Z" },
    { feedback_id: "5", feedback_type: "usefulness", rating: 4, timestamp: "2024-01-15T06:20:00Z" }
  ]);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <TrendingUp className="h-5 w-5 text-green-600" />;
      case 'declining':
        return <TrendingDown className="h-5 w-5 text-red-600" />;
      default:
        return <Minus className="h-5 w-5 text-gray-600" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'declining':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 0.9) return 'text-green-600';
    if (accuracy >= 0.8) return 'text-blue-600';
    if (accuracy >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">AI Learning & Performance Dashboard</h2>
          <p className="text-gray-600">Monitor AI accuracy, user feedback, and continuous learning metrics</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onGenerateReport}>
            Generate Report
          </Button>
          <Button onClick={onExportData}>
            Export Data
          </Button>
        </div>
      </div>

      {/* Key Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Overall Accuracy</p>
                <p className="text-2xl font-bold text-gray-900">{metrics.accuracy_rate}%</p>
              </div>
              <Target className="h-8 w-8 text-blue-600" />
            </div>
            <Progress value={metrics.accuracy_rate} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">User Satisfaction</p>
                <p className="text-2xl font-bold text-gray-900">{metrics.user_satisfaction_score}/5.0</p>
              </div>
              <Star className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="flex gap-1 mt-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star 
                  key={star} 
                  className={`h-4 w-4 ${star <= Math.round(metrics.user_satisfaction_score) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
                />
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Predictions</p>
                <p className="text-2xl font-bold text-gray-900">{formatNumber(metrics.total_predictions)}</p>
              </div>
              <Brain className="h-8 w-8 text-purple-600" />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {formatNumber(metrics.accurate_predictions)} accurate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Improvement Trend</p>
                <div className="flex items-center gap-2 mt-1">
                  {getTrendIcon(metrics.improvement_trend)}
                  <span className="text-lg font-bold capitalize">{metrics.improvement_trend}</span>
                </div>
              </div>
              <Activity className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Accuracy Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Accuracy by Insight Type
            </CardTitle>
            <CardDescription>
              Performance breakdown across different AI insight categories
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {metrics.top_insight_types.map((insight) => (
                <div key={insight.insight_type} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium capitalize">
                      {insight.insight_type.replace('_', ' ')}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className={`text-sm font-bold ${getAccuracyColor(insight.average_accuracy)}`}>
                        {(insight.average_accuracy * 100).toFixed(0)}%
                      </span>
                      <span className="text-xs text-gray-500">
                        ({formatNumber(insight.count)} predictions)
                      </span>
                    </div>
                  </div>
                  <Progress 
                    value={insight.average_accuracy * 100} 
                    className="h-2"
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Recent User Feedback
            </CardTitle>
            <CardDescription>
              Latest user ratings and feedback on AI insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentFeedback.map((feedback) => (
                <div key={feedback.feedback_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star 
                          key={star} 
                          className={`h-3 w-3 ${star <= feedback.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
                        />
                      ))}
                    </div>
                    <span className="text-sm text-gray-600 capitalize">
                      {feedback.feedback_type.replace('_', ' ')}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {formatDate(feedback.timestamp)}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Areas for Improvement */}
      <Card className="border-2 border-orange-200 bg-gradient-to-r from-orange-50 to-amber-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-orange-900">
            <AlertTriangle className="h-5 w-5" />
            Areas for Improvement
          </CardTitle>
          <CardDescription className="text-orange-700">
            AI model weaknesses identified through feedback and accuracy analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {metrics.areas_for_improvement.map((area, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-white rounded-lg border border-orange-200">
                <div className="flex items-center justify-center w-6 h-6 bg-orange-100 rounded-full text-orange-700 font-bold text-sm mt-0.5">
                  {index + 1}
                </div>
                <span className="text-gray-700 flex-grow">{area}</span>
                <Button size="sm" variant="outline" className="border-orange-300 text-orange-700 hover:bg-orange-50">
                  Investigate
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Learning Pipeline Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Continuous Learning Pipeline
          </CardTitle>
          <CardDescription>
            Status of automated learning and model improvement processes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-1">Data Collection</h4>
              <p className="text-sm text-gray-600">Active - Collecting user feedback and accuracy data</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Activity className="h-8 w-8 text-yellow-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-1">Analysis</h4>
              <p className="text-sm text-gray-600">Running - Analyzing patterns and identifying improvements</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <TrendingUp className="h-8 w-8 text-blue-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-1">Model Updates</h4>
              <p className="text-sm text-gray-600">Scheduled - Next update in 3 days</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Performance History (Last 30 Days)
          </CardTitle>
          <CardDescription>
            Accuracy and confidence trends over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-7 gap-2 text-xs text-gray-500">
              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
                <div key={day} className="text-center">{day}</div>
              ))}
            </div>
            <div className="grid grid-cols-7 gap-2">
              {Array.from({ length: 28 }, (_, i) => {
                const accuracy = 85 + Math.random() * 15; // Simulate daily accuracy
                return (
                  <div key={i} className="h-20 bg-gray-100 rounded flex items-end justify-center p-1">
                    <div 
                      className="w-full bg-blue-500 rounded-sm transition-all duration-300 hover:bg-blue-600"
                      style={{ height: `${accuracy}%` }}
                      title={`Day ${i + 1}: ${accuracy.toFixed(1)}%`}
                    />
                  </div>
                );
              })}
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Average: 92.4%</span>
              <span className="text-gray-600">Trend: ↗️ +2.1%</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LearningMetricsDashboard;
