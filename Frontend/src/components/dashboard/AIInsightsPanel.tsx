import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { 
  Lightbulb, 
  TrendingUp, 
  AlertTriangle, 
  DollarSign, 
  Target,
  CheckCircle,
  ArrowRight,
  Star
} from 'lucide-react';

interface PropertyInsight {
  insight_id: string;
  insight_type: string;
  confidence_score: number;
  explanation: string;
  actionable_steps: string[];
  data_sources: string[];
}

interface PropertyAnalysis {
  property_id: string;
  insights: PropertyInsight[];
  overall_score: number;
  summary: string;
  next_steps: string[];
}

interface AIInsightsPanelProps {
  analysis: PropertyAnalysis;
  onActionClick: (action: string, insightId: string) => void;
}

const AIInsightsPanel: React.FC<AIInsightsPanelProps> = ({ analysis, onActionClick }) => {
  const [expandedInsights, setExpandedInsights] = useState<Set<string>>(new Set());

  const toggleInsight = (insightId: string) => {
    const newExpanded = new Set(expandedInsights);
    if (newExpanded.has(insightId)) {
      newExpanded.delete(insightId);
    } else {
      newExpanded.add(insightId);
    }
    setExpandedInsights(newExpanded);
  };

  const getInsightIcon = (insightType: string) => {
    switch (insightType) {
      case 'market_opportunity':
        return <TrendingUp className="h-5 w-5 text-green-600" />;
      case 'risk_assessment':
        return <AlertTriangle className="h-5 w-5 text-orange-600" />;
      case 'investment_potential':
        return <DollarSign className="h-5 w-5 text-blue-600" />;
      case 'financing_analysis':
        return <Target className="h-5 w-5 text-purple-600" />;
      default:
        return <Lightbulb className="h-5 w-5 text-gray-600" />;
    }
  };

  const getInsightColor = (insightType: string) => {
    switch (insightType) {
      case 'market_opportunity':
        return 'bg-green-50 border-green-200';
      case 'risk_assessment':
        return 'bg-orange-50 border-orange-200';
      case 'investment_potential':
        return 'bg-blue-50 border-blue-200';
      case 'financing_analysis':
        return 'bg-purple-50 border-purple-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div className="space-y-6">
      {/* Overall Analysis Summary */}
      <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-900">
            <Lightbulb className="h-6 w-6" />
            AI Property Analysis Summary
          </CardTitle>
          <CardDescription className="text-blue-700">
            {analysis.summary}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-600">Overall Score:</span>
                <Badge variant="secondary" className="text-lg font-bold">
                  {(analysis.overall_score * 100).toFixed(0)}%
                </Badge>
              </div>
              <Progress value={analysis.overall_score * 100} className="w-48" />
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-900">
                {analysis.insights.length}
              </div>
              <div className="text-sm text-blue-700">AI Insights</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Individual Insights */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Detailed AI Insights</h3>
        {analysis.insights.map((insight) => (
          <Card 
            key={insight.insight_id} 
            className={`border-2 ${getInsightColor(insight.insight_type)} hover:shadow-md transition-shadow`}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  {getInsightIcon(insight.insight_type)}
                  <div>
                    <CardTitle className="text-lg capitalize">
                      {insight.insight_type.replace('_', ' ')}
                    </CardTitle>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge 
                        variant="outline" 
                        className={getConfidenceColor(insight.confidence_score)}
                      >
                        {getConfidenceLabel(insight.confidence_score)} Confidence
                      </Badge>
                      <span className="text-sm text-gray-600">
                        {(insight.confidence_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleInsight(insight.insight_id)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  {expandedInsights.has(insight.insight_id) ? 'Collapse' : 'Expand'}
                </Button>
              </div>
            </CardHeader>

            <CardContent className="pt-0">
              {/* Explanation */}
              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-2">Why This Insight Exists:</h4>
                <p className="text-gray-700 leading-relaxed">{insight.explanation}</p>
              </div>

              {/* Data Sources */}
              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-2">Data Sources:</h4>
                <div className="flex flex-wrap gap-2">
                  {insight.data_sources.map((source, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {source}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Actionable Steps */}
              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-3">Recommended Actions:</h4>
                <div className="space-y-2">
                  {insight.actionable_steps.map((step, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 bg-white rounded-lg border">
                      <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span className="text-gray-700 flex-grow">{step}</span>
                      <Button
                        size="sm"
                        onClick={() => onActionClick(step, insight.insight_id)}
                        className="flex items-center gap-1"
                      >
                        Take Action
                        <ArrowRight className="h-3 w-3" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Expanded Content */}
              {expandedInsights.has(insight.insight_id) && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Confidence Breakdown</h5>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Data Quality</span>
                          <span className="font-medium">85%</span>
                        </div>
                        <Progress value={85} className="h-2" />
                        <div className="flex justify-between text-sm">
                          <span>Model Accuracy</span>
                          <span className="font-medium">78%</span>
                        </div>
                        <Progress value={78} className="h-2" />
                        <div className="flex justify-between text-sm">
                          <span>Market Conditions</span>
                          <span className="font-medium">92%</span>
                        </div>
                        <Progress value={92} className="h-2" />
                      </div>
                    </div>
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Similar Properties</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Recent Sales</span>
                          <span className="text-gray-600">12 properties</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Avg. Price</span>
                          <span className="text-gray-600">$725,000</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Market Trend</span>
                          <span className="text-green-600">↗️ +5.2%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Next Steps Panel */}
      <Card className="border-2 border-green-200 bg-gradient-to-r from-green-50 to-emerald-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-900">
            <Target className="h-6 w-6" />
            Prioritized Next Steps
          </CardTitle>
          <CardDescription className="text-green-700">
            AI-recommended actions to maximize your investment potential
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {analysis.next_steps.map((step, index) => (
              <div key={index} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-green-200">
                <div className="flex items-center justify-center w-8 h-8 bg-green-100 rounded-full text-green-700 font-bold text-sm">
                  {index + 1}
                </div>
                <span className="text-gray-700 flex-grow">{step}</span>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onActionClick(step, 'next_steps')}
                  className="border-green-300 text-green-700 hover:bg-green-50"
                >
                  Start
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Feedback Section */}
      <Card className="border-2 border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-purple-900">
            <Star className="h-6 w-6" />
            Help Improve Our AI
          </CardTitle>
          <CardDescription className="text-purple-700">
            Rate the accuracy and usefulness of these insights
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700">Accuracy:</span>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((rating) => (
                  <Button
                    key={rating}
                    variant="ghost"
                    size="sm"
                    className="p-1 h-8 w-8 hover:bg-purple-100"
                  >
                    <Star className={`h-4 w-4 ${rating <= 4 ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} />
                  </Button>
                ))}
              </div>
            </div>
            <Button variant="outline" className="border-purple-300 text-purple-700 hover:bg-purple-50">
              Submit Feedback
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIInsightsPanel;
