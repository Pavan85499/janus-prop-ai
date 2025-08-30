"""
Gemini AI Agent for Janus Prop AI Backend

This module provides integration with Google's Gemini AI API for property analysis and insights.
"""

import asyncio
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

try:
    import google.generativeai as genai
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import HumanMessage, SystemMessage
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    ChatGoogleGenerativeAI = None

from config.settings import get_settings
from core.redis_client import cache_get, cache_set, publish_event

logger = structlog.get_logger(__name__)

class GeminiAIAgent:
    """Agent for Google Gemini AI integration."""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.GEMINI_API_KEY
        self.model_name = "gemini-pro"
        self.is_initialized = False
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured")
            return
        
        if not GEMINI_AVAILABLE:
            logger.warning("Google Generative AI libraries not available")
            return
        
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI client."""
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Initialize models
            self.text_model = genai.GenerativeModel(self.model_name)
            self.chat_model = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=0.7,
                max_output_tokens=2048
            )
            
            self.is_initialized = True
            logger.info("Gemini AI agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.is_initialized = False
    
    async def generate_property_insight(
        self,
        property_data: Dict[str, Any],
        insight_type: str = "market_analysis",
        additional_context: str = ""
    ) -> Dict[str, Any]:
        """Generate property insights using Gemini AI."""
        if not self.is_initialized:
            raise RuntimeError("Gemini AI agent not initialized")
        
        try:
            # Create prompt for property analysis
            prompt = self._create_property_prompt(property_data, insight_type, additional_context)
            
            # Generate response using Gemini
            response = await self._generate_response(prompt)
            
            # Parse and structure the response
            insight = self._parse_insight_response(response, property_data, insight_type)
            
            # Cache the insight
            cache_key = f"gemini_insight:{property_data.get('id', 'unknown')}:{insight_type}"
            await cache_set(cache_key, insight, expire=3600)
            
            logger.info(f"Generated Gemini insight for property {property_data.get('id', 'unknown')}")
            
            return insight
            
        except Exception as e:
            logger.error(f"Failed to generate property insight: {e}")
            raise
    
    async def analyze_market_trends(
        self,
        location: str,
        property_type: str = "residential",
        timeframe: str = "6_months"
    ) -> Dict[str, Any]:
        """Analyze market trends for a specific location."""
        if not self.is_initialized:
            raise RuntimeError("Gemini AI agent not initialized")
        
        try:
            # Create market analysis prompt
            prompt = self._create_market_analysis_prompt(location, property_type, timeframe)
            
            # Generate response
            response = await self._generate_response(prompt)
            
            # Parse market analysis
            analysis = self._parse_market_analysis(response, location, property_type, timeframe)
            
            # Cache the analysis
            cache_key = f"gemini_market_analysis:{location}:{property_type}:{timeframe}"
            await cache_set(cache_key, analysis, expire=7200)
            
            logger.info(f"Generated Gemini market analysis for {location}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze market trends: {e}")
            raise
    
    async def generate_investment_recommendation(
        self,
        property_data: Dict[str, Any],
        investor_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate investment recommendations using Gemini AI."""
        if not self.is_initialized:
            raise RuntimeError("Gemini AI agent not initialized")
        
        try:
            # Create investment analysis prompt
            prompt = self._create_investment_prompt(property_data, investor_profile)
            
            # Generate response
            response = await self._generate_response(prompt)
            
            # Parse investment recommendation
            recommendation = self._parse_investment_recommendation(response, property_data, investor_profile)
            
            logger.info(f"Generated Gemini investment recommendation for property {property_data.get('id', 'unknown')}")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Failed to generate investment recommendation: {e}")
            raise
    
    async def compare_properties(
        self,
        properties: List[Dict[str, Any]],
        comparison_criteria: List[str]
    ) -> Dict[str, Any]:
        """Compare multiple properties using Gemini AI."""
        if not self.is_initialized:
            raise RuntimeError("Gemini AI agent not initialized")
        
        try:
            # Create comparison prompt
            prompt = self._create_comparison_prompt(properties, comparison_criteria)
            
            # Generate response
            response = await self._generate_response(prompt)
            
            # Parse comparison
            comparison = self._parse_property_comparison(response, properties, comparison_criteria)
            
            logger.info(f"Generated Gemini property comparison for {len(properties)} properties")
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare properties: {e}")
            raise
    
    async def generate_lead_qualification(
        self,
        lead_data: Dict[str, Any],
        property_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Qualify leads using Gemini AI."""
        if not self.is_initialized:
            raise RuntimeError("Gemini AI agent not initialized")
        
        try:
            # Create lead qualification prompt
            prompt = self._create_lead_qualification_prompt(lead_data, property_data)
            
            # Generate response
            response = await self._generate_response(prompt)
            
            # Parse qualification
            qualification = self._parse_lead_qualification(response, lead_data, property_data)
            
            logger.info(f"Generated Gemini lead qualification for lead {lead_data.get('id', 'unknown')}")
            
            return qualification
            
        except Exception as e:
            logger.error(f"Failed to qualify lead: {e}")
            raise
    
    def _create_property_prompt(
        self,
        property_data: Dict[str, Any],
        insight_type: str,
        additional_context: str
    ) -> str:
        """Create a prompt for property analysis."""
        base_prompt = f"""
        You are an expert real estate analyst. Analyze the following property and provide insights for {insight_type}.
        
        Property Information:
        - Address: {property_data.get('address', 'N/A')}
        - Price: {property_data.get('price', 'N/A')}
        - Property Type: {property_data.get('property_type', 'N/A')}
        - Bedrooms: {property_data.get('bedrooms', 'N/A')}
        - Bathrooms: {property_data.get('bathrooms', 'N/A')}
        - Square Feet: {property_data.get('square_feet', 'N/A')}
        - Year Built: {property_data.get('year_built', 'N/A')}
        - Lot Size: {property_data.get('lot_size', 'N/A')}
        
        Additional Context: {additional_context}
        
        Please provide:
        1. A concise title for the insight
        2. A detailed analysis (2-3 paragraphs)
        3. Key factors influencing the analysis
        4. Confidence level (0-100%)
        5. Relevant tags for categorization
        6. Specific recommendations or next steps
        
        Format your response as JSON with the following structure:
        {{
            "title": "Insight Title",
            "description": "Detailed analysis...",
            "key_factors": ["factor1", "factor2", "factor3"],
            "confidence_score": 85,
            "tags": ["tag1", "tag2", "tag3"],
            "recommendations": ["rec1", "rec2"],
            "risk_factors": ["risk1", "risk2"],
            "market_trends": ["trend1", "trend2"]
        }}
        """
        
        return base_prompt.strip()
    
    def _create_market_analysis_prompt(
        self,
        location: str,
        property_type: str,
        timeframe: str
    ) -> str:
        """Create a prompt for market analysis."""
        prompt = f"""
        You are an expert real estate market analyst. Provide a comprehensive market analysis for {location} focusing on {property_type} properties over the last {timeframe}.
        
        Please analyze:
        1. Current market conditions
        2. Price trends and appreciation rates
        3. Supply and demand dynamics
        4. Key market drivers
        5. Future outlook and predictions
        6. Investment opportunities
        7. Potential risks
        
        Format your response as JSON with the following structure:
        {{
            "location": "{location}",
            "property_type": "{property_type}",
            "timeframe": "{timeframe}",
            "summary": "Market overview...",
            "current_conditions": "Current state...",
            "price_trends": {{
                "trend": "increasing/decreasing/stable",
                "rate": "percentage change",
                "factors": ["factor1", "factor2"]
            }},
            "supply_demand": {{
                "supply": "high/medium/low",
                "demand": "high/medium/low",
                "balance": "balanced/supply_heavy/demand_heavy"
            }},
            "market_drivers": ["driver1", "driver2", "driver3"],
            "future_outlook": "Prediction...",
            "investment_opportunities": ["opp1", "opp2"],
            "risks": ["risk1", "risk2"],
            "recommendations": ["rec1", "rec2"]
        }}
        """
        
        return prompt.strip()
    
    def _create_investment_prompt(
        self,
        property_data: Dict[str, Any],
        investor_profile: Dict[str, Any]
    ) -> str:
        """Create a prompt for investment analysis."""
        prompt = f"""
        You are an expert real estate investment advisor. Analyze the following property for investment potential based on the investor profile.
        
        Property Information:
        - Address: {property_data.get('address', 'N/A')}
        - Price: {property_data.get('price', 'N/A')}
        - Property Type: {property_data.get('property_type', 'N/A')}
        - Estimated Rent: {property_data.get('estimated_rent', 'N/A')}
        - Property Condition: {property_data.get('condition', 'N/A')}
        
        Investor Profile:
        - Investment Goals: {investor_profile.get('goals', 'N/A')}
        - Risk Tolerance: {investor_profile.get('risk_tolerance', 'N/A')}
        - Investment Timeline: {investor_profile.get('timeline', 'N/A')}
        - Budget: {investor_profile.get('budget', 'N/A')}
        - Experience Level: {investor_profile.get('experience', 'N/A')}
        
        Please provide:
        1. Investment recommendation (buy/hold/sell)
        2. Expected ROI analysis
        3. Risk assessment
        4. Financing recommendations
        5. Exit strategy options
        6. Timeline for returns
        
        Format your response as JSON with the following structure:
        {{
            "recommendation": "buy/hold/sell",
            "confidence": 85,
            "expected_roi": {{
                "annual": "8-12%",
                "total_5yr": "45-60%",
                "assumptions": ["assumption1", "assumption2"]
            }},
            "risk_assessment": {{
                "overall_risk": "low/medium/high",
                "specific_risks": ["risk1", "risk2"],
                "mitigation_strategies": ["strategy1", "strategy2"]
            }},
            "financing": {{
                "recommended_loan_type": "conventional/fha/va",
                "down_payment": "20%",
                "interest_rate_assumption": "6.5%"
            }},
            "exit_strategies": ["strategy1", "strategy2"],
            "timeline": "3-5 years",
            "key_factors": ["factor1", "factor2"]
        }}
        """
        
        return prompt.strip()
    
    def _create_comparison_prompt(
        self,
        properties: List[Dict[str, Any]],
        comparison_criteria: List[str]
    ) -> str:
        """Create a prompt for property comparison."""
        properties_info = []
        for i, prop in enumerate(properties, 1):
            prop_info = f"""
            Property {i}:
            - Address: {prop.get('address', 'N/A')}
            - Price: {prop.get('price', 'N/A')}
            - Property Type: {prop.get('property_type', 'N/A')}
            - Bedrooms: {prop.get('bedrooms', 'N/A')}
            - Bathrooms: {prop.get('bathrooms', 'N/A')}
            - Square Feet: {prop.get('square_feet', 'N/A')}
            """
            properties_info.append(prop_info)
        
        prompt = f"""
        You are an expert real estate analyst. Compare the following properties based on the criteria: {', '.join(comparison_criteria)}.
        
        {''.join(properties_info)}
        
        Please provide a comprehensive comparison including:
        1. Overall ranking
        2. Detailed analysis for each property
        3. Pros and cons of each
        4. Best value for money
        5. Investment potential comparison
        6. Recommendations
        
        Format your response as JSON with the following structure:
        {{
            "overall_ranking": ["property1_id", "property2_id", "property3_id"],
            "best_value": "property_id",
            "best_investment": "property_id",
            "comparison": {{
                "property1_id": {{
                    "ranking": 1,
                    "pros": ["pro1", "pro2"],
                    "cons": ["con1", "con2"],
                    "score": 85,
                    "analysis": "Detailed analysis..."
                }}
            }},
            "recommendations": ["rec1", "rec2"],
            "key_differences": ["diff1", "diff2"]
        }}
        """
        
        return prompt.strip()
    
    def _create_lead_qualification_prompt(
        self,
        lead_data: Dict[str, Any],
        property_data: Dict[str, Any]
    ) -> str:
        """Create a prompt for lead qualification."""
        prompt = f"""
        You are an expert real estate lead qualification specialist. Analyze the following lead and property match.
        
        Lead Information:
        - Name: {lead_data.get('first_name', 'N/A')} {lead_data.get('last_name', 'N/A')}
        - Email: {lead_data.get('email', 'N/A')}
        - Phone: {lead_data.get('phone', 'N/A')}
        - Source: {lead_data.get('source', 'N/A')}
        - Budget Range: {lead_data.get('budget_range', 'N/A')}
        - Property Preferences: {lead_data.get('property_preferences', 'N/A')}
        
        Property Information:
        - Address: {property_data.get('address', 'N/A')}
        - Price: {property_data.get('price', 'N/A')}
        - Property Type: {property_data.get('property_type', 'N/A')}
        
        Please provide:
        1. Lead qualification score (0-100)
        2. Match quality assessment
        3. Likelihood of conversion
        4. Recommended follow-up actions
        5. Priority level
        6. Risk factors
        
        Format your response as JSON with the following structure:
        {{
            "qualification_score": 75,
            "match_quality": "high/medium/low",
            "conversion_likelihood": "high/medium/low",
            "priority": "high/medium/low",
            "recommended_actions": ["action1", "action2"],
            "follow_up_timeline": "immediate/within_24h/within_week",
            "risk_factors": ["risk1", "risk2"],
            "notes": "Additional insights..."
        }}
        """
        
        return prompt.strip()
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response using Gemini AI."""
        try:
            # Use the chat model for better conversation handling
            messages = [
                SystemMessage(content="You are an expert real estate analyst. Provide accurate, professional analysis in the requested JSON format."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.chat_model.agenerate([messages])
            
            if response.generations and response.generations[0]:
                return response.generations[0][0].text
            else:
                raise RuntimeError("No response generated from Gemini")
                
        except Exception as e:
            logger.error(f"Failed to generate Gemini response: {e}")
            raise
    
    def _parse_insight_response(
        self,
        response: str,
        property_data: Dict[str, Any],
        insight_type: str
    ) -> Dict[str, Any]:
        """Parse the insight response from Gemini."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            
            # Add metadata
            parsed.update({
                "property_id": property_data.get('id'),
                "insight_type": insight_type,
                "ai_model": "gemini",
                "generated_date": datetime.utcnow().isoformat(),
                "confidence_score": parsed.get('confidence_score', 0) / 100.0  # Convert to 0-1 scale
            })
            
            return parsed
            
        except Exception as e:
            logger.error(f"Failed to parse insight response: {e}")
            # Return fallback response
            return {
                "title": f"AI Generated {insight_type.title()}",
                "description": "AI analysis completed but response parsing failed.",
                "confidence_score": 0.5,
                "ai_model": "gemini",
                "generated_date": datetime.utcnow().isoformat(),
                "property_id": property_data.get('id'),
                "insight_type": insight_type
            }
    
    def _parse_market_analysis(
        self,
        response: str,
        location: str,
        property_type: str,
        timeframe: str
    ) -> Dict[str, Any]:
        """Parse market analysis response."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            
            # Add metadata
            parsed.update({
                "ai_model": "gemini",
                "generated_date": datetime.utcnow().isoformat(),
                "analysis_id": f"market_analysis_{location}_{property_type}_{timeframe}"
            })
            
            return parsed
            
        except Exception as e:
            logger.error(f"Failed to parse market analysis: {e}")
            return {
                "location": location,
                "property_type": property_type,
                "timeframe": timeframe,
                "summary": "Market analysis completed but response parsing failed.",
                "ai_model": "gemini",
                "generated_date": datetime.utcnow().isoformat()
            }
    
    def _parse_investment_recommendation(
        self,
        response: str,
        property_data: Dict[str, Any],
        investor_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse investment recommendation response."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            
            # Add metadata
            parsed.update({
                "property_id": property_data.get('id'),
                "ai_model": "gemini",
                "generated_date": datetime.utcnow().isoformat(),
                "investor_profile": investor_profile
            })
            
            return parsed
            
        except Exception as e:
            logger.error(f"Failed to parse investment recommendation: {e}")
            return {
                "recommendation": "hold",
                "confidence": 50,
                "property_id": property_data.get('id'),
                "ai_model": "gemini",
                "generated_date": datetime.utcnow().isoformat()
            }
    
    def _parse_property_comparison(
        self,
        response: str,
        properties: List[Dict[str, Any]],
        comparison_criteria: List[str]
    ) -> Dict[str, Any]:
        """Parse property comparison response."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            
            # Add metadata
            parsed.update({
                "ai_model": "gemini",
                "generated_date": datetime.utcnow().isoformat(),
                "comparison_criteria": comparison_criteria,
                "properties_compared": len(properties)
            })
            
            return parsed
            
        except Exception as e:
            logger.error(f"Failed to parse property comparison: {e}")
            return {
                "overall_ranking": [prop.get('id', f'prop_{i}') for i, prop in enumerate(properties)],
                "ai_model": "gemini",
                "generated_date": datetime.utcnow().isoformat()
            }
    
    def _parse_lead_qualification(
        self,
        response: str,
        lead_data: Dict[str, Any],
        property_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse lead qualification response."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            
            # Add metadata
            parsed.update({
                "lead_id": lead_data.get('id'),
                "property_id": property_data.get('id'),
                "ai_model": "gemini",
                "generated_date": datetime.utcnow().isoformat()
            })
            
            return parsed
            
        except Exception as e:
            logger.error(f"Failed to parse lead qualification: {e}")
            return {
                "qualification_score": 50,
                "match_quality": "medium",
                "conversion_likelihood": "medium",
                "lead_id": lead_data.get('id'),
                "property_id": property_data.get('id'),
                "ai_model": "gemini",
                "generated_date": datetime.utcnow().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the Gemini AI agent."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "initialized": self.is_initialized,
            "api_key_configured": bool(self.api_key),
            "libraries_available": GEMINI_AVAILABLE,
            "model_name": self.model_name,
            "last_check": datetime.utcnow().isoformat()
        }

# Global Gemini agent instance
_gemini_agent: Optional[GeminiAIAgent] = None

def get_gemini_agent() -> GeminiAIAgent:
    """Get the global Gemini AI agent instance."""
    global _gemini_agent
    if _gemini_agent is None:
        _gemini_agent = GeminiAIAgent()
    return _gemini_agent

async def gemini_agent_handler(task) -> Dict[str, Any]:
    """Handler function for Gemini AI agent tasks."""
    agent = get_gemini_agent()
    
    if task.task_type == "generate_property_insight":
        return await agent.generate_property_insight(
            property_data=task.metadata.get('property_data', {}),
            insight_type=task.metadata.get('insight_type', 'market_analysis'),
            additional_context=task.metadata.get('additional_context', '')
        )
    
    elif task.task_type == "analyze_market_trends":
        return await agent.analyze_market_trends(
            location=task.metadata.get('location', ''),
            property_type=task.metadata.get('property_type', 'residential'),
            timeframe=task.metadata.get('timeframe', '6_months')
        )
    
    elif task.task_type == "generate_investment_recommendation":
        return await agent.generate_investment_recommendation(
            property_data=task.metadata.get('property_data', {}),
            investor_profile=task.metadata.get('investor_profile', {})
        )
    
    elif task.task_type == "compare_properties":
        return await agent.compare_properties(
            properties=task.metadata.get('properties', []),
            comparison_criteria=task.metadata.get('comparison_criteria', [])
        )
    
    elif task.task_type == "generate_lead_qualification":
        return await agent.generate_lead_qualification(
            lead_data=task.metadata.get('lead_data', {}),
            property_data=task.metadata.get('property_data', {})
        )
    
    else:
        raise ValueError(f"Unknown task type: {task.task_type}")
