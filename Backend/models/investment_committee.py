from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

Base = declarative_base()

class CommitteeStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVED = "approved"
    REJECTED = "rejected"

class AgentRole(str, Enum):
    CHAIRMAN = "chairman"
    ANALYST = "analyst"
    RISK_MANAGER = "risk_manager"
    LEGAL_ADVISOR = "legal_advisor"
    MARKET_EXPERT = "market_expert"
    FINANCIAL_MODELER = "financial_modeler"

class InvestmentCommittee(Base):
    __tablename__ = "investment_committees"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Property Reference
    property_id = Column(Integer, ForeignKey("properties.id"))
    property = relationship("Property", back_populates="investment_committees")
    
    # Committee Details
    committee_name = Column(String(255), nullable=False)
    status = Column(String(50), default=CommitteeStatus.PENDING)
    
    # Investment Analysis
    investment_thesis = Column(Text)
    target_irr = Column(Float)
    target_cash_flow = Column(Float)
    target_hold_period = Column(Integer)  # Years
    risk_tolerance = Column(String(50))  # conservative, moderate, aggressive
    
    # Committee Members (AI Agents)
    chairman_id = Column(Integer, ForeignKey("agents.id"))
    chairman = relationship("Agent", foreign_keys=[chairman_id])
    
    analyst_id = Column(Integer, ForeignKey("agents.id"))
    analyst = relationship("Agent", foreign_keys=[analyst_id])
    
    risk_manager_id = Column(Integer, ForeignKey("agents.id"))
    risk_manager = relationship("Agent", foreign_keys=[risk_manager_id])
    
    legal_advisor_id = Column(Integer, ForeignKey("agents.id"))
    legal_advisor = relationship("Agent", foreign_keys=[legal_advisor_id])
    
    market_expert_id = Column(Integer, ForeignKey("agents.id"))
    market_expert = relationship("Agent", foreign_keys=[market_expert_id])
    
    financial_modeler_id = Column(Integer, ForeignKey("agents.id"))
    financial_modeler = relationship("Agent", foreign_keys=[financial_modeler_id])
    
    # Committee Analysis
    overall_recommendation = Column(String(50))  # approve, reject, conditional_approval
    overall_score = Column(Float)  # 0-100
    risk_score = Column(Float)  # 0-100
    opportunity_score = Column(Float)  # 0-100
    
    # Individual Agent Opinions
    chairman_opinion = Column(Text)
    chairman_score = Column(Float)
    chairman_recommendation = Column(String(50))
    
    analyst_opinion = Column(Text)
    analyst_score = Column(Float)
    analyst_recommendation = Column(String(50))
    
    risk_manager_opinion = Column(Text)
    risk_manager_score = Column(Float)
    risk_manager_recommendation = Column(String(50))
    
    legal_advisor_opinion = Column(Text)
    legal_advisor_score = Column(Float)
    legal_advisor_recommendation = Column(String(50))
    
    market_expert_opinion = Column(Text)
    market_expert_score = Column(Float)
    market_expert_recommendation = Column(String(50))
    
    financial_modeler_opinion = Column(Text)
    financial_modeler_score = Column(Float)
    financial_modeler_recommendation = Column(String(50))
    
    # Committee Discussion
    discussion_points = Column(JSON)  # Key discussion topics
    concerns_raised = Column(JSON)  # Concerns raised by committee members
    opportunities_identified = Column(JSON)  # Opportunities identified
    conditions_attached = Column(JSON)  # Conditions for approval
    
    # Final Decision
    final_decision = Column(String(50))  # approve, reject, conditional_approval
    decision_rationale = Column(Text)
    conditions = Column(JSON)  # Conditions for approval
    next_steps = Column(JSON)  # Recommended next steps
    
    # Investment Memo
    investment_memo = Column(Text)  # Generated investment memo
    executive_summary = Column(Text)
    key_risks = Column(JSON)
    key_opportunities = Column(JSON)
    financial_projections = Column(JSON)
    market_analysis = Column(JSON)
    legal_considerations = Column(JSON)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    approved_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey("users.id"))

class CommitteeDebate(Base):
    __tablename__ = "committee_debates"
    
    id = Column(Integer, primary_key=True, index=True)
    committee_id = Column(Integer, ForeignKey("investment_committees.id"))
    committee = relationship("InvestmentCommittee", back_populates="debates")
    
    # Debate Details
    topic = Column(String(255), nullable=False)
    round_number = Column(Integer, default=1)
    
    # Participants
    speaker_agent_id = Column(Integer, ForeignKey("agents.id"))
    speaker_agent = relationship("Agent", foreign_keys=[speaker_agent_id])
    
    # Debate Content
    position = Column(String(50))  # pro, con, neutral
    argument = Column(Text, nullable=False)
    supporting_data = Column(JSON)
    confidence_level = Column(Float)  # 0-1
    
    # Response to Previous Arguments
    responding_to_agent_id = Column(Integer, ForeignKey("agents.id"))
    responding_to_agent = relationship("Agent", foreign_keys=[responding_to_agent_id])
    counter_argument = Column(Text)
    
    # Debate Outcome
    argument_strength = Column(Float)  # 0-1
    persuasiveness_score = Column(Float)  # 0-1
    consensus_reached = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

class InvestmentMemo(Base):
    __tablename__ = "investment_memos"
    
    id = Column(Integer, primary_key=True, index=True)
    committee_id = Column(Integer, ForeignKey("investment_committees.id"))
    committee = relationship("InvestmentCommittee", back_populates="investment_memos")
    
    # Memo Details
    memo_title = Column(String(255), nullable=False)
    memo_version = Column(Integer, default=1)
    
    # Memo Content
    executive_summary = Column(Text)
    investment_thesis = Column(Text)
    property_overview = Column(Text)
    market_analysis = Column(Text)
    financial_analysis = Column(Text)
    risk_assessment = Column(Text)
    legal_considerations = Column(Text)
    recommendations = Column(Text)
    appendices = Column(JSON)
    
    # AI Generation
    ai_generated = Column(Boolean, default=True)
    generation_prompt = Column(Text)
    generation_parameters = Column(JSON)
    
    # Review Process
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    review_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models for API
class CommitteeRequest(BaseModel):
    property_id: int
    committee_name: str
    investment_thesis: str
    target_irr: Optional[float] = None
    target_cash_flow: Optional[float] = None
    target_hold_period: int = 5
    risk_tolerance: str = "moderate"

class CommitteeResponse(BaseModel):
    id: int
    property_id: int
    committee_name: str
    status: str
    overall_recommendation: Optional[str]
    overall_score: Optional[float]
    risk_score: Optional[float]
    opportunity_score: Optional[float]
    final_decision: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class AgentOpinion(BaseModel):
    agent_name: str
    agent_role: str
    opinion: str
    score: float
    recommendation: str
    confidence_level: float

class CommitteeDebateResponse(BaseModel):
    id: int
    topic: str
    round_number: int
    speaker_agent: str
    position: str
    argument: str
    supporting_data: Optional[Dict[str, Any]]
    confidence_level: float
    argument_strength: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class InvestmentMemoResponse(BaseModel):
    id: int
    memo_title: str
    memo_version: int
    executive_summary: str
    investment_thesis: str
    property_overview: str
    market_analysis: str
    financial_analysis: str
    risk_assessment: str
    legal_considerations: str
    recommendations: str
    ai_generated: bool
    reviewed: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Add relationships to existing models
InvestmentCommittee.debates = relationship("CommitteeDebate", back_populates="committee")
InvestmentCommittee.investment_memos = relationship("InvestmentMemo", back_populates="committee")
