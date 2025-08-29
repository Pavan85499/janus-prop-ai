"""
Gemini AI Agent for Real Estate AI System

This agent uses Google's Gemini API to provide explainable AI insights,
predictions, and actionable recommendations for real estate properties.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
import structlog
from pydantic import BaseModel, Field
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

from agents.base_agent import BaseAgent, AgentConfig, AgentResponse


class GeminiPropertyInsight(BaseModel):
    """A single AI insight about a property using Gemini."""
    
    insight_id: str = Field(default_factory=lambda: str(uuid4()))
    property_id: str
    insight_type: str  # "market_opportunity", "risk_assessment", "investment_potential", etc.
    confidence_score: float = Field(ge=0.0, le=1.0)
    explanation: str  # Plain English explanation of why this insight exists
    actionable_steps: List[str]  # List of specific actions user can take
    data_sources: List[str]  # Sources that support this insight
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GeminiPropertyAnalysis(BaseModel):
    """Complete analysis of a property with multiple insights using Gemini."""
    
    property_id: str
    analysis_id: str = Field(default_factory=lambda: str(uuid4()))
    insights: List[GeminiPropertyInsight]
    overall_score: float = Field(ge=0.0, le=1.0)
    summary: str  # High-level summary of the property
    next_steps: List[str]  # Prioritized list of next actions
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class GeminiAIAgent(BaseAgent):
    """
    Agent that provides explainable AI insights for real estate properties using Gemini.
    
    This agent ensures that every prediction or score comes with:
    1. Clear explanation in plain English
    2. Actionable next steps
    3. Confidence levels
    4. Data sources that support the insight
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.logger = structlog.get_logger(self.__class__.__name__)
        
        # Initialize Gemini API
        self.gemini_api_key = config.metadata.get("gemini_api_key")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.langchain_model = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=self.gemini_api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
        else:
            self.logger.warning("No Gemini API key provided, agent will not function properly")
            self.model = None
            self.langchain_model = None
    
    def _get_supported_operations(self) -> List[str]:
        """Return list of operations this agent supports."""
        return [
            "analyze_property",
            "generate_insights",
            "explain_prediction",
            "suggest_actions",
            "assess_risk",
            "evaluate_opportunity",
            "market_analysis",
            "investment_recommendation"
        ]

    async def _process_request_impl(
        self,
        request: Union[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a request for AI insights using Gemini."""
        if not self.model:
            raise Exception("Gemini API not configured")
            
        if isinstance(request, str):
            response = await self._handle_text_request(request, context)
        else:
            response = await self._handle_structured_request(request, context)
        
        if response.success:
            return response.data
        else:
            raise Exception(response.error)
    
    async def _handle_text_request(self, request: str, context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle natural language requests using Gemini."""
        try:
            # Create a system prompt for real estate analysis
            system_prompt = """You are an expert real estate analyst using Gemini AI. 
            Analyze the following request and provide insights in this format:
            
            {
                "insights": [
                    {
                        "insight_type": "market_opportunity|risk_assessment|investment_potential",
                        "confidence_score": 0.85,
                        "explanation": "Clear explanation in plain English",
                        "actionable_steps": ["Step 1", "Step 2"],
                        "data_sources": ["source1", "source2"]
                    }
                ],
                "overall_score": 0.80,
                "summary": "High-level summary",
                "next_steps": ["Next action 1", "Next action 2"]
            }"""
            
            # Generate response using Gemini
            response = await asyncio.to_thread(
                self.model.generate_content,
                f"{system_prompt}\n\nUser Request: {request}"
            )
            
            # Parse the response
            try:
                import json
                parsed_response = json.loads(response.text)
                return AgentResponse(
                    success=True,
                    data=parsed_response,
                    agent_id=self.config.agent_id
                )
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw text
                return AgentResponse(
                    success=True,
                    data={
                        "message": response.text,
                        "raw_response": True
                    },
                    agent_id=self.config.agent_id
                )
                
        except Exception as e:
            self.logger.error("Error processing text request with Gemini", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Failed to process request: {str(e)}",
                agent_id=self.config.agent_id
            )
    
    async def _handle_structured_request(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle structured requests for property analysis using Gemini."""
        request_type = request.get("type")
        
        if request_type == "analyze_property":
            return await self._analyze_property(request, context)
        elif request_type == "generate_insights":
            return await self._generate_insights(request, context)
        elif request_type == "market_analysis":
            return await self._market_analysis(request, context)
        elif request_type == "investment_recommendation":
            return await self._investment_recommendation(request, context)
        else:
            return AgentResponse(
                success=False,
                error=f"Unsupported request type: {request_type}",
                agent_id=self.config.agent_id
            )
    
    async def _analyze_property(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Analyze a property using Gemini AI."""
        try:
            property_data = request.get("property_data", {})
            
            # Create analysis prompt
            analysis_prompt = f"""
            Analyze this real estate property and provide comprehensive insights:
            
            Property Data: {property_data}
            
            Provide analysis in this exact JSON format:
            {{
                "insights": [
                    {{
                        "insight_type": "market_opportunity",
                        "confidence_score": 0.85,
                        "explanation": "Clear explanation",
                        "actionable_steps": ["Action 1", "Action 2"],
                        "data_sources": ["MLS", "Market Data"]
                    }}
                ],
                "overall_score": 0.80,
                "summary": "Property summary",
                "next_steps": ["Next step 1", "Next step 2"]
            }}
            """
            
            # Generate analysis using Gemini
            response = await asyncio.to_thread(
                self.model.generate_content,
                analysis_prompt
            )
            
            # Parse response
            import json
            parsed_response = json.loads(response.text)
            
            return AgentResponse(
                success=True,
                data=parsed_response,
                agent_id=self.config.agent_id
            )
            
        except Exception as e:
            self.logger.error("Error analyzing property with Gemini", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Property analysis failed: {str(e)}",
                agent_id=self.config.agent_id
            )
    
    async def _generate_insights(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Generate specific insights using Gemini."""
        try:
            insight_type = request.get("insight_type", "general")
            property_context = request.get("property_context", {})
            
            prompt = f"""
            Generate {insight_type} insights for this real estate property:
            
            Context: {property_context}
            
            Focus on: {insight_type}
            
            Provide insights in JSON format with confidence scores and actionable steps.
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            # Parse and return insights
            import json
            parsed_response = json.loads(response.text)
            
            return AgentResponse(
                success=True,
                data=parsed_response,
                agent_id=self.config.agent_id
            )
            
        except Exception as e:
            self.logger.error("Error generating insights with Gemini", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Insight generation failed: {str(e)}",
                agent_id=self.config.agent_id
            )
    
    async def _market_analysis(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Perform market analysis using Gemini."""
        try:
            market_data = request.get("market_data", {})
            location = request.get("location", "")
            
            prompt = f"""
            Analyze the real estate market for {location}:
            
            Market Data: {market_data}
            
            Provide market analysis including:
            - Market trends
            - Price movements
            - Investment opportunities
            - Risk factors
            
            Format as JSON with insights and recommendations.
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            import json
            parsed_response = json.loads(response.text)
            
            return AgentResponse(
                success=True,
                data=parsed_response,
                agent_id=self.config.agent_id
            )
            
        except Exception as e:
            self.logger.error("Error performing market analysis with Gemini", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Market analysis failed: {str(e)}",
                agent_id=self.config.agent_id
            )
    
    async def _investment_recommendation(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Generate investment recommendations using Gemini."""
        try:
            investment_criteria = request.get("investment_criteria", {})
            property_data = request.get("property_data", {})
            
            prompt = f"""
            Generate investment recommendations for this property:
            
            Property: {property_data}
            Investment Criteria: {investment_criteria}
            
            Provide:
            - Investment potential score
            - Risk assessment
            - Expected returns
            - Recommended actions
            
            Format as JSON with detailed analysis.
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            import json
            parsed_response = json.loads(response.text)
            
            return AgentResponse(
                success=True,
                data=parsed_response,
                agent_id=self.config.agent_id
            )
            
        except Exception as e:
            self.logger.error("Error generating investment recommendations with Gemini", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Investment recommendation failed: {str(e)}",
                agent_id=self.config.agent_id
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the Gemini AI agent."""
        try:
            if not self.model:
                return {
                    "status": "unhealthy",
                    "error": "Gemini API not configured",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test Gemini API connection
            test_response = await asyncio.to_thread(
                self.model.generate_content,
                "Hello, this is a health check."
            )
            
            return {
                "status": "healthy",
                "model": "gemini-pro",
                "api_working": True,
                "timestamp": datetime.utcnow().isoformat(),
                "response_time": "fast"
            }
            
        except Exception as e:
            self.logger.error("Health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
