import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  Shield, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Search,
  Filter,
  Download,
  Eye,
  Plus,
  Building,
  MapPin,
  DollarSign,
  Calendar,
  Users,
  FileCheck
} from "lucide-react";
import { AppLayout } from '@/components/layout/AppLayout';

interface ComplianceCheck {
  id: number;
  property_id: number;
  property_address: string;
  status: string;
  created_at: string;
  completed_at?: string;
  compliance_score: number;
  issues_found: number;
  critical_issues: number;
  warnings: number;
  checks_performed: string[];
  ai_analysis: string;
  recommendations: string[];
}

interface ComplianceRule {
  id: number;
  rule_name: string;
  category: string;
  description: string;
  severity: string;
  is_active: boolean;
  last_updated: string;
}

interface LegalDocument {
  id: number;
  document_name: string;
  document_type: string;
  property_address: string;
  status: string;
  uploaded_at: string;
  reviewed_at?: string;
  issues_found: number;
  ai_analysis: string;
}

const LegalCompliance: React.FC = () => {
  const [complianceChecks, setComplianceChecks] = useState<ComplianceCheck[]>([]);
  const [complianceRules, setComplianceRules] = useState<ComplianceRule[]>([]);
  const [legalDocuments, setLegalDocuments] = useState<LegalDocument[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterCategory, setFilterCategory] = useState('all');

  // Mock data
  useEffect(() => {
    setComplianceChecks([
      {
        id: 1,
        property_id: 1,
        property_address: "123 Main St, Anytown, ST 12345",
        status: "completed",
        created_at: "2024-01-15T10:30:00Z",
        completed_at: "2024-01-15T11:45:00Z",
        compliance_score: 85,
        issues_found: 3,
        critical_issues: 0,
        warnings: 3,
        checks_performed: ["zoning", "permits", "liens", "taxes", "ownership"],
        ai_analysis: "Property shows good compliance with minor issues that need attention. No critical violations found.",
        recommendations: [
          "Update property tax records",
          "Verify current zoning classification",
          "Review permit history for recent renovations"
        ]
      },
      {
        id: 2,
        property_id: 2,
        property_address: "456 Oak Ave, Anytown, ST 12345",
        status: "in_progress",
        created_at: "2024-01-15T14:20:00Z",
        compliance_score: 0,
        issues_found: 0,
        critical_issues: 0,
        warnings: 0,
        checks_performed: [],
        ai_analysis: "",
        recommendations: []
      },
      {
        id: 3,
        property_id: 3,
        property_address: "789 Pine St, Anytown, ST 12345",
        status: "completed",
        created_at: "2024-01-14T09:15:00Z",
        completed_at: "2024-01-14T10:30:00Z",
        compliance_score: 95,
        issues_found: 1,
        critical_issues: 0,
        warnings: 1,
        checks_performed: ["zoning", "permits", "liens", "taxes", "ownership"],
        ai_analysis: "Excellent compliance record with only minor documentation issues.",
        recommendations: [
          "Update contact information in property records"
        ]
      }
    ]);

    setComplianceRules([
      {
        id: 1,
        rule_name: "Zoning Compliance Check",
        category: "zoning",
        description: "Verify property is zoned for intended use",
        severity: "critical",
        is_active: true,
        last_updated: "2024-01-10T00:00:00Z"
      },
      {
        id: 2,
        rule_name: "Permit History Review",
        category: "permits",
        description: "Check for required permits and violations",
        severity: "high",
        is_active: true,
        last_updated: "2024-01-10T00:00:00Z"
      },
      {
        id: 3,
        rule_name: "Tax Lien Check",
        category: "taxes",
        description: "Verify no outstanding tax liens",
        severity: "critical",
        is_active: true,
        last_updated: "2024-01-10T00:00:00Z"
      },
      {
        id: 4,
        rule_name: "Ownership Verification",
        category: "ownership",
        description: "Confirm clear title and ownership",
        severity: "critical",
        is_active: true,
        last_updated: "2024-01-10T00:00:00Z"
      },
      {
        id: 5,
        rule_name: "Environmental Compliance",
        category: "environmental",
        description: "Check for environmental issues or restrictions",
        severity: "medium",
        is_active: true,
        last_updated: "2024-01-10T00:00:00Z"
      }
    ]);

    setLegalDocuments([
      {
        id: 1,
        document_name: "Property Deed - 123 Main St",
        document_type: "deed",
        property_address: "123 Main St, Anytown, ST 12345",
        status: "reviewed",
        uploaded_at: "2024-01-15T10:30:00Z",
        reviewed_at: "2024-01-15T11:00:00Z",
        issues_found: 0,
        ai_analysis: "Deed is valid and shows clear ownership. No issues identified."
      },
      {
        id: 2,
        document_name: "Zoning Certificate",
        document_type: "zoning",
        property_address: "123 Main St, Anytown, ST 12345",
        status: "reviewed",
        uploaded_at: "2024-01-15T10:35:00Z",
        reviewed_at: "2024-01-15T11:05:00Z",
        issues_found: 1,
        ai_analysis: "Zoning certificate shows R-2 zoning. Minor discrepancy with current use classification."
      },
      {
        id: 3,
        document_name: "Property Tax Records",
        document_type: "tax",
        property_address: "123 Main St, Anytown, ST 12345",
        status: "pending",
        uploaded_at: "2024-01-15T10:40:00Z",
        issues_found: 0,
        ai_analysis: ""
      }
    ]);
  }, []);

  const filteredComplianceChecks = complianceChecks.filter(check => {
    const matchesSearch = check.property_address.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || check.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const filteredLegalDocuments = legalDocuments.filter(doc => {
    const matchesSearch = doc.document_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.property_address.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'all' || doc.document_type === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'reviewed':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getComplianceScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <AppLayout>
      <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Legal & Compliance</h1>
          <p className="text-muted-foreground">
            Automated legal checks and compliance monitoring for real estate investments
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <FileCheck className="h-4 w-4 mr-2" />
            Run Compliance Check
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Upload Documents
          </Button>
        </div>
      </div>

      <Tabs defaultValue="compliance-checks" className="space-y-4">
        <TabsList>
          <TabsTrigger value="compliance-checks">Compliance Checks</TabsTrigger>
          <TabsTrigger value="legal-documents">Legal Documents</TabsTrigger>
          <TabsTrigger value="compliance-rules">Compliance Rules</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="compliance-checks" className="space-y-4">
          {/* Search and Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      placeholder="Search properties..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="all">All Status</option>
                  <option value="completed">Completed</option>
                  <option value="in_progress">In Progress</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </CardContent>
          </Card>

          {/* Compliance Checks List */}
          <div className="grid gap-4">
            {filteredComplianceChecks.map((check) => (
              <Card key={check.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{check.property_address}</h3>
                        <Badge className={getStatusColor(check.status)}>
                          {check.status === 'completed' && <CheckCircle className="h-3 w-3 mr-1" />}
                          {check.status === 'in_progress' && <Clock className="h-3 w-3 mr-1 animate-pulse" />}
                          {check.status === 'failed' && <AlertTriangle className="h-3 w-3 mr-1" />}
                          {check.status.replace('_', ' ')}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(check.created_at).toLocaleDateString()}
                        </span>
                      </div>

                      {check.status === 'completed' && (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                          <div className="text-center">
                            <p className={`text-2xl font-bold ${getComplianceScoreColor(check.compliance_score)}`}>
                              {check.compliance_score}%
                            </p>
                            <p className="text-sm text-gray-500">Compliance Score</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-red-600">
                              {check.critical_issues}
                            </p>
                            <p className="text-sm text-gray-500">Critical Issues</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-yellow-600">
                              {check.warnings}
                            </p>
                            <p className="text-sm text-gray-500">Warnings</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-blue-600">
                              {check.checks_performed.length}
                            </p>
                            <p className="text-sm text-gray-500">Checks Performed</p>
                          </div>
                        </div>
                      )}

                      {check.status === 'completed' && (
                        <div className="space-y-3">
                          <div className="p-4 bg-blue-50 rounded-lg">
                            <p className="text-sm text-blue-800">
                              <strong>AI Analysis:</strong> {check.ai_analysis}
                            </p>
                          </div>
                          <div className="space-y-2">
                            <p className="text-sm font-medium">Checks Performed:</p>
                            <div className="flex flex-wrap gap-1">
                              {check.checks_performed.map((checkType, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {checkType}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          {check.recommendations.length > 0 && (
                            <div className="space-y-2">
                              <p className="text-sm font-medium">Recommendations:</p>
                              <ul className="list-disc list-inside space-y-1">
                                {check.recommendations.map((rec, index) => (
                                  <li key={index} className="text-sm text-gray-600">{rec}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          <div className="flex justify-end space-x-2">
                            <Button variant="outline" size="sm">
                              <Eye className="h-4 w-4 mr-1" />
                              View Details
                            </Button>
                            <Button variant="outline" size="sm">
                              <Download className="h-4 w-4 mr-1" />
                              Export Report
                            </Button>
                          </div>
                        </div>
                      )}

                      {check.status === 'in_progress' && (
                        <div className="flex items-center space-x-4">
                          <Progress value={65} className="flex-1" />
                          <span className="text-sm text-gray-500">Running compliance checks...</span>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="legal-documents" className="space-y-4">
          {/* Search and Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      placeholder="Search documents..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="all">All Types</option>
                  <option value="deed">Deed</option>
                  <option value="zoning">Zoning</option>
                  <option value="tax">Tax</option>
                  <option value="permit">Permit</option>
                </select>
              </div>
            </CardContent>
          </Card>

          {/* Legal Documents List */}
          <div className="grid gap-4">
            {filteredLegalDocuments.map((doc) => (
              <Card key={doc.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{doc.document_name}</h3>
                        <Badge className={getStatusColor(doc.status)}>
                          {doc.status === 'reviewed' && <CheckCircle className="h-3 w-3 mr-1" />}
                          {doc.status === 'pending' && <Clock className="h-3 w-3 mr-1" />}
                          {doc.status}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(doc.uploaded_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-4">{doc.property_address}</p>
                      
                      {doc.status === 'reviewed' && doc.ai_analysis && (
                        <div className="p-4 bg-blue-50 rounded-lg mb-4">
                          <p className="text-sm text-blue-800">
                            <strong>AI Analysis:</strong> {doc.ai_analysis}
                          </p>
                        </div>
                      )}

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Badge variant="outline">
                            {doc.document_type}
                          </Badge>
                          {doc.issues_found > 0 && (
                            <Badge variant="destructive">
                              {doc.issues_found} issues found
                            </Badge>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                          <Button variant="outline" size="sm">
                            <Download className="h-4 w-4 mr-1" />
                            Download
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

        <TabsContent value="compliance-rules" className="space-y-4">
          <div className="grid gap-4">
            {complianceRules.map((rule) => (
              <Card key={rule.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-2">
                        <h3 className="text-lg font-medium">{rule.rule_name}</h3>
                        <Badge className={getSeverityColor(rule.severity)}>
                          {rule.severity}
                        </Badge>
                        <Badge variant={rule.is_active ? "default" : "secondary"}>
                          {rule.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-4">{rule.description}</p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Badge variant="outline">
                            {rule.category}
                          </Badge>
                          <span className="text-sm text-gray-500">
                            Updated: {new Date(rule.last_updated).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View Details
                          </Button>
                          <Button variant="outline" size="sm">
                            <FileText className="h-4 w-4 mr-1" />
                            Edit Rule
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

        <TabsContent value="reports" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Checks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{complianceChecks.length}</div>
                <p className="text-xs text-muted-foreground">+2 this week</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Completed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {complianceChecks.filter(c => c.status === 'completed').length}
                </div>
                <p className="text-xs text-muted-foreground">95% success rate</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Avg Compliance Score</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {complianceChecks.filter(c => c.status === 'completed').length > 0 
                    ? Math.round(complianceChecks.filter(c => c.status === 'completed').reduce((sum, c) => sum + c.compliance_score, 0) / complianceChecks.filter(c => c.status === 'completed').length)
                    : 0}%
                </div>
                <p className="text-xs text-muted-foreground">Above 80% threshold</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Critical Issues</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {complianceChecks.reduce((sum, c) => sum + c.critical_issues, 0)}
                </div>
                <p className="text-xs text-muted-foreground">Require immediate attention</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
      </div>
    </AppLayout>
  );
};

export default LegalCompliance;
