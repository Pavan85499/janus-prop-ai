from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import json
import uuid

from core.database import get_db
from models.subscription import (
    Subscription, Invoice, Transaction, UsageTracking, Feature, SubscriptionPlan,
    SubscriptionRequest, SubscriptionResponse, InvoiceResponse, UsageResponse,
    SubscriptionPlanResponse, SubscriptionTier, SubscriptionStatus, PaymentStatus,
    BillingCycle
)
from models.user import User
from core.redis_client import publish_event

router = APIRouter()

# Mock payment processing
async def process_payment(amount: float, payment_method_id: str, currency: str = "USD") -> dict:
    """Mock payment processing"""
    await asyncio.sleep(1)
    
    # Mock payment processing logic
    if amount <= 0:
        return {"success": False, "error": "Invalid amount"}
    
    if not payment_method_id:
        return {"success": False, "error": "Payment method required"}
    
    # Mock successful payment
    return {
        "success": True,
        "payment_intent_id": f"pi_{uuid.uuid4().hex[:24]}",
        "transaction_id": f"txn_{uuid.uuid4().hex[:16]}",
        "amount": amount,
        "currency": currency,
        "status": "succeeded"
    }

async def calculate_usage_charges(subscription_id: int, usage_data: dict) -> dict:
    """Calculate usage-based charges"""
    await asyncio.sleep(1)
    
    # Mock usage calculation
    overage_charges = 0.0
    overage_reason = []
    
    # Get subscription limits
    subscription = await get_subscription_by_id(subscription_id)
    if not subscription:
        return {"overage_charges": 0, "overage_reason": []}
    
    # Check property limit
    if subscription.max_properties > 0 and usage_data.get("properties_created", 0) > subscription.max_properties:
        overage = usage_data["properties_created"] - subscription.max_properties
        overage_charges += overage * 10.0  # $10 per additional property
        overage_reason.append(f"Property limit exceeded by {overage}")
    
    # Check scan limit
    if subscription.max_scans_per_month > 0 and usage_data.get("scans_performed", 0) > subscription.max_scans_per_month:
        overage = usage_data["scans_performed"] - subscription.max_scans_per_month
        overage_charges += overage * 5.0  # $5 per additional scan
        overage_reason.append(f"Scan limit exceeded by {overage}")
    
    # Check document limit
    if subscription.max_documents > 0 and usage_data.get("documents_uploaded", 0) > subscription.max_documents:
        overage = usage_data["documents_uploaded"] - subscription.max_documents
        overage_charges += overage * 2.0  # $2 per additional document
        overage_reason.append(f"Document limit exceeded by {overage}")
    
    # Check storage limit
    storage_limit_mb = subscription.storage_limit_gb * 1024 if subscription.storage_limit_gb > 0 else 0
    if storage_limit_mb > 0 and usage_data.get("storage_used_mb", 0) > storage_limit_mb:
        overage = usage_data["storage_used_mb"] - storage_limit_mb
        overage_charges += overage * 0.1  # $0.10 per additional MB
        overage_reason.append(f"Storage limit exceeded by {overage:.1f} MB")
    
    return {
        "overage_charges": overage_charges,
        "overage_reason": overage_reason
    }

async def get_subscription_by_id(subscription_id: int) -> Optional[Subscription]:
    """Get subscription by ID (mock function)"""
    # In production, this would query the database
    return None

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans(
    tier: Optional[SubscriptionTier] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Get available subscription plans"""
    query = db.query(SubscriptionPlan)
    
    if tier:
        query = query.filter(SubscriptionPlan.tier == tier.value)
    
    if is_active:
        query = query.filter(SubscriptionPlan.is_active == True)
    
    plans = query.order_by(SubscriptionPlan.sort_order).all()
    return plans

@router.post("/subscribe", response_model=SubscriptionResponse)
async def create_subscription(
    request: SubscriptionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new subscription"""
    
    # Get subscription plan
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == request.tier.value).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    
    # Calculate pricing
    if request.billing_cycle == BillingCycle.ANNUALLY and plan.annual_price > 0:
        monthly_price = plan.annual_price / 12
        annual_price = plan.annual_price
    else:
        monthly_price = plan.monthly_price
        annual_price = plan.annual_price
    
    # Calculate trial dates
    trial_start_date = datetime.utcnow()
    trial_end_date = trial_start_date + timedelta(days=request.trial_days)
    
    # Calculate billing dates
    billing_start_date = trial_end_date
    next_billing_date = billing_start_date + timedelta(days=30 if request.billing_cycle == BillingCycle.MONTHLY else 90 if request.billing_cycle == BillingCycle.QUARTERLY else 365)
    
    # Create subscription
    subscription = Subscription(
        user_id=1,  # In production, get from authenticated user
        tier=request.tier.value,
        status=SubscriptionStatus.TRIAL,
        billing_cycle=request.billing_cycle.value,
        monthly_price=monthly_price,
        annual_price=annual_price,
        setup_fee=plan.setup_fee,
        transaction_fee_rate=plan.transaction_fee_rate,
        max_properties=plan.max_properties,
        max_scans_per_month=plan.max_scans_per_month,
        max_documents=plan.max_documents,
        max_users=plan.max_users,
        features=plan.included_features,
        trial_start_date=trial_start_date,
        trial_end_date=trial_end_date,
        trial_days=request.trial_days,
        billing_start_date=billing_start_date,
        next_billing_date=next_billing_date,
        payment_method_id=request.payment_method_id
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    # Create initial invoice for setup fee
    if plan.setup_fee > 0:
        invoice = Invoice(
            subscription_id=subscription.id,
            invoice_number=f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
            due_date=datetime.utcnow() + timedelta(days=7),
            subtotal=plan.setup_fee,
            total_amount=plan.setup_fee,
            line_items=[{
                "description": f"Setup fee for {plan.plan_name}",
                "amount": plan.setup_fee,
                "quantity": 1
            }]
        )
        db.add(invoice)
        db.commit()
    
    await publish_event("subscription", "subscription_created", {
        "subscription_id": subscription.id,
        "tier": request.tier.value,
        "trial_days": request.trial_days
    })
    
    return subscription

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    user_id: Optional[int] = None,
    status: Optional[SubscriptionStatus] = None,
    db: Session = Depends(get_db)
):
    """Get subscriptions with filtering"""
    query = db.query(Subscription)
    
    if user_id:
        query = query.filter(Subscription.user_id == user_id)
    
    if status:
        query = query.filter(Subscription.status == status.value)
    
    subscriptions = query.all()
    return subscriptions

@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Get a specific subscription"""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription

@router.post("/subscriptions/{subscription_id}/activate")
async def activate_subscription(
    subscription_id: int,
    payment_method_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Activate a subscription after trial"""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if subscription.status != SubscriptionStatus.TRIAL:
        raise HTTPException(status_code=400, detail="Subscription is not in trial status")
    
    # Process payment
    payment_result = await process_payment(
        subscription.monthly_price,
        payment_method_id,
        "USD"
    )
    
    if not payment_result["success"]:
        raise HTTPException(status_code=400, detail=f"Payment failed: {payment_result['error']}")
    
    # Update subscription
    subscription.status = SubscriptionStatus.ACTIVE
    subscription.payment_method_id = payment_method_id
    subscription.last_payment_date = datetime.utcnow()
    subscription.last_payment_amount = subscription.monthly_price
    db.commit()
    
    # Create transaction record
    transaction = Transaction(
        subscription_id=subscription_id,
        transaction_type="subscription",
        amount=subscription.monthly_price,
        payment_status=PaymentStatus.PAID,
        payment_reference=payment_result["transaction_id"],
        stripe_payment_intent_id=payment_result["payment_intent_id"],
        description=f"Subscription payment for {subscription.tier} plan",
        processed_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    
    await publish_event("subscription", "subscription_activated", {
        "subscription_id": subscription_id,
        "tier": subscription.tier,
        "amount": subscription.monthly_price
    })
    
    return {"message": "Subscription activated successfully"}

@router.post("/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Cancel a subscription"""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if subscription.status in [SubscriptionStatus.CANCELLED, SubscriptionStatus.EXPIRED]:
        raise HTTPException(status_code=400, detail="Subscription is already cancelled or expired")
    
    # Update subscription
    subscription.status = SubscriptionStatus.CANCELLED
    subscription.cancelled_at = datetime.utcnow()
    subscription.cancelled_reason = reason
    subscription.auto_renew = False
    db.commit()
    
    await publish_event("subscription", "subscription_cancelled", {
        "subscription_id": subscription_id,
        "reason": reason
    })
    
    return {"message": "Subscription cancelled successfully"}

@router.get("/subscriptions/{subscription_id}/invoices", response_model=List[InvoiceResponse])
async def get_invoices(subscription_id: int, db: Session = Depends(get_db)):
    """Get invoices for a subscription"""
    invoices = db.query(Invoice).filter(Invoice.subscription_id == subscription_id).all()
    return invoices

@router.post("/subscriptions/{subscription_id}/invoices/{invoice_id}/pay")
async def pay_invoice(
    subscription_id: int,
    invoice_id: int,
    payment_method_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Pay an invoice"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.subscription_id == subscription_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice.status == PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="Invoice is already paid")
    
    # Process payment
    payment_result = await process_payment(
        invoice.total_amount,
        payment_method_id,
        "USD"
    )
    
    if not payment_result["success"]:
        raise HTTPException(status_code=400, detail=f"Payment failed: {payment_result['error']}")
    
    # Update invoice
    invoice.status = PaymentStatus.PAID
    invoice.paid_at = datetime.utcnow()
    invoice.payment_method = "card"
    invoice.payment_reference = payment_result["transaction_id"]
    db.commit()
    
    # Create transaction record
    transaction = Transaction(
        subscription_id=subscription_id,
        transaction_type="invoice_payment",
        amount=invoice.total_amount,
        payment_status=PaymentStatus.PAID,
        payment_reference=payment_result["transaction_id"],
        stripe_payment_intent_id=payment_result["payment_intent_id"],
        description=f"Payment for invoice {invoice.invoice_number}",
        processed_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    
    await publish_event("subscription", "invoice_paid", {
        "subscription_id": subscription_id,
        "invoice_id": invoice_id,
        "amount": invoice.total_amount
    })
    
    return {"message": "Invoice paid successfully"}

@router.get("/subscriptions/{subscription_id}/usage", response_model=List[UsageResponse])
async def get_usage_tracking(subscription_id: int, db: Session = Depends(get_db)):
    """Get usage tracking for a subscription"""
    usage = db.query(UsageTracking).filter(UsageTracking.subscription_id == subscription_id).all()
    return usage

@router.post("/subscriptions/{subscription_id}/usage", response_model=dict)
async def record_usage(
    subscription_id: int,
    background_tasks: BackgroundTasks,
    properties_created: int = 0,
    scans_performed: int = 0,
    documents_uploaded: int = 0,
    api_calls: int = 0,
    storage_used_mb: float = 0,
    db: Session = Depends(get_db)
):
    """Record usage for a subscription"""
    
    # Verify subscription exists
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Get current period
    period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Get or create usage record
    usage = db.query(UsageTracking).filter(
        UsageTracking.subscription_id == subscription_id,
        UsageTracking.period_start == period_start
    ).first()
    
    if not usage:
        usage = UsageTracking(
            subscription_id=subscription_id,
            period_start=period_start,
            period_end=period_end,
            created_by=1
        )
        db.add(usage)
    
    # Update usage metrics
    usage.properties_created += properties_created
    usage.scans_performed += scans_performed
    usage.documents_uploaded += documents_uploaded
    usage.api_calls += api_calls
    usage.storage_used_mb += storage_used_mb
    
    # Calculate overage charges
    usage_data = {
        "properties_created": usage.properties_created,
        "scans_performed": usage.scans_performed,
        "documents_uploaded": usage.documents_uploaded,
        "storage_used_mb": usage.storage_used_mb
    }
    
    overage_calculation = await calculate_usage_charges(subscription_id, usage_data)
    usage.overage_charges = overage_calculation["overage_charges"]
    usage.overage_reason = overage_calculation["overage_reason"]
    
    db.commit()
    
    await publish_event("subscription", "usage_recorded", {
        "subscription_id": subscription_id,
        "properties_created": properties_created,
        "scans_performed": scans_performed,
        "documents_uploaded": documents_uploaded,
        "overage_charges": overage_calculation["overage_charges"]
    })
    
    return {"message": "Usage recorded successfully", "overage_charges": overage_calculation["overage_charges"]}

@router.get("/features", response_model=List[dict])
async def get_features(
    category: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Get available features"""
    query = db.query(Feature)
    
    if category:
        query = query.filter(Feature.category == category)
    
    if is_active:
        query = query.filter(Feature.is_active == True)
    
    features = query.all()
    
    return [
        {
            "id": feature.id,
            "feature_name": feature.feature_name,
            "feature_code": feature.feature_code,
            "description": feature.description,
            "category": feature.category,
            "is_included": feature.is_included,
            "additional_cost": feature.additional_cost,
            "usage_based_pricing": feature.usage_based_pricing,
            "usage_rate": feature.usage_rate,
            "usage_limit": feature.usage_limit,
            "usage_limit_period": feature.usage_limit_period,
            "is_beta": feature.is_beta
        }
        for feature in features
    ]

@router.get("/stats/")
async def get_subscription_stats(db: Session = Depends(get_db)):
    """Get subscription statistics"""
    total_subscriptions = db.query(Subscription).count()
    active_subscriptions = db.query(Subscription).filter(Subscription.status == SubscriptionStatus.ACTIVE).count()
    trial_subscriptions = db.query(Subscription).filter(Subscription.status == SubscriptionStatus.TRIAL).count()
    cancelled_subscriptions = db.query(Subscription).filter(Subscription.status == SubscriptionStatus.CANCELLED).count()
    
    # Revenue metrics
    total_revenue = db.query(Transaction).filter(Transaction.payment_status == PaymentStatus.PAID).with_entities(
        db.func.sum(Transaction.amount)
    ).scalar() or 0
    
    monthly_revenue = db.query(Transaction).filter(
        Transaction.payment_status == PaymentStatus.PAID,
        Transaction.processed_at >= datetime.utcnow() - timedelta(days=30)
    ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
    
    # Plan distribution
    plan_distribution = db.query(Subscription.tier, db.func.count(Subscription.id)).group_by(Subscription.tier).all()
    
    return {
        "total_subscriptions": total_subscriptions,
        "active_subscriptions": active_subscriptions,
        "trial_subscriptions": trial_subscriptions,
        "cancelled_subscriptions": cancelled_subscriptions,
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "plan_distribution": dict(plan_distribution),
        "conversion_rate": (active_subscriptions / (active_subscriptions + cancelled_subscriptions) * 100) if (active_subscriptions + cancelled_subscriptions) > 0 else 0
    }
