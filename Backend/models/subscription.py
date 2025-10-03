from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

Base = declarative_base()

class SubscriptionTier(str, Enum):
    LITE = "lite"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User Reference
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="subscriptions")
    
    # Subscription Details
    tier = Column(String(50), nullable=False)
    status = Column(String(50), default=SubscriptionStatus.ACTIVE)
    billing_cycle = Column(String(50), default=BillingCycle.MONTHLY)
    
    # Pricing
    monthly_price = Column(Float, nullable=False)
    annual_price = Column(Float, default=0)
    setup_fee = Column(Float, default=0)
    transaction_fee_rate = Column(Float, default=0)  # Percentage
    
    # Limits and Features
    max_properties = Column(Integer, default=0)  # 0 = unlimited
    max_scans_per_month = Column(Integer, default=0)  # 0 = unlimited
    max_documents = Column(Integer, default=0)  # 0 = unlimited
    max_users = Column(Integer, default=1)
    features = Column(JSON)  # List of enabled features
    
    # Trial Information
    trial_start_date = Column(DateTime)
    trial_end_date = Column(DateTime)
    trial_days = Column(Integer, default=14)
    
    # Billing Information
    billing_start_date = Column(DateTime, default=datetime.utcnow)
    billing_end_date = Column(DateTime)
    next_billing_date = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    
    # Payment Information
    payment_method_id = Column(String(255))  # Stripe payment method ID
    payment_method_type = Column(String(50))  # card, bank_account, etc.
    last_payment_date = Column(DateTime)
    last_payment_amount = Column(Float, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    cancelled_at = Column(DateTime)
    cancelled_reason = Column(Text)

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    subscription = relationship("Subscription", back_populates="invoices")
    
    # Invoice Details
    invoice_number = Column(String(100), unique=True, nullable=False)
    invoice_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    
    # Amounts
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    
    # Status
    status = Column(String(50), default=PaymentStatus.PENDING)
    paid_at = Column(DateTime)
    payment_method = Column(String(50))
    payment_reference = Column(String(255))
    
    # Line Items
    line_items = Column(JSON)  # Detailed line items
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    subscription = relationship("Subscription", back_populates="transactions")
    
    # Transaction Details
    transaction_type = Column(String(50), nullable=False)  # subscription, transaction_fee, setup_fee, etc.
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Payment Information
    payment_status = Column(String(50), default=PaymentStatus.PENDING)
    payment_method = Column(String(50))
    payment_reference = Column(String(255))
    stripe_payment_intent_id = Column(String(255))
    
    # Description
    description = Column(Text)
    transaction_metadata = Column(JSON)  # Additional transaction metadata
    
    # Timestamps
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class UsageTracking(Base):
    __tablename__ = "usage_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    subscription = relationship("Subscription", back_populates="usage_tracking")
    
    # Usage Period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Usage Metrics
    properties_created = Column(Integer, default=0)
    scans_performed = Column(Integer, default=0)
    documents_uploaded = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    storage_used_mb = Column(Float, default=0)
    
    # Overage Charges
    overage_charges = Column(Float, default=0)
    overage_reason = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

class Feature(Base):
    __tablename__ = "features"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Feature Details
    feature_name = Column(String(255), nullable=False)
    feature_code = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))  # core, advanced, premium, enterprise
    
    # Pricing
    is_included = Column(Boolean, default=True)  # Included in base plan
    additional_cost = Column(Float, default=0)  # Additional cost per month
    usage_based_pricing = Column(Boolean, default=False)
    usage_rate = Column(Float, default=0)  # Cost per usage unit
    
    # Limits
    usage_limit = Column(Integer, default=0)  # 0 = unlimited
    usage_limit_period = Column(String(50))  # monthly, annually
    
    # Status
    is_active = Column(Boolean, default=True)
    is_beta = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Plan Details
    plan_name = Column(String(255), nullable=False)
    tier = Column(String(50), nullable=False)
    description = Column(Text)
    
    # Pricing
    monthly_price = Column(Float, nullable=False)
    annual_price = Column(Float, default=0)
    setup_fee = Column(Float, default=0)
    transaction_fee_rate = Column(Float, default=0)
    
    # Limits
    max_properties = Column(Integer, default=0)
    max_scans_per_month = Column(Integer, default=0)
    max_documents = Column(Integer, default=0)
    max_users = Column(Integer, default=1)
    max_api_calls_per_month = Column(Integer, default=0)
    storage_limit_gb = Column(Float, default=0)
    
    # Features
    included_features = Column(JSON)  # List of included feature codes
    available_features = Column(JSON)  # List of available feature codes
    
    # Status
    is_active = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models for API
class SubscriptionRequest(BaseModel):
    tier: SubscriptionTier
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    payment_method_id: Optional[str] = None
    trial_days: int = 14

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    tier: str
    status: str
    billing_cycle: str
    monthly_price: float
    annual_price: float
    max_properties: int
    max_scans_per_month: int
    max_documents: int
    max_users: int
    features: Optional[List[str]]
    trial_start_date: Optional[datetime]
    trial_end_date: Optional[datetime]
    billing_start_date: datetime
    next_billing_date: Optional[datetime]
    auto_renew: bool
    created_at: datetime

    class Config:
        from_attributes = True

class InvoiceResponse(BaseModel):
    id: int
    subscription_id: int
    invoice_number: str
    invoice_date: datetime
    due_date: datetime
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    status: str
    paid_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class UsageResponse(BaseModel):
    subscription_id: int
    period_start: datetime
    period_end: datetime
    properties_created: int
    scans_performed: int
    documents_uploaded: int
    api_calls: int
    storage_used_mb: float
    overage_charges: float
    created_at: datetime

    class Config:
        from_attributes = True

class SubscriptionPlanResponse(BaseModel):
    id: int
    plan_name: str
    tier: str
    description: str
    monthly_price: float
    annual_price: float
    max_properties: int
    max_scans_per_month: int
    max_documents: int
    max_users: int
    included_features: List[str]
    is_active: bool
    is_popular: bool

    class Config:
        from_attributes = True

# Add relationships to existing models
Subscription.invoices = relationship("Invoice", back_populates="subscription")
Subscription.transactions = relationship("Transaction", back_populates="subscription")
Subscription.usage_tracking = relationship("UsageTracking", back_populates="subscription")
