from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import json
import uuid

from core.database import get_db
from models.execution_closing import (
    DealExecution, OwnerContact, OfferLetter, Contract, Lender, FinancingApplication,
    DealExecutionRequest, DealExecutionResponse, OwnerContactRequest, OfferLetterResponse,
    ContractResponse, FinancingApplicationRequest, DealStatus, OfferType, ContactMethod
)
from models.property import Property
from core.redis_client import publish_event

router = APIRouter()

# Mock AI analysis for execution and closing
async def analyze_deal_success_probability(deal_data: dict) -> dict:
    """AI analysis of deal success probability"""
    await asyncio.sleep(1)
    
    # Mock analysis based on deal factors
    base_probability = 75.0
    
    # Adjust based on offer price vs market value
    if deal_data.get("offer_price", 0) > deal_data.get("market_value", 0) * 0.95:
        base_probability += 10
    elif deal_data.get("offer_price", 0) < deal_data.get("market_value", 0) * 0.90:
        base_probability -= 15
    
    # Adjust based on financing
    if deal_data.get("offer_type") == "cash":
        base_probability += 15
    elif deal_data.get("offer_type") == "financed":
        base_probability += 5
    
    # Adjust based on market conditions
    if deal_data.get("market_conditions") == "hot":
        base_probability -= 10
    elif deal_data.get("market_conditions") == "cold":
        base_probability += 10
    
    # Ensure probability is between 0 and 100
    probability = max(0, min(100, base_probability))
    
    return {
        "success_probability": probability,
        "risk_factors": [
            "Market competition",
            "Financing contingency",
            "Inspection results",
            "Appraisal value"
        ],
        "success_factors": [
            "Strong offer price",
            "Quick closing timeline",
            "Minimal contingencies",
            "Pre-approved financing"
        ],
        "ai_analysis": f"Deal shows {probability}% success probability based on current market conditions and offer terms.",
        "recommendations": [
            "Submit offer quickly to avoid competition",
            "Consider increasing earnest money",
            "Prepare for potential counter-offers",
            "Have financing pre-approved"
        ]
    }

async def generate_offer_letter(deal_data: dict) -> dict:
    """AI-generated offer letter"""
    await asyncio.sleep(1)
    
    return {
        "letter_title": f"Purchase Offer - {deal_data.get('property_address', 'Property')}",
        "letter_content": f"""
Dear {deal_data.get('seller_name', 'Property Owner')},

I am writing to submit a formal offer to purchase your property located at {deal_data.get('property_address', 'Property Address')}.

OFFER DETAILS:
• Purchase Price: ${deal_data.get('offer_price', 0):,}
• Earnest Money: ${deal_data.get('earnest_money', 0):,}
• Down Payment: ${deal_data.get('down_payment', 0):,}
• Loan Amount: ${deal_data.get('loan_amount', 0):,}
• Closing Date: {deal_data.get('closing_date', 'TBD')}
• Inspection Period: {deal_data.get('inspection_period_days', 10)} days
• Financing Contingency: {deal_data.get('financing_contingency_days', 21)} days

TERMS AND CONDITIONS:
• This offer is contingent upon satisfactory inspection
• Financing approval required
• Appraisal must meet or exceed purchase price
• Title search and insurance required

I am prepared to move quickly and have financing pre-approved. I believe this offer reflects fair market value and provides a smooth transaction for all parties.

Please let me know if you have any questions or would like to discuss any terms.

Best regards,
{deal_data.get('buyer_name', 'Buyer')}
        """,
        "ai_analysis": "Offer letter generated with professional tone and comprehensive terms. Includes all standard contingencies and demonstrates buyer's seriousness."
    }

async def generate_contract(deal_data: dict) -> dict:
    """AI-generated purchase contract"""
    await asyncio.sleep(1)
    
    return {
        "contract_title": f"Purchase and Sale Agreement - {deal_data.get('property_address', 'Property')}",
        "contract_content": f"""
PURCHASE AND SALE AGREEMENT

This Purchase and Sale Agreement ("Agreement") is entered into on {datetime.now().strftime('%B %d, %Y')} between:

SELLER: {deal_data.get('seller_name', 'Property Owner')}
BUYER: {deal_data.get('buyer_name', 'Buyer')}
PROPERTY: {deal_data.get('property_address', 'Property Address')}

PURCHASE PRICE: ${deal_data.get('offer_price', 0):,}
EARNEST MONEY: ${deal_data.get('earnest_money', 0):,}
CLOSING DATE: {deal_data.get('closing_date', 'TBD')}

TERMS AND CONDITIONS:
1. Purchase Price: ${deal_data.get('offer_price', 0):,}
2. Earnest Money: ${deal_data.get('earnest_money', 0):,} to be held in escrow
3. Down Payment: ${deal_data.get('down_payment', 0):,}
4. Financing: Buyer to obtain financing in the amount of ${deal_data.get('loan_amount', 0):,}
5. Inspection Period: {deal_data.get('inspection_period_days', 10)} days from contract execution
6. Financing Contingency: {deal_data.get('financing_contingency_days', 21)} days from contract execution
7. Appraisal Contingency: {deal_data.get('appraisal_contingency_days', 14)} days from contract execution

CONTINGENCIES:
- Satisfactory inspection of the property
- Financing approval
- Appraisal meeting or exceeding purchase price
- Clear title
- No material adverse changes to property

CLOSING:
Closing shall occur on or before {deal_data.get('closing_date', 'TBD')} at a location mutually agreed upon by the parties.

DEFAULT:
If either party defaults, the non-defaulting party may seek specific performance or damages.

This Agreement constitutes the entire agreement between the parties and supersedes all prior negotiations.

SELLER: _________________________ DATE: _________
BUYER: _________________________ DATE: _________
        """,
        "ai_analysis": "Contract generated with standard real estate terms and comprehensive contingencies. Includes all necessary legal protections for both parties."
    }

async def analyze_financing_application(application_data: dict) -> dict:
    """AI analysis of financing application"""
    await asyncio.sleep(1)
    
    # Mock analysis based on borrower profile
    credit_score = application_data.get("credit_score", 0)
    dti_ratio = application_data.get("debt_to_income_ratio", 0)
    loan_amount = application_data.get("loan_amount", 0)
    down_payment = application_data.get("down_payment", 0)
    
    approval_probability = 80.0
    
    # Adjust based on credit score
    if credit_score >= 740:
        approval_probability += 15
    elif credit_score >= 680:
        approval_probability += 5
    elif credit_score < 620:
        approval_probability -= 25
    
    # Adjust based on DTI ratio
    if dti_ratio <= 36:
        approval_probability += 10
    elif dti_ratio <= 43:
        approval_probability += 5
    elif dti_ratio > 50:
        approval_probability -= 20
    
    # Adjust based on down payment
    down_payment_percentage = (down_payment / loan_amount) * 100 if loan_amount > 0 else 0
    if down_payment_percentage >= 20:
        approval_probability += 10
    elif down_payment_percentage >= 10:
        approval_probability += 5
    elif down_payment_percentage < 5:
        approval_probability -= 15
    
    approval_probability = max(0, min(100, approval_probability))
    
    return {
        "approval_probability": approval_probability,
        "risk_factors": [
            "Credit score below 680" if credit_score < 680 else None,
            "High debt-to-income ratio" if dti_ratio > 43 else None,
            "Low down payment" if down_payment_percentage < 10 else None,
            "High loan amount" if loan_amount > 800000 else None
        ],
        "strengths": [
            "Strong credit score" if credit_score >= 740 else None,
            "Low debt-to-income ratio" if dti_ratio <= 36 else None,
            "High down payment" if down_payment_percentage >= 20 else None,
            "Stable income" if application_data.get("annual_income", 0) > 100000 else None
        ],
        "ai_analysis": f"Financing application shows {approval_probability}% approval probability. {'Strong application' if approval_probability >= 80 else 'Moderate risk' if approval_probability >= 60 else 'High risk'}.",
        "recommendations": [
            "Consider increasing down payment" if down_payment_percentage < 20 else None,
            "Improve credit score before applying" if credit_score < 680 else None,
            "Reduce debt-to-income ratio" if dti_ratio > 43 else None,
            "Consider co-signer" if approval_probability < 70 else None
        ]
    }

@router.post("/deals", response_model=DealExecutionResponse)
async def create_deal_execution(
    request: DealExecutionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new deal execution"""
    
    # Verify property exists
    property = db.query(Property).filter(Property.id == request.property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Create deal execution
    deal = DealExecution(
        property_id=request.property_id,
        deal_name=request.deal_name,
        offer_type=request.offer_type.value,
        offer_price=request.offer_price,
        earnest_money=request.earnest_money,
        down_payment=request.down_payment,
        loan_amount=request.loan_amount,
        interest_rate=request.interest_rate,
        loan_term=request.loan_term,
        closing_date=request.closing_date,
        inspection_period_days=request.inspection_period_days,
        financing_contingency_days=request.financing_contingency_days,
        contingencies=request.contingencies or [],
        special_terms=request.special_terms,
        created_by=1  # In production, get from authenticated user
    )
    
    db.add(deal)
    db.commit()
    db.refresh(deal)
    
    # Prepare data for AI analysis
    deal_data = {
        "offer_price": request.offer_price,
        "market_value": property.estimated_value or request.offer_price,
        "offer_type": request.offer_type.value,
        "market_conditions": "moderate",  # In production, get from market data
        "property_address": property.address
    }
    
    # Start background AI analysis
    background_tasks.add_task(
        analyze_deal_success_probability,
        deal_data
    )
    
    return deal

@router.get("/deals", response_model=List[DealExecutionResponse])
async def get_deal_executions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: Optional[int] = None,
    status: Optional[DealStatus] = None,
    db: Session = Depends(get_db)
):
    """Get deal executions with filtering"""
    query = db.query(DealExecution)
    
    if property_id:
        query = query.filter(DealExecution.property_id == property_id)
    
    if status:
        query = query.filter(DealExecution.status == status.value)
    
    deals = query.offset(skip).limit(limit).all()
    return deals

@router.get("/deals/{deal_id}", response_model=DealExecutionResponse)
async def get_deal_execution(deal_id: int, db: Session = Depends(get_db)):
    """Get a specific deal execution"""
    deal = db.query(DealExecution).filter(DealExecution.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal execution not found")
    return deal

@router.post("/deals/{deal_id}/submit-offer")
async def submit_offer(
    deal_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit offer for a deal"""
    deal = db.query(DealExecution).filter(DealExecution.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal execution not found")
    
    if deal.status != DealStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Deal must be in draft status to submit offer")
    
    # Update deal status
    deal.status = DealStatus.OFFER_SUBMITTED
    deal.offer_submitted_at = datetime.utcnow()
    db.commit()
    
    # Generate offer letter
    deal_data = {
        "property_address": deal.property.address if deal.property else "Property Address",
        "seller_name": deal.seller_name or "Property Owner",
        "buyer_name": "Buyer",  # In production, get from user profile
        "offer_price": deal.offer_price,
        "earnest_money": deal.earnest_money,
        "down_payment": deal.down_payment,
        "loan_amount": deal.loan_amount,
        "closing_date": deal.closing_date.isoformat() if deal.closing_date else "TBD",
        "inspection_period_days": deal.inspection_period_days,
        "financing_contingency_days": deal.financing_contingency_days
    }
    
    # Generate offer letter
    offer_letter_data = await generate_offer_letter(deal_data)
    
    # Create offer letter record
    offer_letter = OfferLetter(
        deal_id=deal_id,
        letter_title=offer_letter_data["letter_title"],
        letter_content=offer_letter_data["letter_content"],
        letter_type="initial_offer",
        offer_price=deal.offer_price,
        earnest_money=deal.earnest_money,
        closing_date=deal.closing_date,
        contingencies=deal.contingencies,
        special_terms=deal.special_terms,
        status="sent",
        sent_at=datetime.utcnow(),
        created_by=1
    )
    db.add(offer_letter)
    db.commit()
    
    await publish_event("execution_closing", "offer_submitted", {
        "deal_id": deal_id,
        "status": "offer_submitted",
        "offer_price": deal.offer_price
    })
    
    return {"message": "Offer submitted successfully", "offer_letter_id": offer_letter.id}

@router.post("/deals/{deal_id}/contact-owner", response_model=dict)
async def contact_property_owner(
    deal_id: int,
    request: OwnerContactRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Contact property owner"""
    deal = db.query(DealExecution).filter(DealExecution.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal execution not found")
    
    # Create contact record
    contact = OwnerContact(
        deal_id=deal_id,
        contact_method=request.contact_method.value,
        contact_date=datetime.utcnow(),
        subject=request.subject,
        message=request.message,
        follow_up_required=request.follow_up_required,
        follow_up_date=request.follow_up_date,
        created_by=1
    )
    db.add(contact)
    db.commit()
    
    # AI analysis of contact
    contact_data = {
        "message": request.message,
        "subject": request.subject,
        "contact_method": request.contact_method.value
    }
    
    # Simulate AI analysis
    ai_analysis = {
        "sentiment_score": 0.7,  # Mock sentiment analysis
        "ai_analysis": "Message shows professional tone and clear intent. Good chance of positive response.",
        "ai_recommendations": [
            "Follow up within 24-48 hours if no response",
            "Consider adjusting offer terms if initial response is negative",
            "Maintain professional communication throughout"
        ]
    }
    
    contact.ai_sentiment_score = ai_analysis["sentiment_score"]
    contact.ai_analysis = ai_analysis["ai_analysis"]
    contact.ai_recommendations = ai_analysis["ai_recommendations"]
    db.commit()
    
    await publish_event("execution_closing", "owner_contacted", {
        "deal_id": deal_id,
        "contact_method": request.contact_method.value,
        "subject": request.subject
    })
    
    return {"message": "Property owner contacted successfully", "contact_id": contact.id}

@router.get("/deals/{deal_id}/offer-letters", response_model=List[OfferLetterResponse])
async def get_offer_letters(deal_id: int, db: Session = Depends(get_db)):
    """Get offer letters for a deal"""
    offer_letters = db.query(OfferLetter).filter(OfferLetter.deal_id == deal_id).all()
    return offer_letters

@router.post("/deals/{deal_id}/generate-contract", response_model=ContractResponse)
async def generate_contract(
    deal_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate purchase contract for a deal"""
    deal = db.query(DealExecution).filter(DealExecution.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal execution not found")
    
    if deal.status not in [DealStatus.ACCEPTED, DealStatus.UNDER_CONTRACT]:
        raise HTTPException(status_code=400, detail="Deal must be accepted or under contract to generate contract")
    
    # Prepare contract data
    contract_data = {
        "property_address": deal.property.address if deal.property else "Property Address",
        "seller_name": deal.seller_name or "Property Owner",
        "buyer_name": "Buyer",  # In production, get from user profile
        "offer_price": deal.offer_price,
        "earnest_money": deal.earnest_money,
        "down_payment": deal.down_payment,
        "loan_amount": deal.loan_amount,
        "closing_date": deal.closing_date.isoformat() if deal.closing_date else "TBD",
        "inspection_period_days": deal.inspection_period_days,
        "financing_contingency_days": deal.financing_contingency_days,
        "appraisal_contingency_days": deal.appraisal_contingency_days
    }
    
    # Generate contract
    contract_content = await generate_contract(contract_data)
    
    # Create contract record
    contract = Contract(
        deal_id=deal_id,
        contract_title=contract_content["contract_title"],
        contract_type="purchase_agreement",
        contract_content=contract_content["contract_content"],
        buyer_name="Buyer",  # In production, get from user profile
        buyer_email="buyer@email.com",  # In production, get from user profile
        seller_name=deal.seller_name or "Property Owner",
        seller_email=deal.seller_email or "seller@email.com",
        purchase_price=deal.offer_price,
        earnest_money=deal.earnest_money,
        closing_date=deal.closing_date,
        contingencies=deal.contingencies,
        special_provisions=deal.special_terms,
        status="draft",
        created_by=1
    )
    db.add(contract)
    db.commit()
    
    return contract

@router.get("/lenders", response_model=List[dict])
async def get_lenders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    lender_type: Optional[str] = None,
    is_preferred: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get available lenders"""
    query = db.query(Lender).filter(Lender.is_active == True)
    
    if lender_type:
        query = query.filter(Lender.lender_type == lender_type)
    
    if is_preferred is not None:
        query = query.filter(Lender.is_preferred == is_preferred)
    
    lenders = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": lender.id,
            "lender_name": lender.lender_name,
            "lender_type": lender.lender_type,
            "contact_person": lender.contact_person,
            "email": lender.email,
            "phone": lender.phone,
            "website": lender.website,
            "interest_rates": lender.interest_rates,
            "loan_terms": lender.loan_terms,
            "minimum_down_payment": lender.minimum_down_payment,
            "maximum_loan_amount": lender.maximum_loan_amount,
            "credit_score_minimum": lender.credit_score_minimum,
            "is_preferred": lender.is_preferred,
            "rating": lender.rating
        }
        for lender in lenders
    ]

@router.post("/deals/{deal_id}/apply-financing", response_model=dict)
async def apply_for_financing(
    deal_id: int,
    request: FinancingApplicationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Apply for financing for a deal"""
    deal = db.query(DealExecution).filter(DealExecution.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal execution not found")
    
    lender = db.query(Lender).filter(Lender.id == request.lender_id).first()
    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")
    
    # Generate application number
    application_number = f"APP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Create financing application
    application = FinancingApplication(
        deal_id=deal_id,
        lender_id=request.lender_id,
        application_number=application_number,
        loan_amount=request.loan_amount,
        down_payment=request.down_payment,
        interest_rate=request.interest_rate,
        loan_term=request.loan_term,
        borrower_name=request.borrower_name,
        borrower_email=request.borrower_email,
        borrower_phone=request.borrower_phone,
        credit_score=request.credit_score,
        annual_income=request.annual_income,
        debt_to_income_ratio=request.annual_income / (request.loan_amount * 12) if request.loan_amount > 0 else 0,
        property_address=deal.property.address if deal.property else "Property Address",
        property_value=deal.offer_price,
        property_type=deal.property.property_type if deal.property else "Single Family",
        status="submitted",
        created_by=1
    )
    db.add(application)
    db.commit()
    
    # AI analysis of application
    application_data = {
        "credit_score": request.credit_score,
        "debt_to_income_ratio": application.debt_to_income_ratio,
        "loan_amount": request.loan_amount,
        "down_payment": request.down_payment,
        "annual_income": request.annual_income
    }
    
    ai_analysis = await analyze_financing_application(application_data)
    
    application.ai_analysis = ai_analysis["ai_analysis"]
    application.approval_probability = ai_analysis["approval_probability"]
    application.ai_recommendations = ai_analysis["recommendations"]
    db.commit()
    
    await publish_event("execution_closing", "financing_applied", {
        "deal_id": deal_id,
        "application_number": application_number,
        "lender_id": request.lender_id,
        "approval_probability": ai_analysis["approval_probability"]
    })
    
    return {
        "message": "Financing application submitted successfully",
        "application_number": application_number,
        "approval_probability": ai_analysis["approval_probability"]
    }

@router.get("/deals/{deal_id}/financing-applications", response_model=List[dict])
async def get_financing_applications(deal_id: int, db: Session = Depends(get_db)):
    """Get financing applications for a deal"""
    applications = db.query(FinancingApplication).filter(FinancingApplication.deal_id == deal_id).all()
    
    return [
        {
            "id": app.id,
            "application_number": app.application_number,
            "lender_name": app.lender.lender_name if app.lender else "Unknown",
            "loan_amount": app.loan_amount,
            "down_payment": app.down_payment,
            "interest_rate": app.interest_rate,
            "loan_term": app.loan_term,
            "status": app.status,
            "approval_probability": app.approval_probability,
            "submitted_at": app.submitted_at,
            "approved_at": app.approved_at
        }
        for app in applications
    ]

@router.get("/stats/")
async def get_execution_stats(db: Session = Depends(get_db)):
    """Get execution and closing statistics"""
    total_deals = db.query(DealExecution).count()
    active_deals = db.query(DealExecution).filter(DealExecution.status.in_([
        DealStatus.OFFER_SUBMITTED, DealStatus.UNDER_REVIEW, DealStatus.NEGOTIATING,
        DealStatus.UNDER_CONTRACT, DealStatus.INSPECTION, DealStatus.APPRAISAL,
        DealStatus.FINANCING, DealStatus.CLOSING
    ])).count()
    closed_deals = db.query(DealExecution).filter(DealExecution.status == DealStatus.CLOSED).count()
    cancelled_deals = db.query(DealExecution).filter(DealExecution.status == DealStatus.CANCELLED).count()
    
    # Calculate average success probability
    deals_with_probability = db.query(DealExecution).filter(DealExecution.success_probability.isnot(None)).all()
    avg_success_probability = sum(d.success_probability for d in deals_with_probability) / len(deals_with_probability) if deals_with_probability else 0
    
    # Financing applications
    total_applications = db.query(FinancingApplication).count()
    approved_applications = db.query(FinancingApplication).filter(FinancingApplication.status == "approved").count()
    
    return {
        "total_deals": total_deals,
        "active_deals": active_deals,
        "closed_deals": closed_deals,
        "cancelled_deals": cancelled_deals,
        "success_rate": (closed_deals / total_deals * 100) if total_deals > 0 else 0,
        "avg_success_probability": round(avg_success_probability, 1),
        "total_financing_applications": total_applications,
        "approved_financing_applications": approved_applications,
        "financing_approval_rate": (approved_applications / total_applications * 100) if total_applications > 0 else 0
    }
