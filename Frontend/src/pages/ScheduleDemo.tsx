import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Calendar, Clock, CheckCircle, ArrowLeft, Users, Building, Phone, Mail } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface TimeSlot {
  id: string;
  start_time: string;
  end_time: string;
  is_available: boolean;
  timezone: string;
}

interface DemoAvailability {
  date: string;
  available_slots: TimeSlot[];
  timezone: string;
}

interface DemoRequest {
  first_name: string;
  last_name: string;
  email: string;
  company?: string;
  phone?: string;
  demo_type: string;
  preferred_date: string;
  preferred_time_slots: string[];
  timezone: string;
  company_size?: string;
  current_solution?: string;
  specific_requirements?: string;
}

const DEMO_TYPES = [
  { value: "platform_overview", label: "Platform Overview", description: "Complete platform walkthrough" },
  { value: "ai_agents", label: "AI Agents", description: "AI agent capabilities and automation" },
  { value: "property_analysis", label: "Property Analysis", description: "Advanced property analysis tools" },
  { value: "market_intelligence", label: "Market Intelligence", description: "Market data and insights" },
  { value: "investment_opportunities", label: "Investment Opportunities", description: "Deal discovery and analysis" },
  { value: "custom", label: "Custom Demo", description: "Tailored to your specific needs" },
];

const COMPANY_SIZES = [
  { value: "startup", label: "Startup (1-10 employees)" },
  { value: "small", label: "Small (11-50 employees)" },
  { value: "medium", label: "Medium (51-200 employees)" },
  { value: "enterprise", label: "Enterprise (200+ employees)" },
];

export default function ScheduleDemo() {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [availability, setAvailability] = useState<DemoAvailability[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [selectedSlots, setSelectedSlots] = useState<string[]>([]);
  const [showSuccess, setShowSuccess] = useState(false);
  
  const [formData, setFormData] = useState<DemoRequest>({
    first_name: "",
    last_name: "",
    email: "",
    company: "",
    phone: "",
    demo_type: "",
    preferred_date: "",
    preferred_time_slots: [],
    timezone: "UTC",
    company_size: "",
    current_solution: "",
    specific_requirements: "",
  });

  // Load availability on component mount
  useEffect(() => {
    loadAvailability();
  }, []);

  const loadAvailability = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/demo-schedule/availability`);
      if (response.ok) {
        const data = await response.json();
        setAvailability(data);
      } else {
        toast({
          title: "Error",
          description: "Failed to load available time slots",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to connect to server",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof DemoRequest, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleDateSelect = (date: string) => {
    setSelectedDate(date);
    setFormData(prev => ({ ...prev, preferred_date: date }));
    setSelectedSlots([]);
  };

  const handleSlotSelect = (slotId: string) => {
    setSelectedSlots(prev => {
      if (prev.includes(slotId)) {
        return prev.filter(id => id !== slotId);
      } else {
        return [...prev, slotId];
      }
    });
  };

  const formatTime = (timeString: string) => {
    const date = new Date(timeString);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      const requestData = {
        ...formData,
        preferred_time_slots: selectedSlots,
      };

      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/demo-schedule/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (response.ok) {
        setShowSuccess(true);
        toast({
          title: "Demo Scheduled!",
          description: "We'll send you a confirmation email shortly.",
        });
      } else {
        const error = await response.json();
        toast({
          title: "Error",
          description: error.detail || "Failed to schedule demo",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to connect to server",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const nextStep = () => {
    if (step === 1 && (!formData.first_name || !formData.last_name || !formData.email || !formData.demo_type)) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }
    if (step === 2 && (!selectedDate || selectedSlots.length === 0)) {
      toast({
        title: "Missing Information",
        description: "Please select a date and at least one time slot",
        variant: "destructive",
      });
      return;
    }
    setStep(step + 1);
  };

  const prevStep = () => {
    setStep(step - 1);
  };

  if (showSuccess) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background to-muted flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full"
        >
          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="w-16 h-16 bg-success/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-success" />
              </div>
              <h2 className="text-2xl font-bold mb-2">Demo Scheduled Successfully!</h2>
              <p className="text-muted-foreground mb-6">
                We've received your demo request and will send you a confirmation email shortly.
              </p>
              <div className="space-y-2">
                <Button onClick={() => navigate('/')} className="w-full">
                  Return to Home
                </Button>
                <Button variant="outline" onClick={() => {
                  setShowSuccess(false);
                  setStep(1);
                  setFormData({
                    first_name: "",
                    last_name: "",
                    email: "",
                    company: "",
                    phone: "",
                    demo_type: "",
                    preferred_date: "",
                    preferred_time_slots: [],
                    timezone: "UTC",
                    company_size: "",
                    current_solution: "",
                    specific_requirements: "",
                  });
                  setSelectedDate("");
                  setSelectedSlots([]);
                }} className="w-full">
                  Schedule Another Demo
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Button>
            <h1 className="text-xl font-semibold">Schedule a Demo</h1>
            <div className="w-20" /> {/* Spacer */}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Progress Indicator */}
          <div className="flex items-center justify-center mb-8">
            <div className="flex items-center space-x-4">
              {[1, 2, 3].map((stepNumber) => (
                <div key={stepNumber} className="flex items-center">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                      step >= stepNumber
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {stepNumber}
                  </div>
                  {stepNumber < 3 && (
                    <div
                      className={`w-16 h-1 mx-2 ${
                        step > stepNumber ? "bg-primary" : "bg-muted"
                      }`}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2">
              <motion.div
                key={step}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                {step === 1 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Users className="w-5 h-5" />
                        Contact Information
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="first_name">First Name *</Label>
                          <Input
                            id="first_name"
                            value={formData.first_name}
                            onChange={(e) => handleInputChange('first_name', e.target.value)}
                            placeholder="Enter your first name"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="last_name">Last Name *</Label>
                          <Input
                            id="last_name"
                            value={formData.last_name}
                            onChange={(e) => handleInputChange('last_name', e.target.value)}
                            placeholder="Enter your last name"
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="email">Email Address *</Label>
                        <Input
                          id="email"
                          type="email"
                          value={formData.email}
                          onChange={(e) => handleInputChange('email', e.target.value)}
                          placeholder="Enter your email address"
                        />
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="company">Company</Label>
                          <Input
                            id="company"
                            value={formData.company}
                            onChange={(e) => handleInputChange('company', e.target.value)}
                            placeholder="Your company name"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="phone">Phone Number</Label>
                          <Input
                            id="phone"
                            value={formData.phone}
                            onChange={(e) => handleInputChange('phone', e.target.value)}
                            placeholder="Your phone number"
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="demo_type">Demo Type *</Label>
                        <Select value={formData.demo_type} onValueChange={(value) => handleInputChange('demo_type', value)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select demo type" />
                          </SelectTrigger>
                          <SelectContent>
                            {DEMO_TYPES.map((type) => (
                              <SelectItem key={type.value} value={type.value}>
                                <div>
                                  <div className="font-medium">{type.label}</div>
                                  <div className="text-sm text-muted-foreground">{type.description}</div>
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="company_size">Company Size</Label>
                        <Select value={formData.company_size} onValueChange={(value) => handleInputChange('company_size', value)}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select company size" />
                          </SelectTrigger>
                          <SelectContent>
                            {COMPANY_SIZES.map((size) => (
                              <SelectItem key={size.value} value={size.value}>
                                {size.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {step === 2 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Calendar className="w-5 h-5" />
                        Select Date & Time
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {loading ? (
                        <div className="text-center py-8">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                          <p className="mt-2 text-muted-foreground">Loading available times...</p>
                        </div>
                      ) : (
                        <div className="space-y-6">
                          {/* Date Selection */}
                          <div>
                            <Label className="text-base font-medium mb-3 block">Available Dates</Label>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              {availability.map((day) => (
                                <Button
                                  key={day.date}
                                  variant={selectedDate === day.date ? "default" : "outline"}
                                  onClick={() => handleDateSelect(day.date)}
                                  className="h-auto p-4 flex flex-col items-start"
                                  disabled={day.available_slots.length === 0}
                                >
                                  <div className="font-medium">{formatDate(day.date)}</div>
                                  <div className="text-sm text-muted-foreground">
                                    {day.available_slots.length} slots available
                                  </div>
                                </Button>
                              ))}
                            </div>
                          </div>

                          {/* Time Slot Selection */}
                          {selectedDate && (
                            <div>
                              <Label className="text-base font-medium mb-3 block">Available Time Slots</Label>
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                {availability
                                  .find(day => day.date === selectedDate)
                                  ?.available_slots.map((slot) => (
                                    <Button
                                      key={slot.id}
                                      variant={selectedSlots.includes(slot.id) ? "default" : "outline"}
                                      onClick={() => handleSlotSelect(slot.id)}
                                      className="h-auto p-3 flex flex-col items-center"
                                    >
                                      <Clock className="w-4 h-4 mb-1" />
                                      <div className="text-sm font-medium">
                                        {formatTime(slot.start_time)}
                                      </div>
                                    </Button>
                                  ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}

                {step === 3 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Additional Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="space-y-2">
                        <Label htmlFor="current_solution">Current Solution</Label>
                        <Input
                          id="current_solution"
                          value={formData.current_solution}
                          onChange={(e) => handleInputChange('current_solution', e.target.value)}
                          placeholder="What solution are you currently using?"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="specific_requirements">Specific Requirements</Label>
                        <Textarea
                          id="specific_requirements"
                          value={formData.specific_requirements}
                          onChange={(e) => handleInputChange('specific_requirements', e.target.value)}
                          placeholder="Tell us about your specific needs and requirements..."
                          rows={4}
                        />
                      </div>
                    </CardContent>
                  </Card>
                )}
              </motion.div>

              {/* Navigation Buttons */}
              <div className="flex justify-between mt-6">
                <Button
                  variant="outline"
                  onClick={prevStep}
                  disabled={step === 1}
                >
                  Previous
                </Button>
                <Button
                  onClick={step === 3 ? handleSubmit : nextStep}
                  disabled={loading}
                >
                  {loading ? "Processing..." : step === 3 ? "Schedule Demo" : "Next"}
                </Button>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Demo Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Demo Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {formData.demo_type && (
                    <div>
                      <Label className="text-sm font-medium text-muted-foreground">Demo Type</Label>
                      <p className="font-medium">
                        {DEMO_TYPES.find(t => t.value === formData.demo_type)?.label}
                      </p>
                    </div>
                  )}
                  
                  {selectedDate && (
                    <div>
                      <Label className="text-sm font-medium text-muted-foreground">Date</Label>
                      <p className="font-medium">{formatDate(selectedDate)}</p>
                    </div>
                  )}
                  
                  {selectedSlots.length > 0 && (
                    <div>
                      <Label className="text-sm font-medium text-muted-foreground">Time Slots</Label>
                      <div className="space-y-1">
                        {selectedSlots.map((slotId) => {
                          const slot = availability
                            .flatMap(day => day.available_slots)
                            .find(s => s.id === slotId);
                          return slot ? (
                            <Badge key={slotId} variant="secondary" className="mr-1">
                              {formatTime(slot.start_time)}
                            </Badge>
                          ) : null;
                        })}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Contact Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Contact Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="w-4 h-4 text-muted-foreground" />
                    <span>demo@januspropai.com</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="w-4 h-4 text-muted-foreground" />
                    <span>+1 (555) 123-4567</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Building className="w-4 h-4 text-muted-foreground" />
                    <span>Janus Prop AI</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
