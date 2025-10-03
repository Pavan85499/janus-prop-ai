from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio
import json

from core.database import get_db
from models.investment_committee import (
    InvestmentCommittee, CommitteeDebate, InvestmentMemo,
    CommitteeRequest, CommitteeResponse, AgentOpinion,
    CommitteeDebateResponse, InvestmentMemoResponse,
    CommitteeStatus, AgentRole
)
from models.property import Property
from models.agent import Agent
from core.redis_client import publish_event

router = APIRouter()

# Mock AI agent opinions - in production, this would use real AI services
async def get_agent_opinion(agent_role: str, property_data: dict, investment_data: dict) -> dict:
    """Get AI agent opinion based on role"""
    # Simulate AI processing time
    await asyncio.sleep(1)
    
    if agent_role == "chairman":
        return {
            "opinion": "This property presents a compelling investment opportunity with strong fundamentals. The location is prime, and the numbers work well. However, we need to carefully consider the market timing and ensure all due diligence is complete.",
            "score": 78.5,
            "recommendation": "conditional_approval",
            "confidence_level": 0.85,
            "key_points": [
                "Strong location in growing neighborhood",
                "Good cash flow potential",
                "Market timing concerns",
                "Need complete due diligence"
            ]
        }
    elif agent_role == "analyst":
        return {
            "opinion": "Financial analysis shows solid returns with 12.5% IRR and positive cash flow. Cap rate of 6.2% is competitive. However, the property needs significant renovation which could impact short-term returns.",
            "score": 82.0,
            "recommendation": "approve",
            "confidence_level": 0.88,
            "key_points": [
                "12.5% projected IRR",
                "6.2% cap rate",
                "Renovation costs: $45,000",
                "18-month payback period"
            ]
        }
    elif agent_role == "risk_manager":
        return {
            "opinion": "Risk assessment reveals moderate to high risk factors. Market volatility, interest rate sensitivity, and renovation execution risk are concerns. Recommend hedging strategies and contingency planning.",
            "score": 65.0,
            "recommendation": "conditional_approval",
            "confidence_level": 0.92,
            "key_points": [
                "High interest rate sensitivity",
                "Renovation execution risk",
                "Market volatility exposure",
                "Need hedging strategies"
            ]
        }
    elif agent_role == "legal_advisor":
        return {
            "opinion": "Legal review shows clean title with minor HOA restrictions. Zoning is compliant, but permit history needs verification. No major legal impediments, but recommend thorough due diligence.",
            "score": 75.0,
            "recommendation": "approve",
            "confidence_level": 0.90,
            "key_points": [
                "Clean title history",
                "HOA restrictions manageable",
                "Zoning compliant",
                "Verify permit history"
            ]
        }
    elif agent_role == "market_expert":
        return {
            "opinion": "Market analysis indicates strong fundamentals with 5% annual growth. Neighborhood is gentrifying with new developments. Rental demand is high, but competition is increasing. Timing is favorable.",
            "score": 80.0,
            "recommendation": "approve",
            "confidence_level": 0.87,
            "key_points": [
                "5% annual market growth",
                "Gentrifying neighborhood",
                "High rental demand",
                "Increasing competition"
            ]
        }
    elif agent_role == "financial_modeler":
        return {
            "opinion": "Financial models show robust returns across multiple scenarios. Stress testing reveals property remains profitable even in pessimistic conditions. Recommend conservative underwriting assumptions.",
            "score": 85.0,
            "recommendation": "approve",
            "confidence_level": 0.91,
            "key_points": [
                "Robust across scenarios",
                "Strong stress test results",
                "Conservative assumptions",
                "Good downside protection"
            ]
        }
    
    return {
        "opinion": "No specific analysis available",
        "score": 0.0,
        "recommendation": "pending",
        "confidence_level": 0.0,
        "key_points": []
    }

async def generate_investment_memo(committee_id: int, committee_data: dict) -> dict:
    """Generate AI-powered investment memo"""
    # Simulate AI processing time
    await asyncio.sleep(2)
    
    return {
        "memo_title": f"Investment Committee Memo - {committee_data.get('property_address', 'Property')}",
        "executive_summary": f"""
        The Investment Committee recommends {committee_data.get('final_decision', 'APPROVAL')} for the acquisition of {committee_data.get('property_address', 'the subject property')}.
        
        Key Highlights:
        - Projected IRR: {committee_data.get('target_irr', 12.5)}%
        - Cap Rate: {committee_data.get('cap_rate', 6.2)}%
        - Cash Flow: ${committee_data.get('target_cash_flow', 1200):,}/month
        - Risk Score: {committee_data.get('risk_score', 75)}/100
        
        The property presents a compelling investment opportunity with strong fundamentals and manageable risks.
        """,
        "investment_thesis": f"""
        Investment Thesis:
        
        This property represents an attractive value-add opportunity in a rapidly appreciating market. The combination of:
        1. Prime location in a gentrifying neighborhood
        2. Strong rental demand with limited supply
        3. Renovation potential to increase value and rents
        4. Favorable financing terms
        
        Creates a compelling risk-adjusted return profile that aligns with our investment criteria.
        """,
        "property_overview": f"""
        Property Overview:
        
        Address: {committee_data.get('property_address', '123 Main St')}
        Property Type: {committee_data.get('property_type', 'Single Family')}
        Square Footage: {committee_data.get('square_feet', 1800):,} sq ft
        Bedrooms: {committee_data.get('bedrooms', 3)}
        Bathrooms: {committee_data.get('bathrooms', 2.5)}
        Year Built: {committee_data.get('year_built', 1995)}
        Lot Size: {committee_data.get('lot_size', 0.25):.2f} acres
        """,
        "market_analysis": """
        Market Analysis:
        
        The local market shows strong fundamentals with:
        - 5% annual price appreciation over the past 3 years
        - Rental rates increasing 8% year-over-year
        - Low vacancy rates (2.5%)
        - New development driving neighborhood growth
        - Strong job market supporting demand
        
        Market risks include potential interest rate increases and economic headwinds.
        """,
        "financial_analysis": f"""
        Financial Analysis:
        
        Purchase Price: ${committee_data.get('purchase_price', 500000):,}
        Down Payment: ${committee_data.get('down_payment', 100000):,}
        Loan Amount: ${committee_data.get('loan_amount', 400000):,}
        
        Projected Returns:
        - Gross Rental Income: ${committee_data.get('gross_rent', 3000):,}/month
        - Net Operating Income: ${committee_data.get('noi', 2250):,}/month
        - Cash Flow: ${committee_data.get('cash_flow', 1200):,}/month
        - Cap Rate: {committee_data.get('cap_rate', 6.2)}%
        - Cash-on-Cash Return: {committee_data.get('coc_return', 14.4)}%
        - IRR: {committee_data.get('target_irr', 12.5)}%
        """,
        "risk_assessment": """
        Risk Assessment:
        
        Key Risks:
        1. Interest Rate Risk - High sensitivity to rate changes
        2. Market Risk - Potential market correction
        3. Execution Risk - Renovation cost overruns
        4. Liquidity Risk - Limited exit options in downturn
        
        Mitigation Strategies:
        1. Interest rate hedging
        2. Conservative underwriting
        3. Detailed renovation planning
        4. Multiple exit strategies
        """,
        "legal_considerations": """
        Legal Considerations:
        
        - Clean title with no major encumbrances
        - Zoning compliant for intended use
        - HOA restrictions are manageable
        - No environmental issues identified
        - All required permits in place
        
        Recommend final legal review before closing.
        """,
        "recommendations": f"""
        Recommendations:
        
        The Investment Committee recommends {committee_data.get('final_decision', 'APPROVAL')} of this investment with the following conditions:
        
        1. Complete final due diligence
        2. Secure financing at agreed terms
        3. Finalize renovation plans and budget
        4. Execute interest rate hedge
        5. Establish property management plan
        
        Next Steps:
        1. Submit offer within 48 hours
        2. Complete inspection within 7 days
        3. Finalize financing within 14 days
        4. Close within 30 days
        """
    }

async def process_committee_meeting_task(committee_id: int, property_data: dict, investment_data: dict, db: Session):
    """Background task to process committee meeting"""
    try:
        # Update committee status
        committee = db.query(InvestmentCommittee).filter(InvestmentCommittee.id == committee_id).first()
        if not committee:
            return
        
        committee.status = CommitteeStatus.IN_PROGRESS
        committee.started_at = datetime.utcnow()
        db.commit()
        
        # Publish meeting started event
        await publish_event("investment_committee", "meeting_started", {
            "committee_id": committee_id,
            "status": "in_progress"
        })
        
        # Get agent opinions
        agent_roles = ["chairman", "analyst", "risk_manager", "legal_advisor", "market_expert", "financial_modeler"]
        agent_opinions = {}
        
        for role in agent_roles:
            opinion = await get_agent_opinion(role, property_data, investment_data)
            agent_opinions[role] = opinion
            
            # Update committee with agent opinion
            if role == "chairman":
                committee.chairman_opinion = opinion["opinion"]
                committee.chairman_score = opinion["score"]
                committee.chairman_recommendation = opinion["recommendation"]
            elif role == "analyst":
                committee.analyst_opinion = opinion["opinion"]
                committee.analyst_score = opinion["score"]
                committee.analyst_recommendation = opinion["recommendation"]
            elif role == "risk_manager":
                committee.risk_manager_opinion = opinion["opinion"]
                committee.risk_manager_score = opinion["score"]
                committee.risk_manager_recommendation = opinion["recommendation"]
            elif role == "legal_advisor":
                committee.legal_advisor_opinion = opinion["opinion"]
                committee.legal_advisor_score = opinion["score"]
                committee.legal_advisor_recommendation = opinion["recommendation"]
            elif role == "market_expert":
                committee.market_expert_opinion = opinion["opinion"]
                committee.market_expert_score = opinion["score"]
                committee.market_expert_recommendation = opinion["recommendation"]
            elif role == "financial_modeler":
                committee.financial_modeler_opinion = opinion["opinion"]
                committee.financial_modeler_score = opinion["score"]
                committee.financial_modeler_recommendation = opinion["recommendation"]
        
        # Calculate overall scores
        scores = [opinion["score"] for opinion in agent_opinions.values()]
        committee.overall_score = sum(scores) / len(scores) if scores else 0
        
        # Calculate risk and opportunity scores
        risk_scores = [agent_opinions["risk_manager"]["score"], agent_opinions["legal_advisor"]["score"]]
        committee.risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        opportunity_scores = [agent_opinions["analyst"]["score"], agent_opinions["market_expert"]["score"], agent_opinions["financial_modeler"]["score"]]
        committee.opportunity_score = sum(opportunity_scores) / len(opportunity_scores) if opportunity_scores else 0
        
        # Determine overall recommendation
        recommendations = [opinion["recommendation"] for opinion in agent_opinions.values()]
        approve_count = recommendations.count("approve")
        conditional_count = recommendations.count("conditional_approval")
        reject_count = recommendations.count("reject")
        
        if approve_count >= 4:
            committee.overall_recommendation = "approve"
            committee.final_decision = "approve"
        elif conditional_count >= 3 or (approve_count + conditional_count) >= 4:
            committee.overall_recommendation = "conditional_approval"
            committee.final_decision = "conditional_approval"
        else:
            committee.overall_recommendation = "reject"
            committee.final_decision = "reject"
        
        # Generate discussion points and concerns
        committee.discussion_points = [
            "Market timing and interest rate sensitivity",
            "Renovation cost and execution risk",
            "Competition and market saturation",
            "Legal and regulatory compliance",
            "Financial modeling assumptions"
        ]
        
        committee.concerns_raised = [
            "High interest rate sensitivity",
            "Renovation execution risk",
            "Market volatility exposure"
        ]
        
        committee.opportunities_identified = [
            "Strong rental demand",
            "Neighborhood gentrification",
            "Value-add potential",
            "Favorable financing terms"
        ]
        
        if committee.final_decision == "conditional_approval":
            committee.conditions_attached = [
                "Complete final due diligence",
                "Secure financing at agreed terms",
                "Finalize renovation plans",
                "Execute interest rate hedge"
            ]
        
        committee.next_steps = [
            "Submit offer within 48 hours",
            "Complete inspection within 7 days",
            "Finalize financing within 14 days",
            "Close within 30 days"
        ]
        
        # Generate decision rationale
        committee.decision_rationale = f"""
        The Investment Committee has reached a {committee.final_decision.upper()} decision based on the following factors:
        
        Strengths:
        - Strong financial returns with {committee.overall_score:.1f}/100 overall score
        - Good opportunity score of {committee.opportunity_score:.1f}/100
        - Favorable market conditions
        - Clean legal and regulatory status
        
        Concerns:
        - Risk score of {committee.risk_score:.1f}/100 indicates moderate risk
        - Interest rate sensitivity
        - Renovation execution risk
        
        The committee believes the opportunities outweigh the risks, making this a suitable investment for our portfolio.
        """
        
        # Generate investment memo
        memo_data = {
            "property_address": property_data.get("address", "123 Main St"),
            "property_type": property_data.get("property_type", "Single Family"),
            "square_feet": property_data.get("square_feet", 1800),
            "bedrooms": property_data.get("bedrooms", 3),
            "bathrooms": property_data.get("bathrooms", 2.5),
            "year_built": property_data.get("year_built", 1995),
            "lot_size": property_data.get("lot_size", 0.25),
            "purchase_price": investment_data.get("purchase_price", 500000),
            "down_payment": investment_data.get("down_payment", 100000),
            "loan_amount": investment_data.get("loan_amount", 400000),
            "gross_rent": investment_data.get("gross_rent", 3000),
            "noi": investment_data.get("noi", 2250),
            "cash_flow": investment_data.get("cash_flow", 1200),
            "cap_rate": investment_data.get("cap_rate", 6.2),
            "coc_return": investment_data.get("coc_return", 14.4),
            "target_irr": investment_data.get("target_irr", 12.5),
            "risk_score": committee.risk_score,
            "final_decision": committee.final_decision
        }
        
        memo_content = await generate_investment_memo(committee_id, memo_data)
        
        # Create investment memo
        investment_memo = InvestmentMemo(
            committee_id=committee_id,
            memo_title=memo_content["memo_title"],
            executive_summary=memo_content["executive_summary"],
            investment_thesis=memo_content["investment_thesis"],
            property_overview=memo_content["property_overview"],
            market_analysis=memo_content["market_analysis"],
            financial_analysis=memo_content["financial_analysis"],
            risk_assessment=memo_content["risk_assessment"],
            legal_considerations=memo_content["legal_considerations"],
            recommendations=memo_content["recommendations"]
        )
        db.add(investment_memo)
        
        # Update committee with memo content
        committee.investment_memo = memo_content["executive_summary"]
        committee.executive_summary = memo_content["executive_summary"]
        committee.key_risks = committee.concerns_raised
        committee.key_opportunities = committee.opportunities_identified
        
        committee.status = CommitteeStatus.COMPLETED
        committee.completed_at = datetime.utcnow()
        
        db.commit()
        
        # Publish completion event
        await publish_event("investment_committee", "meeting_completed", {
            "committee_id": committee_id,
            "status": "completed",
            "final_decision": committee.final_decision,
            "overall_score": committee.overall_score,
            "risk_score": committee.risk_score,
            "opportunity_score": committee.opportunity_score
        })
        
    except Exception as e:
        # Update committee status to failed
        committee = db.query(InvestmentCommittee).filter(InvestmentCommittee.id == committee_id).first()
        if committee:
            committee.status = CommitteeStatus.FAILED
            db.commit()
        
        await publish_event("investment_committee", "meeting_failed", {
            "committee_id": committee_id,
            "status": "failed",
            "error": str(e)
        })

@router.post("/", response_model=CommitteeResponse)
async def create_investment_committee(
    request: CommitteeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new investment committee meeting"""
    
    # Verify property exists
    property = db.query(Property).filter(Property.id == request.property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get available agents for committee roles
    agents = db.query(Agent).filter(Agent.status == "online").all()
    if len(agents) < 6:
        raise HTTPException(status_code=400, detail="Not enough available agents for committee")
    
    # Assign agents to roles
    chairman = agents[0]
    analyst = agents[1]
    risk_manager = agents[2]
    legal_advisor = agents[3]
    market_expert = agents[4]
    financial_modeler = agents[5]
    
    # Create committee
    committee = InvestmentCommittee(
        property_id=request.property_id,
        committee_name=request.committee_name,
        investment_thesis=request.investment_thesis,
        target_irr=request.target_irr,
        target_cash_flow=request.target_cash_flow,
        target_hold_period=request.target_hold_period,
        risk_tolerance=request.risk_tolerance,
        chairman_id=chairman.id,
        analyst_id=analyst.id,
        risk_manager_id=risk_manager.id,
        legal_advisor_id=legal_advisor.id,
        market_expert_id=market_expert.id,
        financial_modeler_id=financial_modeler.id,
        created_by=1  # In production, get from authenticated user
    )
    
    db.add(committee)
    db.commit()
    db.refresh(committee)
    
    # Prepare data for analysis
    property_data = {
        "address": property.address,
        "city": property.city,
        "state": property.state,
        "property_type": property.property_type,
        "square_feet": property.square_feet,
        "bedrooms": property.bedrooms,
        "bathrooms": property.bathrooms,
        "year_built": property.year_built,
        "lot_size": property.lot_size
    }
    
    investment_data = {
        "purchase_price": request.target_irr or 500000,
        "down_payment": (request.target_irr or 500000) * 0.2,
        "loan_amount": (request.target_irr or 500000) * 0.8,
        "target_irr": request.target_irr or 12.5,
        "target_cash_flow": request.target_cash_flow or 1200,
        "gross_rent": request.target_cash_flow * 2.5 if request.target_cash_flow else 3000,
        "noi": request.target_cash_flow * 1.875 if request.target_cash_flow else 2250,
        "cash_flow": request.target_cash_flow or 1200,
        "cap_rate": 6.2,
        "coc_return": 14.4
    }
    
    # Start background committee meeting
    background_tasks.add_task(
        process_committee_meeting_task,
        committee.id,
        property_data,
        investment_data,
        db
    )
    
    return committee

@router.get("/", response_model=List[CommitteeResponse])
async def get_investment_committees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    property_id: Optional[int] = None,
    status: Optional[CommitteeStatus] = None,
    db: Session = Depends(get_db)
):
    """Get investment committees with filtering"""
    query = db.query(InvestmentCommittee)
    
    if property_id:
        query = query.filter(InvestmentCommittee.property_id == property_id)
    
    if status:
        query = query.filter(InvestmentCommittee.status == status.value)
    
    committees = query.offset(skip).limit(limit).all()
    return committees

@router.get("/{committee_id}", response_model=CommitteeResponse)
async def get_investment_committee(committee_id: int, db: Session = Depends(get_db)):
    """Get a specific investment committee"""
    committee = db.query(InvestmentCommittee).filter(InvestmentCommittee.id == committee_id).first()
    if not committee:
        raise HTTPException(status_code=404, detail="Investment committee not found")
    return committee

@router.get("/{committee_id}/agent-opinions", response_model=List[AgentOpinion])
async def get_agent_opinions(committee_id: int, db: Session = Depends(get_db)):
    """Get all agent opinions for a committee"""
    committee = db.query(InvestmentCommittee).filter(InvestmentCommittee.id == committee_id).first()
    if not committee:
        raise HTTPException(status_code=404, detail="Investment committee not found")
    
    opinions = []
    
    if committee.chairman_opinion:
        opinions.append(AgentOpinion(
            agent_name="Chairman",
            agent_role="chairman",
            opinion=committee.chairman_opinion,
            score=committee.chairman_score or 0,
            recommendation=committee.chairman_recommendation or "pending",
            confidence_level=0.85
        ))
    
    if committee.analyst_opinion:
        opinions.append(AgentOpinion(
            agent_name="Analyst",
            agent_role="analyst",
            opinion=committee.analyst_opinion,
            score=committee.analyst_score or 0,
            recommendation=committee.analyst_recommendation or "pending",
            confidence_level=0.88
        ))
    
    if committee.risk_manager_opinion:
        opinions.append(AgentOpinion(
            agent_name="Risk Manager",
            agent_role="risk_manager",
            opinion=committee.risk_manager_opinion,
            score=committee.risk_manager_score or 0,
            recommendation=committee.risk_manager_recommendation or "pending",
            confidence_level=0.92
        ))
    
    if committee.legal_advisor_opinion:
        opinions.append(AgentOpinion(
            agent_name="Legal Advisor",
            agent_role="legal_advisor",
            opinion=committee.legal_advisor_opinion,
            score=committee.legal_advisor_score or 0,
            recommendation=committee.legal_advisor_recommendation or "pending",
            confidence_level=0.90
        ))
    
    if committee.market_expert_opinion:
        opinions.append(AgentOpinion(
            agent_name="Market Expert",
            agent_role="market_expert",
            opinion=committee.market_expert_opinion,
            score=committee.market_expert_score or 0,
            recommendation=committee.market_expert_recommendation or "pending",
            confidence_level=0.87
        ))
    
    if committee.financial_modeler_opinion:
        opinions.append(AgentOpinion(
            agent_name="Financial Modeler",
            agent_role="financial_modeler",
            opinion=committee.financial_modeler_opinion,
            score=committee.financial_modeler_score or 0,
            recommendation=committee.financial_modeler_recommendation or "pending",
            confidence_level=0.91
        ))
    
    return opinions

@router.get("/{committee_id}/investment-memo", response_model=InvestmentMemoResponse)
async def get_investment_memo(committee_id: int, db: Session = Depends(get_db)):
    """Get the investment memo for a committee"""
    memo = db.query(InvestmentMemo).filter(InvestmentMemo.committee_id == committee_id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="Investment memo not found")
    return memo

@router.post("/{committee_id}/approve")
async def approve_committee_decision(
    committee_id: int,
    approval_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Approve the committee's decision"""
    committee = db.query(InvestmentCommittee).filter(InvestmentCommittee.id == committee_id).first()
    if not committee:
        raise HTTPException(status_code=404, detail="Investment committee not found")
    
    if committee.status != CommitteeStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Committee meeting must be completed before approval")
    
    committee.approved_at = datetime.utcnow()
    committee.approved_by = 1  # In production, get from authenticated user
    
    db.commit()
    
    await publish_event("investment_committee", "decision_approved", {
        "committee_id": committee_id,
        "final_decision": committee.final_decision,
        "approved_at": committee.approved_at.isoformat()
    })
    
    return {"message": "Committee decision approved successfully"}

@router.get("/stats/")
async def get_committee_stats(db: Session = Depends(get_db)):
    """Get investment committee statistics"""
    total_committees = db.query(InvestmentCommittee).count()
    completed_committees = db.query(InvestmentCommittee).filter(InvestmentCommittee.status == CommitteeStatus.COMPLETED).count()
    approved_decisions = db.query(InvestmentCommittee).filter(InvestmentCommittee.final_decision == "approve").count()
    conditional_decisions = db.query(InvestmentCommittee).filter(InvestmentCommittee.final_decision == "conditional_approval").count()
    rejected_decisions = db.query(InvestmentCommittee).filter(InvestmentCommittee.final_decision == "reject").count()
    
    # Calculate average scores
    committees_with_scores = db.query(InvestmentCommittee).filter(InvestmentCommittee.overall_score.isnot(None)).all()
    avg_overall_score = sum(c.overall_score for c in committees_with_scores) / len(committees_with_scores) if committees_with_scores else 0
    avg_risk_score = sum(c.risk_score for c in committees_with_scores if c.risk_score) / len([c for c in committees_with_scores if c.risk_score]) if committees_with_scores else 0
    avg_opportunity_score = sum(c.opportunity_score for c in committees_with_scores if c.opportunity_score) / len([c for c in committees_with_scores if c.opportunity_score]) if committees_with_scores else 0
    
    return {
        "total_committees": total_committees,
        "completed_committees": completed_committees,
        "approved_decisions": approved_decisions,
        "conditional_decisions": conditional_decisions,
        "rejected_decisions": rejected_decisions,
        "approval_rate": (approved_decisions / completed_committees * 100) if completed_committees > 0 else 0,
        "avg_overall_score": round(avg_overall_score, 1),
        "avg_risk_score": round(avg_risk_score, 1),
        "avg_opportunity_score": round(avg_opportunity_score, 1)
    }
