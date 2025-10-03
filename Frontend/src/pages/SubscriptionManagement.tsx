import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  AnimaticCard, 
  AnimaticCardGrid, 
  AnimaticButton, 
  AnimaticHeading, 
  AnimaticText,
  useAnimatic,
  useResponsiveAnimatic
} from "@/components/animatic";
import { 
  CreditCard, 
  FileText, 
  DollarSign, 
  Calendar, 
  CheckCircle,
  Clock,
  AlertTriangle,
  Download,
  Eye,
  Plus,
  Settings,
  Users,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Star,
  Crown,
  Zap,
  Shield
} from "lucide-react";
import { AppLayout } from '@/components/layout/AppLayout';

interface Subscription {
  id: number;
  tier: string;
  status: string;
  billing_cycle: string;
  monthly_price: number;
  annual_price: number;
  max_properties: number;
  max_scans_per_month: number;
  max_documents: number;
  max_users: number;
  features: string[];
  trial_start_date?: string;
  trial_end_date?: string;
  billing_start_date: string;
  next_billing_date?: string;
  auto_renew: boolean;
  created_at: string;
}

interface Invoice {
  id: number;
  subscription_id: number;
  invoice_number: string;
  invoice_date: string;
  due_date: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  status: string;
  paid_at?: string;
  created_at: string;
}

interface UsageTracking {
  subscription_id: number;
  period_start: string;
  period_end: string;
  properties_created: number;
  scans_performed: number;
  documents_uploaded: number;
  api_calls: number;
  storage_used_mb: number;
  overage_charges: number;
  created_at: string;
}

interface SubscriptionPlan {
  id: number;
  plan_name: string;
  tier: string;
  description: string;
  monthly_price: number;
  annual_price: number;
  max_properties: number;
  max_scans_per_month: number;
  max_documents: number;
  max_users: number;
  included_features: string[];
  is_active: boolean;
  is_popular: boolean;
}

const SubscriptionManagement: React.FC = () => {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [usageTracking, setUsageTracking] = useState<UsageTracking[]>([]);
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(null);
  const { isMobile, isTablet, isDesktop } = useResponsiveAnimatic();

  // Mock data
  useEffect(() => {
    setSubscriptions([
      {
        id: 1,
        tier: "pro",
        status: "active",
        billing_cycle: "monthly",
        monthly_price: 99,
        annual_price: 999,
        max_properties: 50,
        max_scans_per_month: 200,
        max_documents: 1000,
        max_users: 5,
        features: ["property_scanner", "document_management", "underwriting", "legal_compliance", "ai_insights"],
        billing_start_date: "2024-01-01T00:00:00Z",
        next_billing_date: "2024-02-01T00:00:00Z",
        auto_renew: true,
        created_at: "2024-01-01T00:00:00Z"
      }
    ]);

    setInvoices([
      {
        id: 1,
        subscription_id: 1,
        invoice_number: "INV-20240101-001",
        invoice_date: "2024-01-01T00:00:00Z",
        due_date: "2024-01-08T00:00:00Z",
        subtotal: 99,
        tax_amount: 7.92,
        discount_amount: 0,
        total_amount: 106.92,
        status: "paid",
        paid_at: "2024-01-02T10:30:00Z",
        created_at: "2024-01-01T00:00:00Z"
      },
      {
        id: 2,
        subscription_id: 1,
        invoice_number: "INV-20240201-002",
        invoice_date: "2024-02-01T00:00:00Z",
        due_date: "2024-02-08T00:00:00Z",
        subtotal: 99,
        tax_amount: 7.92,
        discount_amount: 0,
        total_amount: 106.92,
        status: "pending",
        created_at: "2024-02-01T00:00:00Z"
      }
    ]);

    setUsageTracking([
      {
        subscription_id: 1,
        period_start: "2024-01-01T00:00:00Z",
        period_end: "2024-01-31T23:59:59Z",
        properties_created: 12,
        scans_performed: 45,
        documents_uploaded: 78,
        api_calls: 1250,
        storage_used_mb: 2048,
        overage_charges: 0,
        created_at: "2024-01-31T23:59:59Z"
      }
    ]);

    setPlans([
      {
        id: 1,
        plan_name: "Lite",
        tier: "lite",
        description: "Perfect for individual investors getting started",
        monthly_price: 29,
        annual_price: 299,
        max_properties: 10,
        max_scans_per_month: 50,
        max_documents: 100,
        max_users: 1,
        included_features: ["property_scanner", "basic_analytics"],
        is_active: true,
        is_popular: false
      },
      {
        id: 2,
        plan_name: "Pro",
        tier: "pro",
        description: "Ideal for active real estate professionals",
        monthly_price: 99,
        annual_price: 999,
        max_properties: 50,
        max_scans_per_month: 200,
        max_documents: 1000,
        max_users: 5,
        included_features: ["property_scanner", "document_management", "underwriting", "legal_compliance", "ai_insights"],
        is_active: true,
        is_popular: true
      },
      {
        id: 3,
        plan_name: "Enterprise",
        tier: "enterprise",
        description: "For large teams and organizations",
        monthly_price: 299,
        annual_price: 2999,
        max_properties: 0,
        max_scans_per_month: 0,
        max_documents: 0,
        max_users: 0,
        included_features: ["property_scanner", "document_management", "underwriting", "legal_compliance", "ai_insights", "custom_integrations", "priority_support"],
        is_active: true,
        is_popular: false
      }
    ]);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'trial':
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'expired':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4" />;
      case 'trial':
        return <Clock className="h-4 w-4" />;
      case 'cancelled':
        return <AlertTriangle className="h-4 w-4" />;
      case 'expired':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'lite':
        return <Zap className="h-5 w-5 text-blue-500" />;
      case 'pro':
        return <Crown className="h-5 w-5 text-purple-500" />;
      case 'enterprise':
        return <Shield className="h-5 w-5 text-green-500" />;
      default:
        return <Star className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <AppLayout>
      <div className="min-h-screen bg-background p-4 sm:p-6 lg:p-8">
      <div className="animatic-container space-y-6 sm:space-y-8">
        {/* Header Section */}
        <div className="responsive-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 sm:gap-6">
            <div className="space-y-2">
              <AnimaticHeading 
                level={1} 
                className="text-2xl sm:text-3xl lg:text-4xl font-bold"
                animation="fade"
              >
                Subscription Management
              </AnimaticHeading>
              <AnimaticText 
                className="text-sm sm:text-base text-muted-foreground"
                animation="slide"
                delay={100}
              >
                Manage your subscription, billing, and usage across all features
              </AnimaticText>
            </div>
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
              <AnimaticButton
                variant="animatic"
                size={isMobile ? "sm" : "default"}
                className="w-full sm:w-auto"
                animation="bounce"
                delay={200}
              >
                <Plus className="h-4 w-4 mr-2" />
                Upgrade Plan
              </AnimaticButton>
            </div>
          </div>
        </div>

        {/* Responsive Tabs */}
        <Tabs defaultValue="overview" className="space-y-4 sm:space-y-6">
          <TabsList className="grid w-full grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 
                              bg-card/50 border border-border/50 rounded-lg p-1
                              responsive-fade-in">
            <TabsTrigger 
              value="overview" 
              className="text-xs sm:text-sm data-[state=active]:bg-primary 
                       data-[state=active]:text-primary-foreground
                       transition-all duration-300 hover:scale-105 focus-ring"
            >
              <span className="hidden sm:inline">Overview</span>
              <span className="sm:hidden">Overview</span>
            </TabsTrigger>
            <TabsTrigger 
              value="plans"
              className="text-xs sm:text-sm data-[state=active]:bg-primary 
                       data-[state=active]:text-primary-foreground
                       transition-all duration-300 hover:scale-105 focus-ring"
            >
              <span className="hidden sm:inline">Plans & Pricing</span>
              <span className="sm:hidden">Plans</span>
            </TabsTrigger>
            <TabsTrigger 
              value="billing"
              className="text-xs sm:text-sm data-[state=active]:bg-primary 
                       data-[state=active]:text-primary-foreground
                       transition-all duration-300 hover:scale-105 focus-ring"
            >
              <span className="hidden sm:inline">Billing & Invoices</span>
              <span className="sm:hidden">Billing</span>
            </TabsTrigger>
            <TabsTrigger 
              value="usage"
              className="text-xs sm:text-sm data-[state=active]:bg-primary 
                       data-[state=active]:text-primary-foreground
                       transition-all duration-300 hover:scale-105 focus-ring"
            >
              <span className="hidden sm:inline">Usage & Limits</span>
              <span className="sm:hidden">Usage</span>
            </TabsTrigger>
            <TabsTrigger 
              value="settings"
              className="text-xs sm:text-sm data-[state=active]:bg-primary 
                       data-[state=active]:text-primary-foreground
                       transition-all duration-300 hover:scale-105 focus-ring"
            >
              <span className="hidden sm:inline">Settings</span>
              <span className="sm:hidden">Settings</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4 sm:space-y-6 animate-fade-in-up">
            {/* Current Subscription */}
            {subscriptions.map((subscription, index) => (
              <AnimaticCard 
                key={subscription.id}
                variant="elevated"
                animation="fade"
                delay={index * 100}
                className="hover:shadow-xl hover:shadow-primary/10"
              >
                <CardHeader className="p-4 sm:p-6">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div className="flex items-center space-x-3 sm:space-x-4">
                      <div className="p-2 rounded-lg bg-primary/10">
                        {getTierIcon(subscription.tier)}
                      </div>
                      <div>
                        <CardTitle className="text-lg sm:text-xl animatic-heading">
                          {subscription.tier.toUpperCase()} Plan
                        </CardTitle>
                        <CardDescription className="text-sm sm:text-base">
                          {subscription.billing_cycle === 'monthly' ? 'Monthly' : 'Annual'} billing
                        </CardDescription>
                      </div>
                    </div>
                    <Badge className={`${getStatusColor(subscription.status)} px-3 py-1 text-xs sm:text-sm`}>
                      {getStatusIcon(subscription.status)}
                      <span className="ml-1">{subscription.status}</span>
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="p-4 sm:p-6">
                  {/* Responsive Metrics Grid */}
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
                    <div className="text-center p-3 sm:p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <p className="text-xl sm:text-2xl font-bold text-green-600">
                        ${subscription.billing_cycle === 'monthly' ? subscription.monthly_price : subscription.annual_price}
                      </p>
                      <p className="text-xs sm:text-sm text-gray-500">
                        {subscription.billing_cycle === 'monthly' ? 'Per Month' : 'Per Year'}
                      </p>
                    </div>
                    <div className="text-center p-3 sm:p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <p className="text-xl sm:text-2xl font-bold text-blue-600">
                        {subscription.max_properties === 0 ? '∞' : subscription.max_properties}
                      </p>
                      <p className="text-xs sm:text-sm text-gray-500">Properties</p>
                    </div>
                    <div className="text-center p-3 sm:p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                      <p className="text-xl sm:text-2xl font-bold text-purple-600">
                        {subscription.max_scans_per_month === 0 ? '∞' : subscription.max_scans_per_month}
                      </p>
                      <p className="text-xs sm:text-sm text-gray-500">Scans/Month</p>
                    </div>
                    <div className="text-center p-3 sm:p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                      <p className="text-xl sm:text-2xl font-bold text-orange-600">
                        {subscription.max_users}
                      </p>
                      <p className="text-xs sm:text-sm text-gray-500">Users</p>
                    </div>
                  </div>

                  {/* Features Section */}
                  <div className="space-y-4 sm:space-y-6">
                    <div>
                      <h4 className="font-medium mb-3 text-sm sm:text-base">Included Features</h4>
                      <div className="flex flex-wrap gap-2">
                        {subscription.features.map((feature, index) => (
                          <Badge 
                            key={index} 
                            variant="outline" 
                            className="text-xs px-2 py-1 hover:bg-primary/10 transition-colors duration-200"
                          >
                            {feature.replace('_', ' ')}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {subscription.trial_end_date && (
                      <div className="p-3 sm:p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <p className="text-xs sm:text-sm text-blue-800 dark:text-blue-200">
                          <strong>Trial Period:</strong> Your trial ends on {new Date(subscription.trial_end_date).toLocaleDateString()}
                        </p>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                      <div className="text-xs sm:text-sm text-gray-600 space-y-1">
                        <p>Next billing date: {subscription.next_billing_date ? new Date(subscription.next_billing_date).toLocaleDateString() : 'N/A'}</p>
                        <p>Auto-renewal: {subscription.auto_renew ? 'Enabled' : 'Disabled'}</p>
                      </div>
                      <div className="flex flex-col sm:flex-row gap-2">
                        <AnimaticButton 
                          variant="outline" 
                          size={isMobile ? "sm" : "default"}
                          className="w-full sm:w-auto"
                          animation="bounce"
                        >
                          <Settings className="h-4 w-4 mr-1" />
                          Manage
                        </AnimaticButton>
                        <AnimaticButton 
                          variant="outline" 
                          size={isMobile ? "sm" : "default"}
                          className="w-full sm:w-auto"
                          animation="bounce"
                        >
                          <Download className="h-4 w-4 mr-1" />
                          Invoice
                        </AnimaticButton>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </AnimaticCard>
            ))}
          </TabsContent>

          <TabsContent value="plans" className="space-y-4 sm:space-y-6 animate-fade-in-up">
            <AnimaticCardGrid columns={isMobile ? 1 : isTablet ? 2 : 3} gap="lg" stagger={150}>
              {plans.map((plan, index) => (
                <AnimaticCard 
                  key={plan.id} 
                  variant={plan.is_popular ? 'elevated' : 'default'}
                  animation="scale"
                  delay={index * 150}
                  className={`${plan.is_popular ? 'ring-2 ring-purple-500 shadow-xl shadow-purple-500/20' : ''} 
                             hover:shadow-xl hover:shadow-primary/10 transition-all duration-300`}
                >
                  <CardHeader className="p-4 sm:p-6">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                      <div className="flex items-center space-x-2 sm:space-x-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                          {getTierIcon(plan.tier)}
                        </div>
                        <CardTitle className="text-lg sm:text-xl animatic-heading">
                          {plan.plan_name}
                        </CardTitle>
                      </div>
                      {plan.is_popular && (
                        <Badge className="bg-purple-100 text-purple-800 px-3 py-1 text-xs sm:text-sm">
                          Most Popular
                        </Badge>
                      )}
                    </div>
                    <CardDescription className="text-sm sm:text-base mt-2">
                      {plan.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-4 sm:p-6">
                    <div className="space-y-4 sm:space-y-6">
                      {/* Pricing Section */}
                      <div className="text-center p-4 bg-gradient-to-r from-primary/5 to-accent/5 rounded-lg">
                        <div className="text-2xl sm:text-3xl font-bold text-primary">
                          ${plan.monthly_price}
                        </div>
                        <div className="text-xs sm:text-sm text-gray-500">per month</div>
                        <div className="text-xs sm:text-sm text-green-600 mt-1">
                          or ${plan.annual_price} annually (save ${(plan.monthly_price * 12 - plan.annual_price)})
                        </div>
                      </div>

                      {/* Plan Limits */}
                      <div className="space-y-3">
                        <div className="grid grid-cols-2 gap-3 text-xs sm:text-sm">
                          <div className="flex justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                            <span>Properties</span>
                            <span className="font-medium">
                              {plan.max_properties === 0 ? '∞' : plan.max_properties}
                            </span>
                          </div>
                          <div className="flex justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                            <span>Scans/month</span>
                            <span className="font-medium">
                              {plan.max_scans_per_month === 0 ? '∞' : plan.max_scans_per_month}
                            </span>
                          </div>
                          <div className="flex justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                            <span>Documents</span>
                            <span className="font-medium">
                              {plan.max_documents === 0 ? '∞' : plan.max_documents}
                            </span>
                          </div>
                          <div className="flex justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                            <span>Users</span>
                            <span className="font-medium">
                              {plan.max_users === 0 ? '∞' : plan.max_users}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Features List */}
                      <div className="space-y-2">
                        <h4 className="font-medium text-sm sm:text-base">Features:</h4>
                        <div className="space-y-2">
                          {plan.included_features.map((feature, index) => (
                            <div key={index} className="flex items-center space-x-2 text-xs sm:text-sm">
                              <CheckCircle className="h-3 w-3 sm:h-4 sm:w-4 text-green-500 flex-shrink-0" />
                              <span>{feature.replace('_', ' ')}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Action Button */}
                      <AnimaticButton 
                        className="w-full" 
                        variant={plan.is_popular ? "animatic" : "outline"}
                        size={isMobile ? "sm" : "default"}
                        animation="bounce"
                      >
                        {subscriptions.some(s => s.tier === plan.tier) ? 'Current Plan' : 'Choose Plan'}
                      </AnimaticButton>
                    </div>
                  </CardContent>
                </AnimaticCard>
              ))}
            </AnimaticCardGrid>
          </TabsContent>

        <TabsContent value="billing" className="space-y-4">
          <div className="grid gap-4">
            {invoices.map((invoice) => (
              <Card key={invoice.id}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{invoice.invoice_number}</h3>
                        <Badge className={getStatusColor(invoice.status)}>
                          {invoice.status}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(invoice.invoice_date).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-sm text-gray-500">Subtotal</p>
                          <p className="font-medium">${invoice.subtotal.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Tax</p>
                          <p className="font-medium">${invoice.tax_amount.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Discount</p>
                          <p className="font-medium">${invoice.discount_amount.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Total</p>
                          <p className="font-medium text-lg">${invoice.total_amount.toFixed(2)}</p>
                        </div>
                      </div>
                      <div className="mt-4">
                        <p className="text-sm text-gray-500">
                          Due: {new Date(invoice.due_date).toLocaleDateString()}
                        </p>
                        {invoice.paid_at && (
                          <p className="text-sm text-green-600">
                            Paid: {new Date(invoice.paid_at).toLocaleString()}
                          </p>
                        )}
                      </div>
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
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="usage" className="space-y-4">
          {usageTracking.map((usage) => (
            <Card key={usage.subscription_id}>
              <CardHeader>
                <CardTitle>Usage for {new Date(usage.period_start).toLocaleDateString()} - {new Date(usage.period_end).toLocaleDateString()}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{usage.properties_created}</p>
                    <p className="text-sm text-gray-500">Properties Created</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{usage.scans_performed}</p>
                    <p className="text-sm text-gray-500">Scans Performed</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">{usage.documents_uploaded}</p>
                    <p className="text-sm text-gray-500">Documents Uploaded</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-orange-600">{usage.api_calls}</p>
                    <p className="text-sm text-gray-500">API Calls</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="text-center">
                    <p className="text-lg font-bold text-gray-600">
                      {formatFileSize(usage.storage_used_mb * 1024 * 1024)}
                    </p>
                    <p className="text-sm text-gray-500">Storage Used</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-red-600">
                      ${usage.overage_charges.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-500">Overage Charges</p>
                  </div>
                </div>

                {usage.overage_charges > 0 && (
                  <div className="p-4 bg-yellow-50 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      <strong>Overage Notice:</strong> You have exceeded your plan limits and incurred overage charges. 
                      Consider upgrading your plan to avoid future charges.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Billing Settings</CardTitle>
              <CardDescription>Manage your payment methods and billing preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Payment Method</h4>
                  <p className="text-sm text-gray-500">**** **** **** 1234</p>
                </div>
                <Button variant="outline" size="sm">
                  Update
                </Button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Billing Address</h4>
                  <p className="text-sm text-gray-500">123 Main St, Anytown, ST 12345</p>
                </div>
                <Button variant="outline" size="sm">
                  Update
                </Button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Auto-renewal</h4>
                  <p className="text-sm text-gray-500">Automatically renew subscription</p>
                </div>
                <Button variant="outline" size="sm">
                  Toggle
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Account Settings</CardTitle>
              <CardDescription>Manage your account preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Email Notifications</h4>
                  <p className="text-sm text-gray-500">Receive billing and usage notifications</p>
                </div>
                <Button variant="outline" size="sm">
                  Configure
                </Button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Data Export</h4>
                  <p className="text-sm text-gray-500">Download your data</p>
                </div>
                <Button variant="outline" size="sm">
                  Export
                </Button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Cancel Subscription</h4>
                  <p className="text-sm text-gray-500">Cancel your subscription</p>
                </div>
                <Button variant="destructive" size="sm">
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
          </TabsContent>
        </Tabs>
      </div>
      </div>
    </AppLayout>
  );
};

export default SubscriptionManagement;
