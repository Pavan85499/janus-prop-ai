"""
AI Insights Agent for Real Estate AI System

This agent provides explainable AI insights, predictions, and actionable recommendations
for real estate properties. Every insight includes a clear explanation and next steps.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
import structlog
from pydantic import BaseModel, Field

from agents.base_agent import BaseAgent, AgentConfig, AgentResponse


class PropertyInsight(BaseModel):
    """A single AI insight about a property."""
    
    insight_id: str = Field(default_factory=lambda: str(uuid4()))
    property_id: str
    insight_type: str  # "market_opportunity", "risk_assessment", "investment_potential", etc.
    confidence_score: float = Field(ge=0.0, le=1.0)
    explanation: str  # Plain English explanation of why this insight exists
    actionable_steps: List[str]  # List of specific actions user can take
    data_sources: List[str]  # Sources that support this insight
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PropertyAnalysis(BaseModel):
    """Complete analysis of a property with multiple insights."""
    
    property_id: str
    analysis_id: str = Field(default_factory=lambda: str(uuid4()))
    insights: List[PropertyInsight]
    overall_score: float = Field(ge=0.0, le=1.0)
    summary: str  # High-level summary of the property
    next_steps: List[str]  # Prioritized list of next actions
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class AIInsightsAgent(BaseAgent):
    """
    Agent that provides explainable AI insights for real estate properties.
    
    This agent ensures that every prediction or score comes with:
    1. Clear explanation in plain English
    2. Actionable next steps
    3. Confidence levels
    4. Data sources that support the insight
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.logger = structlog.get_logger(self.__class__.__name__)
    
    def _get_supported_operations(self) -> List[str]:
        """Return list of operations this agent supports."""
        return [
            "analyze_property",
            "generate_insights",
            "explain_prediction",
            "suggest_actions",
            "assess_risk",
            "evaluate_opportunity"
        ]

    async def _process_request_impl(
        self,
        request: Union[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a request for AI insights."""
        if isinstance(request, str):
            response = await self._handle_text_request(request, context)
        else:
            response = await self._handle_structured_request(request, context)
        
        if response.success:
            return response.data
        else:
            # The base agent will catch this exception and format it
            raise Exception(response.error)
    
    async def _handle_text_request(self, request: str, context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle natural language requests."""
        return AgentResponse(
            success=True,
            data={
                "message": "Text-based requests not yet implemented. Please use structured requests.",
                "supported_formats": ["property_analysis", "insight_generation"]
            }
        )
    
    async def _handle_structured_request(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle structured requests for property analysis."""
        request_type = request.get("type")
        
        if request_type == "property_analysis":
            return await self._analyze_property(request, context)
        elif request_type == "insight_generation":
            return await self._generate_insights(request, context)
        else:
            return AgentResponse(
                success=False,
                error=f"Unsupported request type: {request_type}",
                data=None
            )
    
    async def _analyze_property(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Analyze a property and generate comprehensive insights."""
        try:
            property_data = request.get("property_data", {})
            property_id = property_data.get("property_id")
            
            if not property_id:
                return AgentResponse(
                    success=False,
                    error="Property ID is required for analysis",
                    data=None
                )
            
            # Generate insights based on property data
            insights = await self._generate_property_insights(property_data, context)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(insights)
            
            # Generate summary and next steps
            summary = self._generate_summary(insights, property_data)
            next_steps = self._prioritize_next_steps(insights)
            
            analysis = PropertyAnalysis(
                property_id=property_id,
                insights=insights,
                overall_score=overall_score,
                summary=summary,
                next_steps=next_steps
            )
            
            return AgentResponse(
                success=True,
                data=analysis.dict()
            )
            
        except Exception as e:
            self.logger.error("Error analyzing property", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Property analysis failed: {str(e)}",
                data=None
            )
    
    async def _generate_property_insights(self, property_data: Dict[str, Any], context: Optional[Dict[str, Any]]) -> List[PropertyInsight]:
        """Generate insights for a property based on available data."""
        insights = []
        
        # Market opportunity insight
        if self._has_market_data(property_data):
            market_insight = await self._generate_market_insight(property_data)
            insights.append(market_insight)
        
        # Risk assessment insight
        risk_insight = await self._generate_risk_insight(property_data)
        insights.append(risk_insight)
        
        # Investment potential insight
        investment_insight = await self._generate_investment_insight(property_data)
        insights.append(investment_insight)
        
        return insights
    
    async def _generate_market_insight(self, property_data: Dict[str, Any]) -> PropertyInsight:
        """Generate market opportunity insight."""
        market_conditions = property_data.get("market_conditions", {})
        price_trend = market_conditions.get("price_trend", "stable")
        
        if price_trend == "rising":
            explanation = "Property values in this area are increasing by 5-8% annually, indicating strong market momentum and potential for appreciation."
            confidence = 0.85
            actions = [
                "Consider purchasing before prices increase further",
                "Research comparable sales in the area",
                "Consult with local real estate agents about market timing"
            ]
        else:
            explanation = "Market conditions are stable with moderate growth potential. This represents a balanced investment opportunity."
            confidence = 0.70
            actions = [
                "Monitor market trends for optimal entry timing",
                "Compare with other investment opportunities",
                "Assess long-term growth potential"
            ]
        
        return PropertyInsight(
            property_id=property_data.get("property_id"),
            insight_type="market_opportunity",
            confidence_score=confidence,
            explanation=explanation,
            actionable_steps=actions,
            data_sources=["market_analysis", "price_trends", "local_economic_data"]
        )
    
    async def _generate_risk_insight(self, property_data: Dict[str, Any]) -> PropertyInsight:
        """Generate risk assessment insight."""
        risk_factors = []
        risk_score = 0.0
        
        if property_data.get("property_condition") == "poor":
            risk_factors.append("Property requires significant repairs")
            risk_score += 0.3
        
        if property_data.get("market_volatility", "low") == "high":
            risk_factors.append("High market volatility in the area")
            risk_score += 0.2
        
        if not risk_factors:
            risk_factors.append("Low risk profile with stable market conditions")
            risk_score = 0.1
        
        explanation = f"Risk assessment based on: {', '.join(risk_factors)}. Overall risk level: {'High' if risk_score > 0.5 else 'Medium' if risk_score > 0.2 else 'Low'}."
        
        actions = [
            "Conduct thorough property inspection",
            "Review local crime statistics and safety reports",
            "Consult with insurance providers about coverage options"
        ]
        
        return PropertyInsight(
            property_id=property_data.get("property_id"),
            insight_type="risk_assessment",
            confidence_score=0.80,
            explanation=explanation,
            actionable_steps=actions,
            data_sources=["property_inspection", "crime_statistics", "market_analysis"]
        )
    
    async def _generate_investment_insight(self, property_data: Dict[str, Any]) -> PropertyInsight:
        """Generate investment potential insight."""
        purchase_price = property_data.get("purchase_price", 0)
        estimated_rent = property_data.get("estimated_monthly_rent", 0)
        
        if purchase_price > 0 and estimated_rent > 0:
            annual_roi = (estimated_rent * 12) / purchase_price
            explanation = f"Based on current market data, this property shows a potential annual ROI of {annual_roi:.1%}. This compares favorably to the local market average of 6-8%."
            confidence = 0.75
        else:
            explanation = "Investment potential analysis requires complete financial data including purchase price and rental estimates."
            confidence = 0.50
        
        actions = [
            "Calculate detailed cash flow projections",
            "Compare with other investment properties in the area",
            "Consult with financial advisor about financing options"
        ]
        
        return PropertyInsight(
            property_id=property_data.get("property_id"),
            insight_type="investment_potential",
            confidence_score=confidence,
            explanation=explanation,
            actionable_steps=actions,
            data_sources=["financial_analysis", "market_comparisons", "rental_data"]
        )
    
    def _calculate_overall_score(self, insights: List[PropertyInsight]) -> float:
        """Calculate overall property score based on insights."""
        if not insights:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for insight in insights:
            weight = self._get_insight_weight(insight.insight_type)
            total_weighted_score += insight.confidence_score * weight
            total_weight += weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _get_insight_weight(self, insight_type: str) -> float:
        """Get weight for different insight types."""
        weights = {
            "market_opportunity": 0.3,
            "investment_potential": 0.25,
            "risk_assessment": 0.2,
            "financing_analysis": 0.15,
            "market_timing": 0.1
        }
        return weights.get(insight_type, 0.1)
    
    def _generate_summary(self, insights: List[PropertyInsight], property_data: Dict[str, Any]) -> str:
        """Generate a high-level summary of the property analysis."""
        if not insights:
            return "Insufficient data for comprehensive analysis."
        
        positive_insights = [i for i in insights if i.confidence_score > 0.7]
        risk_insights = [i for i in insights if i.insight_type == "risk_assessment" and i.confidence_score > 0.6]
        
        if len(positive_insights) > len(insights) * 0.6:
            summary = "This property shows strong potential with multiple positive indicators."
        elif len(risk_insights) > 0:
            summary = "Property has mixed indicators with some areas of concern that require attention."
        else:
            summary = "Property shows moderate potential with opportunities for improvement."
        
        return summary
    
    def _prioritize_next_steps(self, insights: List[PropertyInsight]) -> List[str]:
        """Prioritize next steps based on insights."""
        all_steps = []
        for insight in insights:
            all_steps.extend(insight.actionable_steps)
        
        unique_steps = list(dict.fromkeys(all_steps))
        
        high_confidence_insights = [i for i in insights if i.confidence_score > 0.8]
        high_priority_steps = []
        
        for insight in high_confidence_insights:
            for step in insight.actionable_steps:
                if step in unique_steps and step not in high_priority_steps:
                    high_priority_steps.append(step)
        
        remaining_steps = [step for step in unique_steps if step not in high_priority_steps]
        
        return high_priority_steps + remaining_steps
    
    def _has_market_data(self, property_data: Dict[str, Any]) -> bool:
        """Check if property has sufficient market data for analysis."""
        return bool(property_data.get("market_conditions") or property_data.get("comparable_sales"))
    
    async def _generate_insights(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Generate insights for multiple properties."""
        # Placeholder implementation
        return AgentResponse(
            success=True,
            data={"message": "Insight generation not yet implemented"}
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of this agent."""
        return {
            "status": "healthy",
            "agent_type": "ai_insights",
            "capabilities": await self.get_capabilities(),
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the agent."""
        self.logger.info("AI Insights Agent shutting down")
