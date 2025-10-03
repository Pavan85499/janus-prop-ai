import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  Users, 
  MessageSquare, 
  FileText, 
  TrendingUp, 
  TrendingDown,
  CheckCircle,
  XCircle,
  Clock,
  Play,
  Pause,
  RefreshCw,
  Download,
  Eye,
  Plus,
  Brain,
  Target,
  AlertTriangle,
  ThumbsUp,
  ThumbsDown
} from "lucide-react";
import { AppLayout } from '@/components/layout/AppLayout';

interface CommitteeDebate {
  id: number;
  property_id: number;
  property_address: string;
  status: string;
  created_at: string;
  completed_at?: string;
  participants: CommitteeMember[];
  debate_summary: string;
  final_decision: string;
  confidence_score: number;
  key_points: string[];
  risks_identified: string[];
  opportunities_identified: string[];
}

interface CommitteeMember {
  id: number;
  name: string;
  role: string;
  expertise: string[];
  position: string;
  reasoning: string;
  confidence: number;
  vote: string;
}

interface FinancialAnalysis {
  purchase_price: number;
  renovation_cost: number;
  total_investment: number;
  projected_rent: number;
  projected_expenses: number;
  projected_cash_flow: number;
  cap_rate: number;
  cash_on_cash_return: number;
  irr: number;
}

interface RiskAssessment {
  market_risk: string;
  interest_rate_risk: string;
  renovation_risk: string;
  operational_risk: string;
  overall_risk_score: number;
}

interface MarketAnalysis {
  market_trend: string;
  demand_supply: string;
  price_appreciation: string;
  rental_growth: string;
}

interface KeyMetrics {
  ltv: number;
  dscr: number;
  occupancy_rate: number;
  rent_rollover_rate: number;
}

interface InvestmentMemo {
  id: number;
  property_id: number;
  property_address: string;
  created_at: string;
  executive_summary: string;
  investment_thesis: string;
  financial_analysis: FinancialAnalysis;
  risk_assessment: RiskAssessment;
  market_analysis: MarketAnalysis;
  recommendation: string;
  confidence_level: number;
  key_metrics: KeyMetrics;
}

const AIInvestmentCommittee: React.FC = () => {
  const [debates, setDebates] = useState<CommitteeDebate[]>([]);
  const [memos, setMemos] = useState<InvestmentMemo[]>([]);
  const [selectedDebate, setSelectedDebate] = useState<CommitteeDebate | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  // Mock data
  useEffect(() => {
    setDebates([
      {
        id: 1,
        property_id: 1,
        property_address: "123 Main St, Anytown, ST 12345",
        status: "completed",
        created_at: "2024-01-15T10:30:00Z",
        completed_at: "2024-01-15T11:45:00Z",
        participants: [
          {
            id: 1,
            name: "Sarah Chen",
            role: "Chief Investment Officer",
            expertise: ["market_analysis", "portfolio_management"],
            position: "BUY",
            reasoning: "Strong cash flow potential with excellent location and growth prospects. Market fundamentals support long-term appreciation.",
            confidence: 85,
            vote: "approve"
          },
          {
            id: 2,
            name: "Michael Rodriguez",
            role: "Risk Management Director",
            expertise: ["risk_assessment", "due_diligence"],
            position: "HOLD",
            reasoning: "Solid investment but concerned about market volatility and potential interest rate increases. Recommend waiting for better entry point.",
            confidence: 70,
            vote: "neutral"
          },
          {
            id: 3,
            name: "Dr. Emily Watson",
            role: "Market Research Analyst",
            expertise: ["market_research", "economic_analysis"],
            position: "BUY",
            reasoning: "Market data shows strong demand fundamentals. Demographic trends support continued growth in this area.",
            confidence: 90,
            vote: "approve"
          },
          {
            id: 4,
            name: "James Thompson",
            role: "Operations Manager",
            expertise: ["property_management", "operations"],
            position: "SELL",
            reasoning: "Property requires significant renovation investment. Maintenance costs may exceed projections based on age and condition.",
            confidence: 75,
            vote: "reject"
          }
        ],
        debate_summary: "The committee engaged in a comprehensive debate about the investment opportunity. While there was strong support for the property's location and market potential, concerns were raised about renovation costs and market timing. The final decision was to proceed with caution.",
        final_decision: "APPROVE WITH CONDITIONS",
        confidence_score: 78,
        key_points: [
          "Excellent location with strong market fundamentals",
          "High renovation costs may impact returns",
          "Market timing concerns due to interest rate environment",
          "Strong rental demand supports cash flow projections"
        ],
        risks_identified: [
          "Renovation cost overruns",
          "Interest rate sensitivity",
          "Market timing risk",
          "Property condition unknowns"
        ],
        opportunities_identified: [
          "Strong rental demand",
          "Location appreciation potential",
          "Value-add renovation opportunity",
          "Market recovery potential"
        ]
      },
      {
        id: 2,
        property_id: 2,
        property_address: "456 Oak Ave, Anytown, ST 12345",
        status: "in_progress",
        created_at: "2024-01-15T14:20:00Z",
        participants: [
          {
            id: 1,
            name: "Sarah Chen",
            role: "Chief Investment Officer",
            expertise: ["market_analysis", "portfolio_management"],
            position: "PENDING",
            reasoning: "",
            confidence: 0,
            vote: "pending"
          },
          {
            id: 2,
            name: "Michael Rodriguez",
            role: "Risk Management Director",
            expertise: ["risk_assessment", "due_diligence"],
            position: "PENDING",
            reasoning: "",
            confidence: 0,
            vote: "pending"
          },
          {
            id: 3,
            name: "Dr. Emily Watson",
            role: "Market Research Analyst",
            expertise: ["market_research", "economic_analysis"],
            position: "PENDING",
            reasoning: "",
            confidence: 0,
            vote: "pending"
          },
          {
            id: 4,
            name: "James Thompson",
            role: "Operations Manager",
            expertise: ["property_management", "operations"],
            position: "PENDING",
            reasoning: "",
            confidence: 0,
            vote: "pending"
          }
        ],
        debate_summary: "",
        final_decision: "",
        confidence_score: 0,
        key_points: [],
        risks_identified: [],
        opportunities_identified: []
      }
    ]);

    setMemos([
      {
        id: 1,
        property_id: 1,
        property_address: "123 Main St, Anytown, ST 12345",
        created_at: "2024-01-15T12:00:00Z",
        executive_summary: "This property presents a compelling investment opportunity with strong fundamentals and value-add potential. The committee recommends proceeding with the acquisition, subject to satisfactory due diligence completion.",
        investment_thesis: "The property benefits from an excellent location in a growing market with strong rental demand. The value-add renovation opportunity provides upside potential while the current cash flow supports the investment thesis.",
        financial_analysis: {
          purchase_price: 450000,
          renovation_cost: 75000,
          total_investment: 525000,
          projected_rent: 3200,
          projected_expenses: 1800,
          projected_cash_flow: 1400,
          cap_rate: 8.1,
          cash_on_cash_return: 12.5,
          irr: 15.2
        },
        risk_assessment: {
          market_risk: "Medium",
          interest_rate_risk: "High",
          renovation_risk: "Medium",
          operational_risk: "Low",
          overall_risk_score: 65
        },
        market_analysis: {
          market_trend: "Growing",
          demand_supply: "Favorable",
          price_appreciation: "4.2% annually",
          rental_growth: "3.8% annually"
        },
        recommendation: "BUY",
        confidence_level: 78,
        key_metrics: {
          ltv: 80,
          dscr: 1.8,
          occupancy_rate: 95,
          rent_rollover_rate: 15
        }
      }
    ]);
  }, []);

  const handleStartDebate = async (propertyId: number) => {
    setIsRunning(true);
    
    // Simulate debate running
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Update debate status
    setDebates(prev => prev.map(debate => 
      debate.property_id === propertyId 
        ? { ...debate, status: "completed" }
        : debate
    ));
    
    setIsRunning(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getVoteIcon = (vote: string) => {
    switch (vote) {
      case 'approve':
        return <ThumbsUp className="h-4 w-4 text-green-500" />;
      case 'reject':
        return <ThumbsDown className="h-4 w-4 text-red-500" />;
      case 'neutral':
        return <Target className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getVoteColor = (vote: string) => {
    switch (vote) {
      case 'approve':
        return 'bg-green-100 text-green-800';
      case 'reject':
        return 'bg-red-100 text-red-800';
      case 'neutral':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDecisionColor = (decision: string) => {
    switch (decision.toLowerCase()) {
      case 'approve':
        return 'text-green-600';
      case 'approve with conditions':
        return 'text-yellow-600';
      case 'reject':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Investment Committee</h1>
          <p className="text-muted-foreground">
            Simulate investment committee debates and generate comprehensive investment memos
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Committee Debate
        </Button>
      </div>

      <Tabs defaultValue="debates" className="space-y-4">
        <TabsList>
          <TabsTrigger value="debates">Committee Debates</TabsTrigger>
          <TabsTrigger value="memos">Investment Memos</TabsTrigger>
          <TabsTrigger value="members">Committee Members</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="debates" className="space-y-4">
          <div className="grid gap-4">
            {debates.map((debate) => (
              <Card key={debate.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{debate.property_address}</h3>
                        <Badge className={getStatusColor(debate.status)}>
                          {debate.status === 'completed' && <CheckCircle className="h-3 w-3 mr-1" />}
                          {debate.status === 'in_progress' && <RefreshCw className="h-3 w-3 mr-1 animate-spin" />}
                          {debate.status === 'failed' && <XCircle className="h-3 w-3 mr-1" />}
                          {debate.status.replace('_', ' ')}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(debate.created_at).toLocaleDateString()}
                        </span>
                      </div>

                      {debate.status === 'completed' && (
                        <div className="space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                            <div className="text-center">
                              <p className="text-2xl font-bold text-blue-600">
                                {debate.confidence_score}%
                              </p>
                              <p className="text-sm text-gray-500">Confidence Score</p>
                            </div>
                            <div className="text-center">
                              <p className={`text-2xl font-bold ${getDecisionColor(debate.final_decision)}`}>
                                {debate.final_decision}
                              </p>
                              <p className="text-sm text-gray-500">Final Decision</p>
                            </div>
                            <div className="text-center">
                              <p className="text-2xl font-bold text-purple-600">
                                {debate.participants.length}
                              </p>
                              <p className="text-sm text-gray-500">Committee Members</p>
                            </div>
                          </div>

                          <div className="p-4 bg-blue-50 rounded-lg">
                            <p className="text-sm text-blue-800">
                              <strong>Debate Summary:</strong> {debate.debate_summary}
                            </p>
                          </div>

                          <div className="space-y-4">
                            <div>
                              <h4 className="font-medium mb-2">Committee Members & Votes</h4>
                              <div className="grid gap-3">
                                {debate.participants.map((member) => (
                                  <div key={member.id} className="flex items-start space-x-3 p-3 border rounded-lg">
                                    <div className="flex-shrink-0">
                                      <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                                        <Users className="h-5 w-5 text-gray-500" />
                                      </div>
                                    </div>
                                    <div className="flex-1 min-w-0">
                                      <div className="flex items-center space-x-2 mb-1">
                                        <h5 className="font-medium">{member.name}</h5>
                                        <Badge className={getVoteColor(member.vote)}>
                                          {getVoteIcon(member.vote)}
                                          <span className="ml-1">{member.position}</span>
                                        </Badge>
                                        <span className="text-sm text-gray-500">
                                          {member.confidence}% confidence
                                        </span>
                                      </div>
                                      <p className="text-sm text-gray-600">{member.role}</p>
                                      <p className="text-sm text-gray-500 mt-1">{member.reasoning}</p>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>

                            <div className="grid md:grid-cols-2 gap-4">
                              <div>
                                <h4 className="font-medium mb-2">Key Points</h4>
                                <ul className="list-disc list-inside space-y-1">
                                  {debate.key_points.map((point, index) => (
                                    <li key={index} className="text-sm text-gray-600">{point}</li>
                                  ))}
                                </ul>
                              </div>
                              <div>
                                <h4 className="font-medium mb-2">Risks Identified</h4>
                                <ul className="list-disc list-inside space-y-1">
                                  {debate.risks_identified.map((risk, index) => (
                                    <li key={index} className="text-sm text-red-600">{risk}</li>
                                  ))}
                                </ul>
                              </div>
                            </div>

                            <div className="flex justify-end space-x-2">
                              <Button variant="outline" size="sm">
                                <Eye className="h-4 w-4 mr-1" />
                                View Full Debate
                              </Button>
                              <Button variant="outline" size="sm">
                                <Download className="h-4 w-4 mr-1" />
                                Export Report
                              </Button>
                            </div>
                          </div>
                        </div>
                      )}

                      {debate.status === 'in_progress' && (
                        <div className="flex items-center space-x-4">
                          <Progress value={65} className="flex-1" />
                          <span className="text-sm text-gray-500">Committee debating...</span>
                        </div>
                      )}

                      {debate.status === 'pending' && (
                        <div className="flex justify-end">
                          <Button 
                            onClick={() => handleStartDebate(debate.property_id)}
                            disabled={isRunning}
                          >
                            {isRunning ? (
                              <>
                                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                                Starting Debate...
                              </>
                            ) : (
                              <>
                                <Play className="h-4 w-4 mr-2" />
                                Start Committee Debate
                              </>
                            )}
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="memos" className="space-y-4">
          <div className="grid gap-4">
            {memos.map((memo) => (
              <Card key={memo.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{memo.property_address}</h3>
                        <Badge className={getVoteColor(memo.recommendation.toLowerCase())}>
                          {memo.recommendation}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(memo.created_at).toLocaleDateString()}
                        </span>
                      </div>

                      <div className="space-y-4">
                        <div className="p-4 bg-blue-50 rounded-lg">
                          <p className="text-sm text-blue-800">
                            <strong>Executive Summary:</strong> {memo.executive_summary}
                          </p>
                        </div>

                        <div className="grid md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="font-medium mb-2">Financial Analysis</h4>
                            <div className="space-y-1 text-sm">
                              <div className="flex justify-between">
                                <span>Purchase Price:</span>
                                <span className="font-medium">${memo.financial_analysis.purchase_price.toLocaleString()}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Projected Cash Flow:</span>
                                <span className="font-medium">${memo.financial_analysis.projected_cash_flow.toLocaleString()}/month</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Cap Rate:</span>
                                <span className="font-medium">{memo.financial_analysis.cap_rate}%</span>
                              </div>
                              <div className="flex justify-between">
                                <span>IRR:</span>
                                <span className="font-medium">{memo.financial_analysis.irr}%</span>
                              </div>
                            </div>
                          </div>
                          <div>
                            <h4 className="font-medium mb-2">Risk Assessment</h4>
                            <div className="space-y-1 text-sm">
                              <div className="flex justify-between">
                                <span>Market Risk:</span>
                                <span className="font-medium">{memo.risk_assessment.market_risk}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Interest Rate Risk:</span>
                                <span className="font-medium">{memo.risk_assessment.interest_rate_risk}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Overall Risk Score:</span>
                                <span className="font-medium">{memo.risk_assessment.overall_risk_score}/100</span>
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="flex justify-end space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View Full Memo
                          </Button>
                          <Button variant="outline" size="sm">
                            <Download className="h-4 w-4 mr-1" />
                            Download PDF
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="members" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                id: 1,
                name: "Sarah Chen",
                role: "Chief Investment Officer",
                expertise: ["Market Analysis", "Portfolio Management", "Strategic Planning"],
                experience: "15 years",
                avatar: "SC"
              },
              {
                id: 2,
                name: "Michael Rodriguez",
                role: "Risk Management Director",
                expertise: ["Risk Assessment", "Due Diligence", "Compliance"],
                experience: "12 years",
                avatar: "MR"
              },
              {
                id: 3,
                name: "Dr. Emily Watson",
                role: "Market Research Analyst",
                expertise: ["Market Research", "Economic Analysis", "Data Science"],
                experience: "10 years",
                avatar: "EW"
              },
              {
                id: 4,
                name: "James Thompson",
                role: "Operations Manager",
                expertise: ["Property Management", "Operations", "Maintenance"],
                experience: "18 years",
                avatar: "JT"
              }
            ].map((member) => (
              <Card key={member.id}>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-lg font-bold text-blue-600">{member.avatar}</span>
                    </div>
                    <h3 className="text-lg font-medium">{member.name}</h3>
                    <p className="text-sm text-gray-600 mb-2">{member.role}</p>
                    <p className="text-xs text-gray-500 mb-4">{member.experience} experience</p>
                    <div className="space-y-1">
                      {member.expertise.map((skill, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Debates</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{debates.length}</div>
                <p className="text-xs text-muted-foreground">+3 this month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Approved</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {debates.filter(d => d.final_decision.toLowerCase().includes('approve')).length}
                </div>
                <p className="text-xs text-muted-foreground">75% approval rate</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Avg Confidence</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {debates.filter(d => d.status === 'completed').length > 0 
                    ? Math.round(debates.filter(d => d.status === 'completed').reduce((sum, d) => sum + d.confidence_score, 0) / debates.filter(d => d.status === 'completed').length)
                    : 0}%
                </div>
                <p className="text-xs text-muted-foreground">Committee confidence</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Investment Memos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{memos.length}</div>
                <p className="text-xs text-muted-foreground">Generated this month</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
      </div>
    </AppLayout>
  );
};

export default AIInvestmentCommittee;
