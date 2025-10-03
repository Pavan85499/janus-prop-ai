import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  Handshake, 
  FileText, 
  Mail, 
  Phone, 
  DollarSign, 
  Calendar,
  CheckCircle,
  Clock,
  AlertTriangle,
  Play,
  Pause,
  RefreshCw,
  Download,
  Eye,
  Plus,
  Building,
  User,
  CreditCard,
  FileCheck,
  Send,
  Edit,
  Trash2
} from "lucide-react";
import { AppLayout } from '@/components/layout/AppLayout';

interface DealExecution {
  id: number;
  property_id: number;
  property_address: string;
  deal_name: string;
  status: string;
  offer_type: string;
  offer_price: number;
  earnest_money: number;
  down_payment: number;
  loan_amount: number;
  closing_date: string;
  success_probability: number;
  created_at: string;
  updated_at: string;
}

interface OwnerContact {
  id: number;
  deal_id: number;
  contact_method: string;
  contact_date: string;
  subject: string;
  message: string;
  response_received: boolean;
  response_date?: string;
  response_content?: string;
  ai_sentiment_score: number;
  follow_up_required: boolean;
  follow_up_date?: string;
}

interface OfferLetter {
  id: number;
  deal_id: number;
  letter_title: string;
  letter_content: string;
  letter_type: string;
  offer_price: number;
  status: string;
  sent_at?: string;
  created_at: string;
}

interface Contract {
  id: number;
  deal_id: number;
  contract_title: string;
  contract_type: string;
  purchase_price: number;
  status: string;
  buyer_signed_at?: string;
  seller_signed_at?: string;
  executed_at?: string;
  created_at: string;
}

interface Lender {
  id: number;
  lender_name: string;
  lender_type: string;
  contact_person: string;
  email: string;
  phone: string;
  interest_rates: any;
  minimum_down_payment: number;
  maximum_loan_amount: number;
  is_preferred: boolean;
  rating: number;
}

const ExecutionClosing: React.FC = () => {
  const [deals, setDeals] = useState<DealExecution[]>([]);
  const [ownerContacts, setOwnerContacts] = useState<OwnerContact[]>([]);
  const [offerLetters, setOfferLetters] = useState<OfferLetter[]>([]);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [lenders, setLenders] = useState<Lender[]>([]);
  const [selectedDeal, setSelectedDeal] = useState<DealExecution | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  // Mock data
  useEffect(() => {
    setDeals([
      {
        id: 1,
        property_id: 1,
        property_address: "123 Main St, Anytown, ST 12345",
        deal_name: "Main Street Investment",
        status: "under_contract",
        offer_type: "financed",
        offer_price: 450000,
        earnest_money: 10000,
        down_payment: 90000,
        loan_amount: 360000,
        closing_date: "2024-02-15T00:00:00Z",
        success_probability: 85,
        created_at: "2024-01-15T10:30:00Z",
        updated_at: "2024-01-15T10:30:00Z"
      },
      {
        id: 2,
        property_id: 2,
        property_address: "456 Oak Ave, Anytown, ST 12345",
        deal_name: "Oak Avenue Flip",
        status: "offer_submitted",
        offer_type: "cash",
        offer_price: 320000,
        earnest_money: 5000,
        down_payment: 320000,
        loan_amount: 0,
        closing_date: "2024-02-01T00:00:00Z",
        success_probability: 72,
        created_at: "2024-01-14T14:20:00Z",
        updated_at: "2024-01-14T14:20:00Z"
      },
      {
        id: 3,
        property_id: 3,
        property_address: "789 Pine St, Anytown, ST 12345",
        deal_name: "Pine Street Rental",
        status: "draft",
        offer_type: "financed",
        offer_price: 280000,
        earnest_money: 0,
        down_payment: 56000,
        loan_amount: 224000,
        closing_date: "2024-02-28T00:00:00Z",
        success_probability: 0,
        created_at: "2024-01-13T09:15:00Z",
        updated_at: "2024-01-13T09:15:00Z"
      }
    ]);

    setOwnerContacts([
      {
        id: 1,
        deal_id: 1,
        contact_method: "email",
        contact_date: "2024-01-15T10:30:00Z",
        subject: "Initial Offer Discussion",
        message: "Hello, I'm interested in purchasing your property at 123 Main St. I'd like to discuss the terms and schedule a viewing.",
        response_received: true,
        response_date: "2024-01-15T14:20:00Z",
        response_content: "Thank you for your interest. I'm available to discuss the property. When would be a good time to meet?",
        ai_sentiment_score: 0.8,
        follow_up_required: true,
        follow_up_date: "2024-01-17T00:00:00Z"
      },
      {
        id: 2,
        deal_id: 2,
        contact_method: "phone",
        contact_date: "2024-01-14T16:45:00Z",
        subject: "Property Inquiry",
        message: "Called to discuss property details and pricing.",
        response_received: false,
        ai_sentiment_score: 0.0,
        follow_up_required: true,
        follow_up_date: "2024-01-16T00:00:00Z"
      }
    ]);

    setOfferLetters([
      {
        id: 1,
        deal_id: 1,
        letter_title: "Purchase Offer - 123 Main St",
        letter_content: "Dear Property Owner, I am writing to submit a formal offer to purchase your property...",
        letter_type: "initial_offer",
        offer_price: 450000,
        status: "sent",
        sent_at: "2024-01-15T11:00:00Z",
        created_at: "2024-01-15T10:45:00Z"
      }
    ]);

    setContracts([
      {
        id: 1,
        deal_id: 1,
        contract_title: "Purchase and Sale Agreement - 123 Main St",
        contract_type: "purchase_agreement",
        purchase_price: 450000,
        status: "draft",
        created_at: "2024-01-15T12:00:00Z"
      }
    ]);

    setLenders([
      {
        id: 1,
        lender_name: "First National Bank",
        lender_type: "bank",
        contact_person: "John Smith",
        email: "john.smith@fnb.com",
        phone: "(555) 123-4567",
        interest_rates: { "30_year": 6.5, "15_year": 6.0 },
        minimum_down_payment: 20,
        maximum_loan_amount: 2000000,
        is_preferred: true,
        rating: 4.8
      },
      {
        id: 2,
        lender_name: "Community Credit Union",
        lender_type: "credit_union",
        contact_person: "Sarah Johnson",
        email: "sarah.johnson@ccu.com",
        phone: "(555) 987-6543",
        interest_rates: { "30_year": 6.3, "15_year": 5.8 },
        minimum_down_payment: 15,
        maximum_loan_amount: 1500000,
        is_preferred: false,
        rating: 4.6
      }
    ]);
  }, []);

  const filteredDeals = deals.filter(deal => {
    const matchesSearch = deal.property_address.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         deal.deal_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || deal.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'under_contract':
        return 'bg-green-100 text-green-800';
      case 'offer_submitted':
        return 'bg-yellow-100 text-yellow-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'closed':
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'under_contract':
        return <CheckCircle className="h-4 w-4" />;
      case 'offer_submitted':
        return <Clock className="h-4 w-4" />;
      case 'draft':
        return <Edit className="h-4 w-4" />;
      case 'closed':
        return <CheckCircle className="h-4 w-4" />;
      case 'cancelled':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getSuccessProbabilityColor = (probability: number) => {
    if (probability >= 80) return 'text-green-600';
    if (probability >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <AppLayout>
      <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Execution & Closing</h1>
          <p className="text-muted-foreground">
            Manage deal execution, owner contacts, offers, contracts, and financing
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Deal
        </Button>
      </div>

      <Tabs defaultValue="deals" className="space-y-4">
        <TabsList>
          <TabsTrigger value="deals">Deal Pipeline</TabsTrigger>
          <TabsTrigger value="contacts">Owner Contacts</TabsTrigger>
          <TabsTrigger value="offers">Offer Letters</TabsTrigger>
          <TabsTrigger value="contracts">Contracts</TabsTrigger>
          <TabsTrigger value="financing">Financing</TabsTrigger>
        </TabsList>

        <TabsContent value="deals" className="space-y-4">
          {/* Search and Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Input
                      placeholder="Search deals..."
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
                  <option value="draft">Draft</option>
                  <option value="offer_submitted">Offer Submitted</option>
                  <option value="under_contract">Under Contract</option>
                  <option value="closed">Closed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>
            </CardContent>
          </Card>

          {/* Deals List */}
          <div className="grid gap-4">
            {filteredDeals.map((deal) => (
              <Card key={deal.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{deal.deal_name}</h3>
                        <Badge className={getStatusColor(deal.status)}>
                          {getStatusIcon(deal.status)}
                          <span className="ml-1">{deal.status.replace('_', ' ')}</span>
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(deal.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-4">{deal.property_address}</p>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-green-600">
                            ${deal.offer_price.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-500">Offer Price</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-blue-600">
                            ${deal.earnest_money.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-500">Earnest Money</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-purple-600">
                            {deal.offer_type}
                          </p>
                          <p className="text-sm text-gray-500">Offer Type</p>
                        </div>
                        <div className="text-center">
                          <p className={`text-2xl font-bold ${getSuccessProbabilityColor(deal.success_probability)}`}>
                            {deal.success_probability}%
                          </p>
                          <p className="text-sm text-gray-500">Success Probability</p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Badge variant="outline">
                            <Calendar className="h-3 w-3 mr-1" />
                            Closing: {new Date(deal.closing_date).toLocaleDateString()}
                          </Badge>
                          <Badge variant="outline">
                            <DollarSign className="h-3 w-3 mr-1" />
                            Loan: ${deal.loan_amount.toLocaleString()}
                          </Badge>
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View Details
                          </Button>
                          <Button variant="outline" size="sm">
                            <Edit className="h-4 w-4 mr-1" />
                            Edit
                          </Button>
                          <Button variant="outline" size="sm">
                            <Download className="h-4 w-4 mr-1" />
                            Export
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

        <TabsContent value="contacts" className="space-y-4">
          <div className="grid gap-4">
            {ownerContacts.map((contact) => (
              <Card key={contact.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{contact.subject}</h3>
                        <Badge variant="outline">
                          {contact.contact_method}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(contact.contact_date).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-4">{contact.message}</p>
                      
                      {contact.response_received && (
                        <div className="p-4 bg-green-50 rounded-lg mb-4">
                          <p className="text-sm text-green-800">
                            <strong>Response:</strong> {contact.response_content}
                          </p>
                          <p className="text-xs text-green-600 mt-1">
                            Received: {new Date(contact.response_date!).toLocaleString()}
                          </p>
                        </div>
                      )}

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Badge variant={contact.response_received ? "default" : "secondary"}>
                            {contact.response_received ? "Response Received" : "Awaiting Response"}
                          </Badge>
                          <Badge variant="outline">
                            Sentiment: {(contact.ai_sentiment_score * 100).toFixed(0)}%
                          </Badge>
                          {contact.follow_up_required && (
                            <Badge variant="destructive">
                              Follow-up Required
                            </Badge>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                          <Button variant="outline" size="sm">
                            <Send className="h-4 w-4 mr-1" />
                            Follow Up
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

        <TabsContent value="offers" className="space-y-4">
          <div className="grid gap-4">
            {offerLetters.map((letter) => (
              <Card key={letter.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{letter.letter_title}</h3>
                        <Badge className={getStatusColor(letter.status)}>
                          {letter.status}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(letter.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                        {letter.letter_content}
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Badge variant="outline">
                            ${letter.offer_price.toLocaleString()}
                          </Badge>
                          <Badge variant="outline">
                            {letter.letter_type.replace('_', ' ')}
                          </Badge>
                          {letter.sent_at && (
                            <span className="text-sm text-gray-500">
                              Sent: {new Date(letter.sent_at).toLocaleString()}
                            </span>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                          <Button variant="outline" size="sm">
                            <Edit className="h-4 w-4 mr-1" />
                            Edit
                          </Button>
                          <Button variant="outline" size="sm">
                            <Send className="h-4 w-4 mr-1" />
                            Send
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

        <TabsContent value="contracts" className="space-y-4">
          <div className="grid gap-4">
            {contracts.map((contract) => (
              <Card key={contract.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{contract.contract_title}</h3>
                        <Badge className={getStatusColor(contract.status)}>
                          {contract.status}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {new Date(contract.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Badge variant="outline">
                            ${contract.purchase_price.toLocaleString()}
                          </Badge>
                          <Badge variant="outline">
                            {contract.contract_type.replace('_', ' ')}
                          </Badge>
                          {contract.buyer_signed_at && (
                            <Badge variant="default">
                              Buyer Signed
                            </Badge>
                          )}
                          {contract.seller_signed_at && (
                            <Badge variant="default">
                              Seller Signed
                            </Badge>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                          <Button variant="outline" size="sm">
                            <Edit className="h-4 w-4 mr-1" />
                            Edit
                          </Button>
                          <Button variant="outline" size="sm">
                            <FileCheck className="h-4 w-4 mr-1" />
                            Sign
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

        <TabsContent value="financing" className="space-y-4">
          <div className="grid gap-4">
            {lenders.map((lender) => (
              <Card key={lender.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-4">
                        <h3 className="text-lg font-medium">{lender.lender_name}</h3>
                        <Badge variant="outline">
                          {lender.lender_type}
                        </Badge>
                        {lender.is_preferred && (
                          <Badge variant="default">
                            Preferred
                          </Badge>
                        )}
                        <div className="flex items-center">
                          {[...Array(5)].map((_, i) => (
                            <span
                              key={i}
                              className={`text-yellow-400 ${
                                i < Math.floor(lender.rating) ? 'text-yellow-400' : 'text-gray-300'
                              }`}
                            >
                              ★
                            </span>
                          ))}
                          <span className="ml-1 text-sm text-gray-500">
                            {lender.rating}
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mb-4">
                        Contact: {lender.contact_person} | {lender.email} | {lender.phone}
                      </p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div className="text-center">
                          <p className="text-lg font-bold text-green-600">
                            {lender.interest_rates["30_year"]}%
                          </p>
                          <p className="text-sm text-gray-500">30-Year Rate</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-bold text-blue-600">
                            {lender.minimum_down_payment}%
                          </p>
                          <p className="text-sm text-gray-500">Min Down Payment</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-bold text-purple-600">
                            ${(lender.maximum_loan_amount / 1000000).toFixed(1)}M
                          </p>
                          <p className="text-sm text-gray-500">Max Loan Amount</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-bold text-orange-600">
                            {lender.interest_rates["15_year"]}%
                          </p>
                          <p className="text-sm text-gray-500">15-Year Rate</p>
                        </div>
                      </div>
                      <div className="flex justify-end space-x-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-1" />
                          View Details
                        </Button>
                        <Button variant="outline" size="sm">
                          <Phone className="h-4 w-4 mr-1" />
                          Contact
                        </Button>
                        <Button size="sm">
                          <CreditCard className="h-4 w-4 mr-1" />
                          Apply
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
      </div>
    </AppLayout>
  );
};

export default ExecutionClosing;
