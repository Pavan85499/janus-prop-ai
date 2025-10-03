"""
AI Investment Committee Agent for Janus Prop AI Backend

This agent creates a panel of AI agents that debates pros and cons,
surfacing risks and opportunities to produce in-depth investment memos.
"""

import asyncio
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
from dataclasses import dataclass
from enum import Enum

try:
    import google.generativeai as genai
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from config.settings import get_settings
from core.redis_client import cache_get, cache_set, publish_event
from core.websocket_manager import get_websocket_manager

logger = structlog.get_logger(__name__)

class CommitteeDecision(Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    PASS = "pass"
    AVOID = "avoid"

class CommitteeMemberRole(Enum):
    FINANCIAL_ANALYST = "financial_analyst"
    MARKET_ANALYST = "market_analyst"
    LEGAL_EXPERT = "legal_expert"
    CONSTRUCTION_EXPERT = "construction_expert"
    RISK_MANAGER = "risk_manager"

@dataclass
class CommitteeMember:
    """Individual committee member with specialized expertise."""
    member_id: str
    name: str
    role: CommitteeMemberRole
    expertise: List[str]
    risk_tolerance: str  # "conservative", "moderate", "aggressive"
    voting_weight: float
    personality_traits: List[str]

@dataclass
class MemberOpinion:
    """Opinion from a committee member."""
    member_id: str
    member_name: str
    recommendation: CommitteeDecision
    confidence_level: float
    reasoning: str
    key_concerns: List[str]
    opportunities_identified: List[str]
    risk_assessment: str
    financial_projections: Dict[str, float]
    supporting_evidence: List[str]

@dataclass
class DebateRound:
    """Single round of committee debate."""
    round_number: int
    topic: str
    member_statements: List[Dict[str, Any]]
    consensus_points: List[str]
    disagreement_points: List[str]
    new_insights: List[str]

@dataclass
class InvestmentMemo:
    """Comprehensive investment committee memo."""
    property_id: str
    property_address: str
    memo_date: datetime
    committee_decision: CommitteeDecision
    decision_confidence: float
    unanimous_decision: bool
    voting_breakdown: Dict[str, str]
    
    # Analysis sections
    executive_summary: str
    property_overview: Dict[str, Any]
    financial_analysis: Dict[str, Any]
    market_analysis: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    legal_considerations: Dict[str, Any]
    
    # Committee insights
    member_opinions: List[MemberOpinion]
    debate_summary: List[DebateRound]
    consensus_points: List[str]
    key_risks: List[str]
    key_opportunities: List[str]
    
    # Recommendations
    investment_recommendation: str
    suggested_offer_price: Optional[float]
    financing_recommendations: List[str]
    due_diligence_priorities: List[str]
    exit_strategy_options: List[str]
    
    # Supporting data
    comparable_deals: List[Dict[str, Any]]
    sensitivity_analysis: Dict[str, Any]
    stress_test_results: Dict[str, Any]

class AIInvestmentCommitteeAgent:
    """AI Investment Committee Agent that simulates expert panel discussions."""
    
    def __init__(self):
        self.agent_id = "ai_investment_committee_agent"
        self.name = "AI Investment Committee Agent"
        self.settings = get_settings()
        self.gemini_api_key = self.settings.GEMINI_API_KEY
        self.is_initialized = False
        
        # Initialize committee members
        self.committee_members = self._initialize_committee_members()
        
        # Debate configuration
        self.debate_rounds = 3
        self.consensus_threshold = 0.7
        self.decision_threshold = 0.6
        
        if self._has_required_libraries():
            self._initialize_agent()
    
    def _has_required_libraries(self) -> bool:
        """Check if required libraries are available."""
        return bool(self.gemini_api_key)
    
    def _initialize_agent(self):
        """Initialize the AI investment committee agent."""
        try:
            if GEMINI_AVAILABLE and self.gemini_api_key:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel("gemini-pro")
                self.chat_model = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.gemini_api_key,
                    temperature=0.7,  # Allow for diverse perspectives
                    max_output_tokens=4096
                )
            
            self.is_initialized = True
            logger.info("AI Investment Committee Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Investment Committee Agent: {e}")
            self.is_initialized = False
    
    def _initialize_committee_members(self) -> List[CommitteeMember]:
        """Initialize the investment committee members."""
        return [
            CommitteeMember(
                member_id="financial_analyst_1",
                name="Alexandra Chen",
                role=CommitteeMemberRole.FINANCIAL_ANALYST,
                expertise=["cash_flow_analysis", "cap_rates", "ROI_calculations", "financing_structures"],
                risk_tolerance="conservative",
                voting_weight=1.2,
                personality_traits=["detail_oriented", "analytical", "cautious"]
            ),
            CommitteeMember(
                member_id="market_analyst_1",
                name="Marcus Rodriguez",
                role=CommitteeMemberRole.MARKET_ANALYST,
                expertise=["market_trends", "comparable_sales", "neighborhood_analysis", "demand_forecasting"],
                risk_tolerance="moderate",
                voting_weight=1.1,
                personality_traits=["strategic", "forward_thinking", "data_driven"]
            ),
            CommitteeMember(
                member_id="legal_expert_1",
                name="Sarah Thompson",
                role=CommitteeMemberRole.LEGAL_EXPERT,
                expertise=["title_issues", "zoning_law", "regulatory_compliance", "contract_analysis"],
                risk_tolerance="conservative",
                voting_weight=1.0,
                personality_traits=["thorough", "risk_averse", "compliance_focused"]
            ),
            CommitteeMember(
                member_id="construction_expert_1",
                name="David Kim",
                role=CommitteeMemberRole.CONSTRUCTION_EXPERT,
                expertise=["renovation_costs", "structural_analysis", "permit_requirements", "project_management"],
                risk_tolerance="moderate",
                voting_weight=1.0,
                personality_traits=["practical", "experienced", "solution_oriented"]
            ),
            CommitteeMember(
                member_id="risk_manager_1",
                name="Jennifer Walsh",
                role=CommitteeMemberRole.RISK_MANAGER,
                expertise=["risk_assessment", "scenario_analysis", "insurance", "contingency_planning"],
                risk_tolerance="conservative",
                voting_weight=1.1,
                personality_traits=["cautious", "systematic", "comprehensive"]
            )
        ]
    
    async def generate_investment_memo(
        self,
        property_data: Dict[str, Any],
        financial_analysis: Dict[str, Any],
        market_data: Dict[str, Any],
        legal_analysis: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> InvestmentMemo:
        """
        Generate comprehensive investment memo through committee analysis.
        
        Args:
            property_data: Basic property information
            financial_analysis: Financial metrics and projections
            market_data: Market conditions and comparables
            legal_analysis: Legal and compliance information
            additional_context: Any additional context or requirements
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Gather individual member opinions
            member_opinions = await self._gather_member_opinions(
                property_data, financial_analysis, market_data, legal_analysis, additional_context
            )
            
            # Step 2: Conduct committee debate
            debate_rounds = await self._conduct_committee_debate(
                member_opinions, property_data, financial_analysis
            )
            
            # Step 3: Reach committee decision
            committee_decision, voting_breakdown = await self._reach_committee_decision(
                member_opinions, debate_rounds
            )
            
            # Step 4: Generate executive summary
            executive_summary = await self._generate_executive_summary(
                committee_decision, member_opinions, debate_rounds
            )
            
            # Step 5: Compile consensus and risks
            consensus_points = self._extract_consensus_points(debate_rounds)
            key_risks = self._extract_key_risks(member_opinions)
            key_opportunities = self._extract_key_opportunities(member_opinions)
            
            # Step 6: Generate recommendations
            investment_recommendation = await self._generate_investment_recommendation(
                committee_decision, member_opinions, financial_analysis
            )
            
            # Step 7: Calculate decision confidence
            decision_confidence = self._calculate_decision_confidence(member_opinions, voting_breakdown)
            
            # Create comprehensive memo
            memo = InvestmentMemo(
                property_id=property_data.get("id", ""),
                property_address=property_data.get("address", ""),
                memo_date=start_time,
                committee_decision=committee_decision,
                decision_confidence=decision_confidence,
                unanimous_decision=len(set(voting_breakdown.values())) == 1,
                voting_breakdown=voting_breakdown,
                
                executive_summary=executive_summary,
                property_overview=self._compile_property_overview(property_data),
                financial_analysis=financial_analysis,
                market_analysis=market_data,
                risk_analysis=self._compile_risk_analysis(member_opinions),
                legal_considerations=legal_analysis,
                
                member_opinions=member_opinions,
                debate_summary=debate_rounds,
                consensus_points=consensus_points,
                key_risks=key_risks,
                key_opportunities=key_opportunities,
                
                investment_recommendation=investment_recommendation,
                suggested_offer_price=self._calculate_suggested_offer(financial_analysis, member_opinions),
                financing_recommendations=self._generate_financing_recommendations(financial_analysis),
                due_diligence_priorities=self._generate_due_diligence_priorities(member_opinions),
                exit_strategy_options=self._generate_exit_strategies(property_data, financial_analysis),
                
                comparable_deals=market_data.get("comparable_deals", []),
                sensitivity_analysis=financial_analysis.get("sensitivity_analysis", {}),
                stress_test_results=financial_analysis.get("stress_test_results", {})
            )
            
            # Cache the memo
            await cache_set(f"investment_memo:{property_data.get('id', 'unknown')}", 
                          memo.__dict__, expire=7200)
            
            # Publish real-time update
            await self._publish_memo_update(memo)
            
            logger.info(f"Investment memo generated for {property_data.get('address', 'unknown')}")
            return memo
            
        except Exception as e:
            logger.error(f"Investment memo generation failed: {e}")
            raise
    
    async def _gather_member_opinions(
        self,
        property_data: Dict[str, Any],
        financial_analysis: Dict[str, Any],
        market_data: Dict[str, Any],
        legal_analysis: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]]
    ) -> List[MemberOpinion]:
        """Gather individual opinions from each committee member."""
        opinions = []
        
        for member in self.committee_members:
            try:
                opinion = await self._get_member_opinion(
                    member, property_data, financial_analysis, market_data, legal_analysis
                )
                opinions.append(opinion)
            except Exception as e:
                logger.warning(f"Failed to get opinion from {member.name}: {e}")
        
        return opinions
    
    async def _get_member_opinion(
        self,
        member: CommitteeMember,
        property_data: Dict[str, Any],
        financial_analysis: Dict[str, Any],
        market_data: Dict[str, Any],
        legal_analysis: Dict[str, Any]
    ) -> MemberOpinion:
        """Get opinion from a specific committee member."""
        if not self.is_initialized:
            return self._generate_mock_opinion(member, property_data, financial_analysis)
        
        try:
            # Create role-specific prompt
            prompt = self._create_member_prompt(member, property_data, financial_analysis, market_data, legal_analysis)
            
            # Generate response using AI
            response = self.gemini_model.generate_content(prompt)
            
            # Parse the response (simplified - would need more robust parsing)
            opinion_data = self._parse_member_response(response.text, member)
            
            return MemberOpinion(
                member_id=member.member_id,
                member_name=member.name,
                recommendation=opinion_data.get("recommendation", CommitteeDecision.HOLD),
                confidence_level=opinion_data.get("confidence_level", 0.5),
                reasoning=opinion_data.get("reasoning", ""),
                key_concerns=opinion_data.get("key_concerns", []),
                opportunities_identified=opinion_data.get("opportunities", []),
                risk_assessment=opinion_data.get("risk_assessment", "medium"),
                financial_projections=opinion_data.get("financial_projections", {}),
                supporting_evidence=opinion_data.get("supporting_evidence", [])
            )
            
        except Exception as e:
            logger.warning(f"AI opinion generation failed for {member.name}: {e}")
            return self._generate_mock_opinion(member, property_data, financial_analysis)
    
    def _create_member_prompt(
        self,
        member: CommitteeMember,
        property_data: Dict[str, Any],
        financial_analysis: Dict[str, Any],
        market_data: Dict[str, Any],
        legal_analysis: Dict[str, Any]
    ) -> str:
        """Create a role-specific prompt for the committee member."""
        base_context = f"""
        You are {member.name}, a {member.role.value.replace('_', ' ').title()} on an investment committee.
        
        Your expertise areas: {', '.join(member.expertise)}
        Your risk tolerance: {member.risk_tolerance}
        Your personality traits: {', '.join(member.personality_traits)}
        
        Property Details:
        - Address: {property_data.get('address', 'Unknown')}
        - Type: {property_data.get('property_type', 'Unknown')}
        - Price: ${property_data.get('price', 0):,}
        - Size: {property_data.get('sqft', 0)} sq ft
        - Beds/Baths: {property_data.get('beds', 0)}/{property_data.get('baths', 0)}
        
        Financial Analysis:
        - Monthly Cash Flow: ${financial_analysis.get('monthly_cash_flow', 0):,}
        - Cash-on-Cash Return: {financial_analysis.get('cash_on_cash_return', 0):.2%}
        - Cap Rate: {financial_analysis.get('cap_rate', 0):.2%}
        
        Based on your expertise and perspective, provide your investment recommendation.
        
        Respond with your analysis in the following format:
        RECOMMENDATION: [strong_buy/buy/hold/pass/avoid]
        CONFIDENCE: [0.0-1.0]
        REASONING: [Your detailed reasoning]
        KEY_CONCERNS: [List key concerns]
        OPPORTUNITIES: [List opportunities you see]
        RISK_ASSESSMENT: [low/medium/high]
        """
        
        # Add role-specific focus
        if member.role == CommitteeMemberRole.FINANCIAL_ANALYST:
            base_context += "\nFocus particularly on the financial metrics, cash flow projections, and return calculations."
        elif member.role == CommitteeMemberRole.MARKET_ANALYST:
            base_context += "\nFocus on market conditions, comparable sales, and neighborhood trends."
        elif member.role == CommitteeMemberRole.LEGAL_EXPERT:
            base_context += "\nFocus on legal compliance, title issues, and regulatory risks."
        elif member.role == CommitteeMemberRole.CONSTRUCTION_EXPERT:
            base_context += "\nFocus on property condition, renovation needs, and construction costs."
        elif member.role == CommitteeMemberRole.RISK_MANAGER:
            base_context += "\nFocus on identifying and quantifying all potential risks and mitigation strategies."
        
        return base_context
    
    def _parse_member_response(self, response_text: str, member: CommitteeMember) -> Dict[str, Any]:
        """Parse AI response into structured opinion data."""
        # Simplified parsing - in production would use more robust parsing
        lines = response_text.split('\n')
        opinion_data = {}
        
        for line in lines:
            if line.startswith('RECOMMENDATION:'):
                rec_text = line.split(':', 1)[1].strip().lower()
                try:
                    opinion_data['recommendation'] = CommitteeDecision(rec_text)
                except ValueError:
                    opinion_data['recommendation'] = CommitteeDecision.HOLD
            elif line.startswith('CONFIDENCE:'):
                try:
                    opinion_data['confidence_level'] = float(line.split(':', 1)[1].strip())
                except ValueError:
                    opinion_data['confidence_level'] = 0.5
            elif line.startswith('REASONING:'):
                opinion_data['reasoning'] = line.split(':', 1)[1].strip()
            elif line.startswith('KEY_CONCERNS:'):
                concerns_text = line.split(':', 1)[1].strip()
                opinion_data['key_concerns'] = [c.strip() for c in concerns_text.split(',') if c.strip()]
            elif line.startswith('OPPORTUNITIES:'):
                opps_text = line.split(':', 1)[1].strip()
                opinion_data['opportunities'] = [o.strip() for o in opps_text.split(',') if o.strip()]
            elif line.startswith('RISK_ASSESSMENT:'):
                opinion_data['risk_assessment'] = line.split(':', 1)[1].strip().lower()
        
        return opinion_data
    
    def _generate_mock_opinion(self, member: CommitteeMember, property_data: Dict[str, Any], financial_analysis: Dict[str, Any]) -> MemberOpinion:
        """Generate mock opinion when AI is not available."""
        # Generate opinion based on member's role and risk tolerance
        cash_flow = financial_analysis.get('monthly_cash_flow', 0)
        coc_return = financial_analysis.get('cash_on_cash_return', 0)
        
        if member.risk_tolerance == "conservative":
            if cash_flow > 500 and coc_return > 0.08:
                recommendation = CommitteeDecision.BUY
                confidence = 0.8
            elif cash_flow > 0 and coc_return > 0.06:
                recommendation = CommitteeDecision.HOLD
                confidence = 0.6
            else:
                recommendation = CommitteeDecision.PASS
                confidence = 0.7
        else:  # moderate or aggressive
            if cash_flow > 200 and coc_return > 0.10:
                recommendation = CommitteeDecision.STRONG_BUY
                confidence = 0.9
            elif cash_flow > 0 and coc_return > 0.08:
                recommendation = CommitteeDecision.BUY
                confidence = 0.8
            else:
                recommendation = CommitteeDecision.HOLD
                confidence = 0.5
        
        return MemberOpinion(
            member_id=member.member_id,
            member_name=member.name,
            recommendation=recommendation,
            confidence_level=confidence,
            reasoning=f"Based on {member.role.value} analysis of financial metrics and risk profile",
            key_concerns=["Market volatility", "Interest rate risk"],
            opportunities_identified=["Potential rent growth", "Property appreciation"],
            risk_assessment="medium",
            financial_projections={"5_year_irr": 0.12, "exit_value": financial_analysis.get('estimated_value', 0) * 1.2},
            supporting_evidence=["Cash flow analysis", "Market comparables"]
        )
    
    async def _conduct_committee_debate(self, member_opinions: List[MemberOpinion], property_data: Dict[str, Any], financial_analysis: Dict[str, Any]) -> List[DebateRound]:
        """Conduct multi-round committee debate."""
        debate_rounds = []
        
        # Identify initial disagreements
        recommendations = [opinion.recommendation for opinion in member_opinions]
        unique_recs = set(recommendations)
        
        if len(unique_recs) == 1:
            # Unanimous decision - minimal debate needed
            debate_rounds.append(DebateRound(
                round_number=1,
                topic="Unanimous recommendation validation",
                member_statements=[{
                    "member": "Committee Chair",
                    "statement": "Committee reached unanimous decision. Brief validation discussion."
                }],
                consensus_points=["All members agree on recommendation"],
                disagreement_points=[],
                new_insights=[]
            ))
        else:
            # Multiple rounds of debate for disagreements
            topics = [
                "Initial position statements and key disagreements",
                "Risk assessment and mitigation strategies", 
                "Financial projections and sensitivity analysis"
            ]
            
            for round_num, topic in enumerate(topics[:self.debate_rounds], 1):
                debate_round = await self._conduct_debate_round(round_num, topic, member_opinions, property_data)
                debate_rounds.append(debate_round)
        
        return debate_rounds
    
    async def _conduct_debate_round(self, round_number: int, topic: str, member_opinions: List[MemberOpinion], property_data: Dict[str, Any]) -> DebateRound:
        """Conduct a single round of debate."""
        member_statements = []
        
        # Generate statements for each member based on topic
        for opinion in member_opinions:
            statement = await self._generate_debate_statement(opinion, topic, round_number)
            member_statements.append({
                "member": opinion.member_name,
                "role": opinion.member_id.split('_')[0],
                "statement": statement,
                "position": opinion.recommendation.value
            })
        
        # Identify consensus and disagreement points
        consensus_points = self._identify_consensus_points(member_statements)
        disagreement_points = self._identify_disagreement_points(member_statements)
        new_insights = self._extract_debate_insights(member_statements)
        
        return DebateRound(
            round_number=round_number,
            topic=topic,
            member_statements=member_statements,
            consensus_points=consensus_points,
            disagreement_points=disagreement_points,
            new_insights=new_insights
        )
    
    async def _generate_debate_statement(self, opinion: MemberOpinion, topic: str, round_number: int) -> str:
        """Generate a debate statement for a committee member."""
        # Mock debate statements based on role and opinion
        role = opinion.member_id.split('_')[0]
        recommendation = opinion.recommendation.value
        
        statements = {
            "financial": {
                1: f"From a financial perspective, I {recommendation.replace('_', ' ')} this deal. The cash-on-cash returns and cap rates {('support' if recommendation in ['buy', 'strong_buy'] else 'do not support')} our investment criteria.",
                2: f"Looking at the risk-adjusted returns, we need to consider {opinion.key_concerns[0] if opinion.key_concerns else 'market volatility'} in our projections.",
                3: f"My final assessment maintains {recommendation.replace('_', ' ')} based on the financial fundamentals and risk profile."
            },
            "market": {
                1: f"Market conditions {('favor' if recommendation in ['buy', 'strong_buy'] else 'are challenging for')} this type of investment. Local trends show {('positive momentum' if recommendation in ['buy', 'strong_buy'] else 'concerning patterns')}.",
                2: f"Comparable sales and rental rates {('validate' if recommendation in ['buy', 'strong_buy'] else 'question')} our assumptions about future performance.",
                3: f"Market analysis confirms my {recommendation.replace('_', ' ')} recommendation based on current and projected conditions."
            },
            "legal": {
                1: f"From a legal standpoint, I must {('recommend proceeding with' if recommendation in ['buy', 'strong_buy'] else 'express caution about')} this transaction due to {('clean title and compliance' if recommendation in ['buy', 'strong_buy'] else 'potential legal issues')}.",
                2: f"Due diligence requirements include thorough review of {opinion.key_concerns[0] if opinion.key_concerns else 'title and permits'}.",
                3: f"Legal analysis supports {recommendation.replace('_', ' ')} with appropriate safeguards in place."
            },
            "construction": {
                1: f"Construction and renovation analysis {('supports' if recommendation in ['buy', 'strong_buy'] else 'raises concerns about')} this investment. Cost estimates and timeline projections are {('favorable' if recommendation in ['buy', 'strong_buy'] else 'challenging')}.",
                2: f"Key construction considerations include {opinion.key_concerns[0] if opinion.key_concerns else 'structural integrity and permit requirements'}.",
                3: f"Final construction assessment maintains {recommendation.replace('_', ' ')} based on renovation scope and costs."
            },
            "risk": {
                1: f"Risk assessment indicates {('acceptable' if recommendation in ['buy', 'strong_buy'] else 'elevated')} risk levels for this investment. Key mitigation strategies {('are available' if recommendation in ['buy', 'strong_buy'] else 'may be insufficient')}.",
                2: f"Stress testing reveals {('resilient' if recommendation in ['buy', 'strong_buy'] else 'vulnerable')} performance under adverse scenarios.",
                3: f"Comprehensive risk analysis confirms {recommendation.replace('_', ' ')} recommendation with identified mitigation measures."
            }
        }
        
        return statements.get(role, {}).get(round_number, f"I maintain my {recommendation.replace('_', ' ')} recommendation based on my analysis.")
    
    def _identify_consensus_points(self, member_statements: List[Dict[str, Any]]) -> List[str]:
        """Identify points of consensus from debate statements."""
        # Mock consensus identification
        return [
            "Property has potential for positive returns",
            "Market fundamentals are generally sound",
            "Due diligence is essential before proceeding"
        ]
    
    def _identify_disagreement_points(self, member_statements: List[Dict[str, Any]]) -> List[str]:
        """Identify points of disagreement from debate statements."""
        positions = [stmt["position"] for stmt in member_statements]
        unique_positions = set(positions)
        
        if len(unique_positions) > 1:
            return [
                "Risk tolerance levels vary among committee members",
                "Different weight given to market vs. financial factors",
                "Varying confidence in renovation cost estimates"
            ]
        return []
    
    def _extract_debate_insights(self, member_statements: List[Dict[str, Any]]) -> List[str]:
        """Extract new insights generated during debate."""
        return [
            "Need additional market research for comparable properties",
            "Consider phased renovation approach to mitigate risk",
            "Explore alternative financing structures"
        ]
    
    async def _reach_committee_decision(self, member_opinions: List[MemberOpinion], debate_rounds: List[DebateRound]) -> Tuple[CommitteeDecision, Dict[str, str]]:
        """Reach final committee decision through weighted voting."""
        # Calculate weighted votes
        vote_scores = {}
        voting_breakdown = {}
        
        for opinion in member_opinions:
            member = next(m for m in self.committee_members if m.member_id == opinion.member_id)
            vote_weight = member.voting_weight * opinion.confidence_level
            
            if opinion.recommendation not in vote_scores:
                vote_scores[opinion.recommendation] = 0
            vote_scores[opinion.recommendation] += vote_weight
            voting_breakdown[member.name] = opinion.recommendation.value
        
        # Determine winning decision
        if vote_scores:
            committee_decision = max(vote_scores, key=vote_scores.get)
        else:
            committee_decision = CommitteeDecision.HOLD
        
        return committee_decision, voting_breakdown
    
    async def _generate_executive_summary(self, decision: CommitteeDecision, opinions: List[MemberOpinion], debates: List[DebateRound]) -> str:
        """Generate executive summary of committee analysis."""
        summary_template = f"""
        INVESTMENT COMMITTEE RECOMMENDATION: {decision.value.upper().replace('_', ' ')}
        
        The Investment Committee has completed a comprehensive analysis and recommends to {decision.value.replace('_', ' ')} this investment opportunity. 
        
        KEY FINDINGS:
        - Committee reached {('unanimous' if len(set(op.recommendation for op in opinions)) == 1 else 'majority')} decision
        - Financial analysis shows {('positive' if decision in [CommitteeDecision.BUY, CommitteeDecision.STRONG_BUY] else 'challenging')} return metrics
        - Risk assessment indicates {('manageable' if decision in [CommitteeDecision.BUY, CommitteeDecision.STRONG_BUY] else 'elevated')} risk levels
        - Market conditions are {('favorable' if decision in [CommitteeDecision.BUY, CommitteeDecision.STRONG_BUY] else 'mixed')} for this investment type
        
        COMMITTEE PERSPECTIVE:
        The committee engaged in {len(debates)} rounds of detailed analysis, examining financial, market, legal, construction, and risk factors. 
        {('Strong consensus emerged' if len(set(op.recommendation for op in opinions)) == 1 else 'After thorough debate, majority consensus was reached')} 
        supporting the {decision.value.replace('_', ' ')} recommendation.
        
        This recommendation is based on comprehensive due diligence and reflects the collective expertise of the investment committee.
        """
        
        return summary_template.strip()
    
    def _extract_consensus_points(self, debate_rounds: List[DebateRound]) -> List[str]:
        """Extract consensus points from all debate rounds."""
        all_consensus = []
        for round_data in debate_rounds:
            all_consensus.extend(round_data.consensus_points)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_consensus = []
        for point in all_consensus:
            if point not in seen:
                seen.add(point)
                unique_consensus.append(point)
        
        return unique_consensus[:5]  # Top 5 consensus points
    
    def _extract_key_risks(self, member_opinions: List[MemberOpinion]) -> List[str]:
        """Extract key risks identified by committee members."""
        all_risks = []
        for opinion in member_opinions:
            all_risks.extend(opinion.key_concerns)
        
        # Count frequency and return most mentioned risks
        risk_counts = {}
        for risk in all_risks:
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        sorted_risks = sorted(risk_counts.items(), key=lambda x: x[1], reverse=True)
        return [risk for risk, count in sorted_risks[:5]]
    
    def _extract_key_opportunities(self, member_opinions: List[MemberOpinion]) -> List[str]:
        """Extract key opportunities identified by committee members."""
        all_opportunities = []
        for opinion in member_opinions:
            all_opportunities.extend(opinion.opportunities_identified)
        
        # Count frequency and return most mentioned opportunities
        opp_counts = {}
        for opp in all_opportunities:
            opp_counts[opp] = opp_counts.get(opp, 0) + 1
        
        sorted_opps = sorted(opp_counts.items(), key=lambda x: x[1], reverse=True)
        return [opp for opp, count in sorted_opps[:5]]
    
    async def _generate_investment_recommendation(self, decision: CommitteeDecision, opinions: List[MemberOpinion], financial_analysis: Dict[str, Any]) -> str:
        """Generate detailed investment recommendation."""
        if decision == CommitteeDecision.STRONG_BUY:
            return "Strong Buy: Exceptional investment opportunity with superior returns and manageable risk profile. Recommend immediate action to secure this asset."
        elif decision == CommitteeDecision.BUY:
            return "Buy: Solid investment opportunity meeting our investment criteria. Recommend proceeding with standard due diligence timeline."
        elif decision == CommitteeDecision.HOLD:
            return "Hold: Investment shows potential but requires additional analysis or market conditions to improve before proceeding."
        elif decision == CommitteeDecision.PASS:
            return "Pass: Investment does not meet our current criteria. Recommend focusing resources on more attractive opportunities."
        else:  # AVOID
            return "Avoid: Significant risks or poor returns make this investment unsuitable for our portfolio. Do not proceed."
    
    def _compile_property_overview(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compile property overview section."""
        return {
            "address": property_data.get("address", ""),
            "property_type": property_data.get("property_type", ""),
            "size_sqft": property_data.get("sqft", 0),
            "bedrooms": property_data.get("beds", 0),
            "bathrooms": property_data.get("baths", 0),
            "year_built": property_data.get("year_built", 0),
            "lot_size": property_data.get("lot_size", 0),
            "asking_price": property_data.get("price", 0),
            "estimated_value": property_data.get("estimated_value", 0)
        }
    
    def _compile_risk_analysis(self, member_opinions: List[MemberOpinion]) -> Dict[str, Any]:
        """Compile risk analysis from member opinions."""
        risk_levels = [op.risk_assessment for op in member_opinions]
        risk_counts = {"low": 0, "medium": 0, "high": 0}
        
        for level in risk_levels:
            if level in risk_counts:
                risk_counts[level] += 1
        
        overall_risk = max(risk_counts, key=risk_counts.get)
        
        return {
            "overall_risk_level": overall_risk,
            "risk_distribution": risk_counts,
            "key_risk_factors": self._extract_key_risks(member_opinions),
            "mitigation_strategies": [
                "Comprehensive due diligence",
                "Conservative financing structure",
                "Contingency reserves",
                "Professional property management"
            ]
        }
    
    def _calculate_suggested_offer(self, financial_analysis: Dict[str, Any], member_opinions: List[MemberOpinion]) -> Optional[float]:
        """Calculate suggested offer price based on analysis."""
        asking_price = financial_analysis.get("purchase_price", 0)
        estimated_value = financial_analysis.get("estimated_value", asking_price)
        
        # Conservative approach - offer below asking if deal quality is questionable
        avg_confidence = sum(op.confidence_level for op in member_opinions) / len(member_opinions)
        
        if avg_confidence > 0.8:
            suggested_offer = asking_price * 0.98  # 2% below asking
        elif avg_confidence > 0.6:
            suggested_offer = asking_price * 0.95  # 5% below asking
        else:
            suggested_offer = asking_price * 0.90  # 10% below asking
        
        return round(suggested_offer, -3)  # Round to nearest thousand
    
    def _generate_financing_recommendations(self, financial_analysis: Dict[str, Any]) -> List[str]:
        """Generate financing recommendations."""
        return [
            "Conventional 30-year fixed mortgage for stability",
            "Consider portfolio lender for better terms",
            "Maintain 25% down payment for optimal cash flow",
            "Explore interest rate buy-down options"
        ]
    
    def _generate_due_diligence_priorities(self, member_opinions: List[MemberOpinion]) -> List[str]:
        """Generate due diligence priorities based on member concerns."""
        all_concerns = []
        for opinion in member_opinions:
            all_concerns.extend(opinion.key_concerns)
        
        priorities = [
            "Professional property inspection",
            "Title and lien search",
            "Rental market analysis",
            "Renovation cost verification",
            "Insurance and tax verification"
        ]
        
        return priorities[:5]
    
    def _generate_exit_strategies(self, property_data: Dict[str, Any], financial_analysis: Dict[str, Any]) -> List[str]:
        """Generate exit strategy options."""
        property_type = property_data.get("property_type", "residential")
        
        strategies = [
            "Long-term hold for cash flow and appreciation",
            "Refinance after value-add improvements",
            "Sale to retail buyer after 3-5 years",
            "1031 exchange into larger property"
        ]
        
        if property_type == "commercial":
            strategies.append("Sale to institutional investor")
        
        return strategies
    
    def _calculate_decision_confidence(self, member_opinions: List[MemberOpinion], voting_breakdown: Dict[str, str]) -> float:
        """Calculate overall confidence in committee decision."""
        # Average member confidence weighted by their individual confidence
        weighted_confidence = sum(op.confidence_level for op in member_opinions) / len(member_opinions)
        
        # Adjust for consensus level
        unique_votes = len(set(voting_breakdown.values()))
        consensus_factor = 1.0 if unique_votes == 1 else 0.8 if unique_votes == 2 else 0.6
        
        return min(1.0, weighted_confidence * consensus_factor)
    
    async def _publish_memo_update(self, memo: InvestmentMemo):
        """Publish real-time update about memo completion."""
        try:
            websocket_manager = get_websocket_manager()
            if websocket_manager:
                await websocket_manager.broadcast_to_all({
                    "type": "investment_memo_complete",
                    "property_id": memo.property_id,
                    "property_address": memo.property_address,
                    "committee_decision": memo.committee_decision.value,
                    "decision_confidence": memo.decision_confidence,
                    "unanimous_decision": memo.unanimous_decision,
                    "key_risks_count": len(memo.key_risks),
                    "key_opportunities_count": len(memo.key_opportunities)
                })
            
            # Publish to Redis
            await publish_event("agent_activity", "investment_memo_complete", {
                "agent_id": self.agent_id,
                "memo_summary": {
                    "property_id": memo.property_id,
                    "committee_decision": memo.committee_decision.value,
                    "decision_confidence": memo.decision_confidence,
                    "unanimous": memo.unanimous_decision
                }
            })
            
        except Exception as e:
            logger.warning(f"Failed to publish memo update: {e}")

# Global instance
_investment_committee_agent = None

def get_investment_committee_agent() -> AIInvestmentCommitteeAgent:
    """Get global investment committee agent instance."""
    global _investment_committee_agent
    if _investment_committee_agent is None:
        _investment_committee_agent = AIInvestmentCommitteeAgent()
    return _investment_committee_agent

async def investment_committee_agent_handler(task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler function for investment committee agent tasks."""
    agent = get_investment_committee_agent()
    
    if not agent.is_initialized:
        raise RuntimeError("AI Investment Committee Agent not properly initialized")
    
    if task_type == "generate_memo":
        memo = await agent.generate_investment_memo(
            property_data=task_data.get("property_data", {}),
            financial_analysis=task_data.get("financial_analysis", {}),
            market_data=task_data.get("market_data", {}),
            legal_analysis=task_data.get("legal_analysis", {}),
            additional_context=task_data.get("additional_context")
        )
        return {"investment_memo": memo.__dict__}
    
    else:
        raise ValueError(f"Unknown task type: {task_type}")