"""
Automated Underwriting & Analysis Agent for Janus Prop AI Backend

This agent specializes in instant cash-flow models, rent comparables, 
renovation scenarios, cap rates, sensitivity analyses and stress tests.
"""

import asyncio
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import math
from dataclasses import dataclass
from enum import Enum

try:
    import numpy as np
    import pandas as pd
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

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

class PropertyType(Enum):
    SINGLE_FAMILY = "single_family"
    MULTI_FAMILY = "multi_family"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    COMMERCIAL = "commercial"
    MIXED_USE = "mixed_use"

class InvestmentStrategy(Enum):
    BUY_AND_HOLD = "buy_and_hold"
    FLIP = "flip"
    BRRRR = "brrrr"  # Buy, Rehab, Rent, Refinance, Repeat
    WHOLESALE = "wholesale"
    LIVE_IN_FLIP = "live_in_flip"

@dataclass
class PropertyFinancials:
    """Core property financial data."""
    purchase_price: float
    after_repair_value: float
    renovation_cost: float
    closing_costs: float
    monthly_rent: float
    monthly_expenses: float
    down_payment_percent: float
    interest_rate: float
    loan_term_years: int
    property_taxes: float
    insurance: float
    maintenance_reserve: float
    vacancy_rate: float
    property_management_fee: float

@dataclass
class CashFlowAnalysis:
    """Cash flow analysis results."""
    monthly_gross_rent: float
    monthly_net_rent: float
    monthly_mortgage_payment: float
    monthly_expenses: float
    monthly_cash_flow: float
    annual_cash_flow: float
    cash_on_cash_return: float
    cap_rate: float
    gross_rent_multiplier: float
    debt_service_coverage_ratio: float
    break_even_ratio: float

@dataclass
class RentComparable:
    """Rental comparable data."""
    address: str
    monthly_rent: float
    beds: int
    baths: int
    sqft: int
    distance_miles: float
    days_on_market: int
    rent_per_sqft: float
    property_type: str
    amenities: List[str]
    confidence_score: float

@dataclass
class RenovationScenario:
    """Renovation scenario analysis."""
    scenario_name: str
    renovation_items: Dict[str, float]  # item -> cost
    total_cost: float
    estimated_arv_increase: float
    estimated_rent_increase: float
    roi_estimate: float
    payback_period_months: int
    risk_level: str  # "low", "medium", "high"

@dataclass
class SensitivityAnalysis:
    """Sensitivity analysis results."""
    base_case_cash_flow: float
    scenarios: Dict[str, Dict[str, float]]  # scenario -> metrics
    stress_test_results: Dict[str, float]
    risk_assessment: str
    recommendation: str

@dataclass
class UnderwritingReport:
    """Comprehensive underwriting report."""
    property_id: str
    property_address: str
    analysis_date: datetime
    property_financials: PropertyFinancials
    cash_flow_analysis: CashFlowAnalysis
    rent_comparables: List[RentComparable]
    renovation_scenarios: List[RenovationScenario]
    sensitivity_analysis: SensitivityAnalysis
    investment_recommendation: str
    risk_rating: str  # "A", "B", "C", "D"
    confidence_score: float
    key_insights: List[str]
    assumptions: Dict[str, Any]

class AutomatedUnderwritingAgent:
    """AI Agent specialized in automated underwriting and analysis."""
    
    def __init__(self):
        self.agent_id = "automated_underwriting_agent"
        self.name = "Automated Underwriting Agent"
        self.settings = get_settings()
        self.gemini_api_key = self.settings.GEMINI_API_KEY
        self.is_initialized = False
        
        # Default market assumptions
        self.market_assumptions = {
            "default_cap_rate": 0.08,
            "default_cash_on_cash": 0.10,
            "default_vacancy_rate": 0.05,
            "default_property_management": 0.08,
            "default_maintenance_reserve": 0.05,
            "default_appreciation_rate": 0.03,
            "default_rent_growth_rate": 0.02,
            "default_interest_rate": 0.07,
            "default_down_payment": 0.25
        }
        
        # Renovation cost estimates (per sq ft or per unit)
        self.renovation_costs = {
            "cosmetic_light": {"cost_per_sqft": 15, "description": "Paint, fixtures, minor updates"},
            "cosmetic_heavy": {"cost_per_sqft": 30, "description": "Flooring, kitchen cabinets, bathrooms"},
            "moderate_rehab": {"cost_per_sqft": 50, "description": "Kitchen/bath remodel, HVAC, electrical"},
            "heavy_rehab": {"cost_per_sqft": 80, "description": "Structural, foundation, major systems"},
            "full_renovation": {"cost_per_sqft": 120, "description": "Complete gut renovation"}
        }
        
        if self._has_required_libraries():
            self._initialize_agent()
    
    def _has_required_libraries(self) -> bool:
        """Check if required libraries are available."""
        return ANALYTICS_AVAILABLE and bool(self.gemini_api_key)
    
    def _initialize_agent(self):
        """Initialize the automated underwriting agent."""
        try:
            if GEMINI_AVAILABLE and self.gemini_api_key:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel("gemini-pro")
                self.chat_model = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.gemini_api_key,
                    temperature=0.2,  # Low temperature for consistent analysis
                    max_output_tokens=4096
                )
            
            self.is_initialized = True
            logger.info("Automated Underwriting Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Automated Underwriting Agent: {e}")
            self.is_initialized = False
    
    async def generate_underwriting_report(
        self,
        property_data: Dict[str, Any],
        financial_inputs: Dict[str, Any],
        investment_strategy: InvestmentStrategy = InvestmentStrategy.BUY_AND_HOLD
    ) -> UnderwritingReport:
        """
        Generate comprehensive underwriting report for a property.
        
        Args:
            property_data: Property details (address, type, size, etc.)
            financial_inputs: Financial parameters (price, renovation, financing)
            investment_strategy: Investment strategy being analyzed
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Create property financials object
            property_financials = self._create_property_financials(property_data, financial_inputs)
            
            # Step 2: Perform cash flow analysis
            cash_flow_analysis = await self._perform_cash_flow_analysis(property_financials)
            
            # Step 3: Get rent comparables
            rent_comparables = await self._get_rent_comparables(property_data)
            
            # Step 4: Generate renovation scenarios
            renovation_scenarios = await self._generate_renovation_scenarios(
                property_data, property_financials
            )
            
            # Step 5: Perform sensitivity analysis
            sensitivity_analysis = await self._perform_sensitivity_analysis(
                property_financials, cash_flow_analysis
            )
            
            # Step 6: Generate investment recommendation
            investment_recommendation = await self._generate_investment_recommendation(
                cash_flow_analysis, sensitivity_analysis, investment_strategy
            )
            
            # Step 7: Calculate risk rating
            risk_rating = self._calculate_risk_rating(cash_flow_analysis, sensitivity_analysis)
            
            # Step 8: Generate key insights
            key_insights = await self._generate_key_insights(
                property_data, cash_flow_analysis, rent_comparables, renovation_scenarios
            )
            
            # Create comprehensive report
            report = UnderwritingReport(
                property_id=property_data.get("id", ""),
                property_address=property_data.get("address", ""),
                analysis_date=start_time,
                property_financials=property_financials,
                cash_flow_analysis=cash_flow_analysis,
                rent_comparables=rent_comparables,
                renovation_scenarios=renovation_scenarios,
                sensitivity_analysis=sensitivity_analysis,
                investment_recommendation=investment_recommendation,
                risk_rating=risk_rating,
                confidence_score=self._calculate_confidence_score(rent_comparables, property_data),
                key_insights=key_insights,
                assumptions=self._get_analysis_assumptions()
            )
            
            # Cache the report
            await cache_set(f"underwriting_report:{property_data.get('id', 'unknown')}", 
                          report.__dict__, expire=3600)
            
            # Publish real-time update
            await self._publish_analysis_update(report)
            
            logger.info(f"Underwriting report generated for {property_data.get('address', 'unknown')}")
            return report
            
        except Exception as e:
            logger.error(f"Underwriting analysis failed: {e}")
            raise
    
    def _create_property_financials(self, property_data: Dict[str, Any], financial_inputs: Dict[str, Any]) -> PropertyFinancials:
        """Create PropertyFinancials object from input data."""
        return PropertyFinancials(
            purchase_price=financial_inputs.get("purchase_price", 0),
            after_repair_value=financial_inputs.get("after_repair_value", financial_inputs.get("purchase_price", 0)),
            renovation_cost=financial_inputs.get("renovation_cost", 0),
            closing_costs=financial_inputs.get("closing_costs", financial_inputs.get("purchase_price", 0) * 0.03),
            monthly_rent=financial_inputs.get("monthly_rent", 0),
            monthly_expenses=financial_inputs.get("monthly_expenses", 0),
            down_payment_percent=financial_inputs.get("down_payment_percent", self.market_assumptions["default_down_payment"]),
            interest_rate=financial_inputs.get("interest_rate", self.market_assumptions["default_interest_rate"]),
            loan_term_years=financial_inputs.get("loan_term_years", 30),
            property_taxes=financial_inputs.get("property_taxes", financial_inputs.get("purchase_price", 0) * 0.015),
            insurance=financial_inputs.get("insurance", financial_inputs.get("purchase_price", 0) * 0.004),
            maintenance_reserve=financial_inputs.get("maintenance_reserve", financial_inputs.get("monthly_rent", 0) * self.market_assumptions["default_maintenance_reserve"]),
            vacancy_rate=financial_inputs.get("vacancy_rate", self.market_assumptions["default_vacancy_rate"]),
            property_management_fee=financial_inputs.get("property_management_fee", self.market_assumptions["default_property_management"])
        )
    
    async def _perform_cash_flow_analysis(self, financials: PropertyFinancials) -> CashFlowAnalysis:
        """Perform detailed cash flow analysis."""
        
        # Calculate loan amount and monthly payment
        loan_amount = financials.purchase_price * (1 - financials.down_payment_percent)
        monthly_rate = financials.interest_rate / 12
        num_payments = financials.loan_term_years * 12
        
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        else:
            monthly_payment = loan_amount / num_payments
        
        # Calculate monthly income and expenses
        monthly_gross_rent = financials.monthly_rent
        vacancy_loss = monthly_gross_rent * financials.vacancy_rate
        property_management = monthly_gross_rent * financials.property_management_fee
        monthly_net_rent = monthly_gross_rent - vacancy_loss - property_management
        
        monthly_property_taxes = financials.property_taxes / 12
        monthly_insurance = financials.insurance / 12
        total_monthly_expenses = (monthly_property_taxes + monthly_insurance + 
                                financials.maintenance_reserve + financials.monthly_expenses)
        
        # Calculate cash flow
        monthly_cash_flow = monthly_net_rent - monthly_payment - total_monthly_expenses
        annual_cash_flow = monthly_cash_flow * 12
        
        # Calculate returns
        total_cash_invested = (financials.purchase_price * financials.down_payment_percent + 
                             financials.closing_costs + financials.renovation_cost)
        
        cash_on_cash_return = annual_cash_flow / total_cash_invested if total_cash_invested > 0 else 0
        
        # Calculate cap rate (NOI / Property Value)
        annual_noi = (monthly_net_rent * 12) - (total_monthly_expenses * 12) + (monthly_payment * 12)  # Add back debt service
        cap_rate = annual_noi / financials.after_repair_value if financials.after_repair_value > 0 else 0
        
        # Calculate other metrics
        gross_rent_multiplier = financials.purchase_price / (monthly_gross_rent * 12) if monthly_gross_rent > 0 else 0
        debt_service_coverage_ratio = annual_noi / (monthly_payment * 12) if monthly_payment > 0 else float('inf')
        break_even_ratio = (total_monthly_expenses + monthly_payment) / monthly_gross_rent if monthly_gross_rent > 0 else 0
        
        return CashFlowAnalysis(
            monthly_gross_rent=monthly_gross_rent,
            monthly_net_rent=monthly_net_rent,
            monthly_mortgage_payment=monthly_payment,
            monthly_expenses=total_monthly_expenses,
            monthly_cash_flow=monthly_cash_flow,
            annual_cash_flow=annual_cash_flow,
            cash_on_cash_return=cash_on_cash_return,
            cap_rate=cap_rate,
            gross_rent_multiplier=gross_rent_multiplier,
            debt_service_coverage_ratio=debt_service_coverage_ratio,
            break_even_ratio=break_even_ratio
        )
    
    async def _get_rent_comparables(self, property_data: Dict[str, Any]) -> List[RentComparable]:
        """Get rental comparables for the property."""
        # Mock rent comparables - replace with real MLS/rental data API
        property_type = property_data.get("property_type", "single_family")
        beds = property_data.get("beds", 3)
        baths = property_data.get("baths", 2)
        sqft = property_data.get("sqft", 1200)
        
        base_rent = self._estimate_base_rent(property_data)
        
        comparables = [
            RentComparable(
                address=f"{1000 + i} Example St, Same City",
                monthly_rent=base_rent + (i * 50) - 100,
                beds=beds + (i % 2 - 1),  # Vary beds slightly
                baths=baths + (i % 3 - 1) * 0.5,  # Vary baths slightly
                sqft=sqft + (i * 100) - 200,
                distance_miles=0.5 + (i * 0.3),
                days_on_market=30 + (i * 10),
                rent_per_sqft=(base_rent + (i * 50) - 100) / (sqft + (i * 100) - 200),
                property_type=property_type,
                amenities=["parking", "laundry"] + (["pool"] if i % 3 == 0 else []),
                confidence_score=0.9 - (i * 0.1)
            )
            for i in range(5)
        ]
        
        return sorted(comparables, key=lambda x: x.confidence_score, reverse=True)
    
    def _estimate_base_rent(self, property_data: Dict[str, Any]) -> float:
        """Estimate base rent for property based on location and characteristics."""
        # Mock rent estimation - replace with real market data
        location = property_data.get("location", "").lower()
        sqft = property_data.get("sqft", 1200)
        beds = property_data.get("beds", 3)
        
        # Base rent per sq ft by market
        rent_per_sqft_by_market = {
            "los_angeles": 3.5,
            "san_francisco": 4.5,
            "new_york": 4.0,
            "chicago": 2.0,
            "phoenix": 1.8,
            "dallas": 1.5,
            "default": 2.0
        }
        
        rent_per_sqft = rent_per_sqft_by_market.get(location, rent_per_sqft_by_market["default"])
        base_rent = sqft * rent_per_sqft
        
        # Adjust for number of bedrooms
        if beds >= 4:
            base_rent *= 1.1
        elif beds <= 1:
            base_rent *= 0.9
        
        return round(base_rent, 0)
    
    async def _generate_renovation_scenarios(self, property_data: Dict[str, Any], financials: PropertyFinancials) -> List[RenovationScenario]:
        """Generate renovation scenarios and their impact on value and rent."""
        sqft = property_data.get("sqft", 1200)
        scenarios = []
        
        for scenario_name, scenario_data in self.renovation_costs.items():
            cost_per_sqft = scenario_data["cost_per_sqft"]
            total_cost = sqft * cost_per_sqft
            
            # Estimate ARV increase (conservative)
            arv_increase = total_cost * 1.2  # 20% value add
            
            # Estimate rent increase
            rent_increase_percent = {
                "cosmetic_light": 0.05,
                "cosmetic_heavy": 0.12,
                "moderate_rehab": 0.20,
                "heavy_rehab": 0.30,
                "full_renovation": 0.40
            }
            
            rent_increase = financials.monthly_rent * rent_increase_percent.get(scenario_name, 0.1)
            
            # Calculate ROI
            annual_rent_increase = rent_increase * 12
            roi = annual_rent_increase / total_cost if total_cost > 0 else 0
            
            # Calculate payback period
            payback_months = (total_cost / rent_increase) if rent_increase > 0 else float('inf')
            
            # Determine risk level
            risk_level = {
                "cosmetic_light": "low",
                "cosmetic_heavy": "low",
                "moderate_rehab": "medium",
                "heavy_rehab": "high",
                "full_renovation": "high"
            }.get(scenario_name, "medium")
            
            scenarios.append(RenovationScenario(
                scenario_name=scenario_name.replace("_", " ").title(),
                renovation_items={scenario_data["description"]: total_cost},
                total_cost=total_cost,
                estimated_arv_increase=arv_increase,
                estimated_rent_increase=rent_increase,
                roi_estimate=roi,
                payback_period_months=int(payback_months) if payback_months != float('inf') else 999,
                risk_level=risk_level
            ))
        
        return scenarios
    
    async def _perform_sensitivity_analysis(self, financials: PropertyFinancials, base_case: CashFlowAnalysis) -> SensitivityAnalysis:
        """Perform sensitivity analysis on key variables."""
        
        scenarios = {}
        
        # Interest rate sensitivity
        for rate_change in [-0.01, 0.01, 0.02]:  # -1%, +1%, +2%
            new_financials = financials
            new_financials.interest_rate += rate_change
            new_analysis = await self._perform_cash_flow_analysis(new_financials)
            scenarios[f"Interest Rate {'+' if rate_change >= 0 else ''}{rate_change*100:.1f}%"] = {
                "monthly_cash_flow": new_analysis.monthly_cash_flow,
                "cash_on_cash_return": new_analysis.cash_on_cash_return,
                "impact": new_analysis.monthly_cash_flow - base_case.monthly_cash_flow
            }
        
        # Rent sensitivity
        for rent_change in [-0.1, 0.05, 0.1]:  # -10%, +5%, +10%
            new_financials = financials
            new_financials.monthly_rent *= (1 + rent_change)
            new_analysis = await self._perform_cash_flow_analysis(new_financials)
            scenarios[f"Rent {'+' if rent_change >= 0 else ''}{rent_change*100:.0f}%"] = {
                "monthly_cash_flow": new_analysis.monthly_cash_flow,
                "cash_on_cash_return": new_analysis.cash_on_cash_return,
                "impact": new_analysis.monthly_cash_flow - base_case.monthly_cash_flow
            }
        
        # Vacancy rate sensitivity
        for vacancy_change in [0.05, 0.10]:  # +5%, +10% vacancy
            new_financials = financials
            new_financials.vacancy_rate += vacancy_change
            new_analysis = await self._perform_cash_flow_analysis(new_financials)
            scenarios[f"Vacancy +{vacancy_change*100:.0f}%"] = {
                "monthly_cash_flow": new_analysis.monthly_cash_flow,
                "cash_on_cash_return": new_analysis.cash_on_cash_return,
                "impact": new_analysis.monthly_cash_flow - base_case.monthly_cash_flow
            }
        
        # Stress test scenarios
        stress_tests = {
            "Recession Scenario": base_case.monthly_cash_flow * 0.7,  # 30% income drop
            "Major Repair": base_case.monthly_cash_flow - 500,  # $500/month extra costs
            "Extended Vacancy": base_case.monthly_cash_flow - financials.monthly_rent * 0.5  # 50% vacancy
        }
        
        # Risk assessment
        worst_case_cash_flow = min(scenario["monthly_cash_flow"] for scenario in scenarios.values())
        if worst_case_cash_flow < 0:
            risk_assessment = "High Risk: Negative cash flow in adverse scenarios"
        elif worst_case_cash_flow < base_case.monthly_cash_flow * 0.5:
            risk_assessment = "Medium Risk: Significant cash flow reduction possible"
        else:
            risk_assessment = "Low Risk: Cash flow remains stable across scenarios"
        
        # Generate recommendation
        recommendation = await self._generate_sensitivity_recommendation(scenarios, stress_tests)
        
        return SensitivityAnalysis(
            base_case_cash_flow=base_case.monthly_cash_flow,
            scenarios=scenarios,
            stress_test_results=stress_tests,
            risk_assessment=risk_assessment,
            recommendation=recommendation
        )
    
    async def _generate_sensitivity_recommendation(self, scenarios: Dict[str, Dict[str, float]], stress_tests: Dict[str, float]) -> str:
        """Generate recommendation based on sensitivity analysis."""
        negative_scenarios = sum(1 for s in scenarios.values() if s["monthly_cash_flow"] < 0)
        total_scenarios = len(scenarios)
        
        if negative_scenarios == 0:
            return "Strong investment with positive cash flow across all scenarios"
        elif negative_scenarios / total_scenarios < 0.3:
            return "Solid investment with minor downside risk in adverse conditions"
        else:
            return "High-risk investment with significant cash flow volatility"
    
    async def _generate_investment_recommendation(self, cash_flow: CashFlowAnalysis, sensitivity: SensitivityAnalysis, strategy: InvestmentStrategy) -> str:
        """Generate AI-powered investment recommendation."""
        if not self.is_initialized:
            return self._generate_basic_recommendation(cash_flow, sensitivity, strategy)
        
        try:
            prompt = f"""
            Analyze this real estate investment opportunity and provide a recommendation:
            
            Cash Flow Analysis:
            - Monthly Cash Flow: ${cash_flow.monthly_cash_flow:,.2f}
            - Annual Cash Flow: ${cash_flow.annual_cash_flow:,.2f}
            - Cash-on-Cash Return: {cash_flow.cash_on_cash_return:.2%}
            - Cap Rate: {cash_flow.cap_rate:.2%}
            - Debt Service Coverage: {cash_flow.debt_service_coverage_ratio:.2f}
            
            Risk Assessment: {sensitivity.risk_assessment}
            
            Investment Strategy: {strategy.value}
            
            Provide a concise recommendation (2-3 sentences) with specific reasoning.
            """
            
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.warning(f"AI recommendation generation failed: {e}")
            return self._generate_basic_recommendation(cash_flow, sensitivity, strategy)
    
    def _generate_basic_recommendation(self, cash_flow: CashFlowAnalysis, sensitivity: SensitivityAnalysis, strategy: InvestmentStrategy) -> str:
        """Generate basic recommendation without AI."""
        if cash_flow.monthly_cash_flow > 500 and cash_flow.cash_on_cash_return > 0.1:
            return "Strong Buy: Excellent cash flow and returns with low risk profile"
        elif cash_flow.monthly_cash_flow > 0 and cash_flow.cash_on_cash_return > 0.08:
            return "Buy: Positive cash flow with acceptable returns for long-term hold"
        elif cash_flow.monthly_cash_flow > -200 and cash_flow.cash_on_cash_return > 0.05:
            return "Consider: Marginal deal that may work with improvements or better financing"
        else:
            return "Pass: Poor cash flow and returns do not justify the investment risk"
    
    def _calculate_risk_rating(self, cash_flow: CashFlowAnalysis, sensitivity: SensitivityAnalysis) -> str:
        """Calculate risk rating based on financial metrics."""
        score = 0
        
        # Cash flow stability (40% weight)
        if cash_flow.monthly_cash_flow > 500:
            score += 40
        elif cash_flow.monthly_cash_flow > 200:
            score += 30
        elif cash_flow.monthly_cash_flow > 0:
            score += 20
        elif cash_flow.monthly_cash_flow > -200:
            score += 10
        
        # Returns quality (30% weight)
        if cash_flow.cash_on_cash_return > 0.12:
            score += 30
        elif cash_flow.cash_on_cash_return > 0.10:
            score += 25
        elif cash_flow.cash_on_cash_return > 0.08:
            score += 20
        elif cash_flow.cash_on_cash_return > 0.05:
            score += 10
        
        # Debt coverage (20% weight)
        if cash_flow.debt_service_coverage_ratio > 1.5:
            score += 20
        elif cash_flow.debt_service_coverage_ratio > 1.25:
            score += 15
        elif cash_flow.debt_service_coverage_ratio > 1.1:
            score += 10
        elif cash_flow.debt_service_coverage_ratio > 1.0:
            score += 5
        
        # Risk assessment (10% weight)
        if "Low Risk" in sensitivity.risk_assessment:
            score += 10
        elif "Medium Risk" in sensitivity.risk_assessment:
            score += 5
        
        # Convert to letter grade
        if score >= 80:
            return "A"
        elif score >= 65:
            return "B"
        elif score >= 50:
            return "C"
        else:
            return "D"
    
    async def _generate_key_insights(self, property_data: Dict[str, Any], cash_flow: CashFlowAnalysis, 
                                   rent_comparables: List[RentComparable], renovation_scenarios: List[RenovationScenario]) -> List[str]:
        """Generate key insights about the investment."""
        insights = []
        
        # Cash flow insights
        if cash_flow.monthly_cash_flow > 0:
            insights.append(f"Positive monthly cash flow of ${cash_flow.monthly_cash_flow:,.0f}")
        else:
            insights.append(f"Negative monthly cash flow of ${cash_flow.monthly_cash_flow:,.0f} requires subsidization")
        
        # Returns insights
        if cash_flow.cash_on_cash_return > 0.10:
            insights.append(f"Strong {cash_flow.cash_on_cash_return:.1%} cash-on-cash return exceeds market averages")
        elif cash_flow.cash_on_cash_return > 0.08:
            insights.append(f"Solid {cash_flow.cash_on_cash_return:.1%} cash-on-cash return meets investment criteria")
        
        # Cap rate insights
        if cash_flow.cap_rate > 0.08:
            insights.append(f"Attractive {cash_flow.cap_rate:.1%} cap rate indicates good value")
        elif cash_flow.cap_rate < 0.06:
            insights.append(f"Low {cash_flow.cap_rate:.1%} cap rate suggests premium pricing")
        
        # Rent comparable insights
        if rent_comparables:
            avg_comp_rent = sum(comp.monthly_rent for comp in rent_comparables) / len(rent_comparables)
            current_rent = cash_flow.monthly_gross_rent
            if current_rent < avg_comp_rent * 0.9:
                insights.append(f"Rent ${current_rent:,.0f} is below market average of ${avg_comp_rent:,.0f}")
            elif current_rent > avg_comp_rent * 1.1:
                insights.append(f"Rent ${current_rent:,.0f} is above market average of ${avg_comp_rent:,.0f}")
        
        # Renovation insights
        best_renovation = min(renovation_scenarios, key=lambda x: x.payback_period_months) if renovation_scenarios else None
        if best_renovation and best_renovation.payback_period_months < 36:
            insights.append(f"{best_renovation.scenario_name} renovation could pay back in {best_renovation.payback_period_months} months")
        
        return insights[:5]  # Limit to top 5 insights
    
    def _calculate_confidence_score(self, rent_comparables: List[RentComparable], property_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis."""
        score = 0.5  # Base confidence
        
        # Rent comparable quality
        if len(rent_comparables) >= 3:
            score += 0.2
            avg_confidence = sum(comp.confidence_score for comp in rent_comparables) / len(rent_comparables)
            score += avg_confidence * 0.2
        
        # Property data completeness
        required_fields = ["address", "beds", "baths", "sqft", "property_type"]
        completeness = sum(1 for field in required_fields if property_data.get(field)) / len(required_fields)
        score += completeness * 0.2
        
        # Market data availability
        if property_data.get("location"):
            score += 0.1
        
        return min(1.0, score)
    
    def _get_analysis_assumptions(self) -> Dict[str, Any]:
        """Get assumptions used in the analysis."""
        return {
            "vacancy_rate": f"{self.market_assumptions['default_vacancy_rate']:.1%}",
            "property_management": f"{self.market_assumptions['default_property_management']:.1%}",
            "maintenance_reserve": f"{self.market_assumptions['default_maintenance_reserve']:.1%}",
            "appreciation_rate": f"{self.market_assumptions['default_appreciation_rate']:.1%}",
            "rent_growth_rate": f"{self.market_assumptions['default_rent_growth_rate']:.1%}",
            "analysis_date": datetime.utcnow().isoformat(),
            "disclaimer": "Analysis based on provided inputs and market assumptions. Actual results may vary."
        }
    
    async def _publish_analysis_update(self, report: UnderwritingReport):
        """Publish real-time update about analysis completion."""
        try:
            websocket_manager = get_websocket_manager()
            if websocket_manager:
                await websocket_manager.broadcast_to_all({
                    "type": "underwriting_complete",
                    "property_id": report.property_id,
                    "property_address": report.property_address,
                    "monthly_cash_flow": report.cash_flow_analysis.monthly_cash_flow,
                    "cash_on_cash_return": report.cash_flow_analysis.cash_on_cash_return,
                    "risk_rating": report.risk_rating,
                    "investment_recommendation": report.investment_recommendation,
                    "confidence_score": report.confidence_score
                })
            
            # Publish to Redis
            await publish_event("agent_activity", "underwriting_complete", {
                "agent_id": self.agent_id,
                "report_summary": {
                    "property_id": report.property_id,
                    "cash_flow": report.cash_flow_analysis.monthly_cash_flow,
                    "returns": report.cash_flow_analysis.cash_on_cash_return,
                    "risk_rating": report.risk_rating
                }
            })
            
        except Exception as e:
            logger.warning(f"Failed to publish analysis update: {e}")
    
    async def calculate_brrrr_analysis(self, property_data: Dict[str, Any], financial_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate BRRRR (Buy, Rehab, Rent, Refinance, Repeat) analysis."""
        try:
            purchase_price = financial_inputs.get("purchase_price", 0)
            renovation_cost = financial_inputs.get("renovation_cost", 0)
            after_repair_value = financial_inputs.get("after_repair_value", 0)
            monthly_rent = financial_inputs.get("monthly_rent", 0)
            
            # Calculate total invested
            total_invested = purchase_price + renovation_cost + (purchase_price * 0.03)  # Add closing costs
            
            # Calculate refinance potential (typically 75% LTV)
            refinance_loan = after_repair_value * 0.75
            cash_recovered = refinance_loan - purchase_price
            cash_left_in_deal = total_invested - cash_recovered
            
            # Calculate post-refinance cash flow
            refinance_payment = self._calculate_monthly_payment(refinance_loan, 0.07, 30)
            
            # Monthly expenses (estimated)
            monthly_expenses = (
                (after_repair_value * 0.015 / 12) +  # Property taxes
                (after_repair_value * 0.004 / 12) +  # Insurance
                (monthly_rent * 0.05) +  # Maintenance
                (monthly_rent * 0.05)    # Vacancy
            )
            
            monthly_cash_flow = monthly_rent - refinance_payment - monthly_expenses
            
            # Calculate infinite return if no cash left in deal
            if cash_left_in_deal <= 0:
                cash_on_cash_return = float('inf')
            else:
                cash_on_cash_return = (monthly_cash_flow * 12) / cash_left_in_deal
            
            return {
                "total_invested": total_invested,
                "after_repair_value": after_repair_value,
                "refinance_loan_amount": refinance_loan,
                "cash_recovered": cash_recovered,
                "cash_left_in_deal": cash_left_in_deal,
                "monthly_cash_flow_post_refinance": monthly_cash_flow,
                "cash_on_cash_return": cash_on_cash_return,
                "strategy_viability": "Excellent" if cash_left_in_deal <= 0 else "Good" if cash_on_cash_return > 0.15 else "Fair"
            }
            
        except Exception as e:
            logger.error(f"BRRRR analysis failed: {e}")
            return {}
    
    def _calculate_monthly_payment(self, loan_amount: float, interest_rate: float, term_years: int) -> float:
        """Calculate monthly mortgage payment."""
        monthly_rate = interest_rate / 12
        num_payments = term_years * 12
        
        if monthly_rate > 0:
            return loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        else:
            return loan_amount / num_payments
    
    async def analyze_flip_potential(self, property_data: Dict[str, Any], financial_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fix-and-flip potential."""
        try:
            purchase_price = financial_inputs.get("purchase_price", 0)
            renovation_cost = financial_inputs.get("renovation_cost", 0)
            after_repair_value = financial_inputs.get("after_repair_value", 0)
            holding_period_months = financial_inputs.get("holding_period_months", 6)
            
            # Calculate costs
            acquisition_costs = purchase_price * 0.03  # Closing costs
            carrying_costs = purchase_price * 0.01 * (holding_period_months / 12)  # 1% per year
            selling_costs = after_repair_value * 0.08  # 8% for agent, closing, etc.
            
            total_costs = purchase_price + renovation_cost + acquisition_costs + carrying_costs + selling_costs
            
            # Calculate profit
            gross_profit = after_repair_value - total_costs
            profit_margin = gross_profit / after_repair_value if after_repair_value > 0 else 0
            
            # Calculate annualized return
            annualized_return = (gross_profit / (purchase_price + renovation_cost)) * (12 / holding_period_months)
            
            return {
                "purchase_price": purchase_price,
                "renovation_cost": renovation_cost,
                "after_repair_value": after_repair_value,
                "total_costs": total_costs,
                "gross_profit": gross_profit,
                "profit_margin": profit_margin,
                "annualized_return": annualized_return,
                "holding_period_months": holding_period_months,
                "recommendation": "Strong Flip" if profit_margin > 0.2 else "Good Flip" if profit_margin > 0.15 else "Marginal Flip" if profit_margin > 0.1 else "Poor Flip"
            }
            
        except Exception as e:
            logger.error(f"Flip analysis failed: {e}")
            return {}

# Global instance
_underwriting_agent = None

def get_underwriting_agent() -> AutomatedUnderwritingAgent:
    """Get global underwriting agent instance."""
    global _underwriting_agent
    if _underwriting_agent is None:
        _underwriting_agent = AutomatedUnderwritingAgent()
    return _underwriting_agent

async def underwriting_agent_handler(task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler function for underwriting agent tasks."""
    agent = get_underwriting_agent()
    
    if not agent.is_initialized:
        raise RuntimeError("Automated Underwriting Agent not properly initialized")
    
    if task_type == "generate_report":
        report = await agent.generate_underwriting_report(
            property_data=task_data.get("property_data", {}),
            financial_inputs=task_data.get("financial_inputs", {}),
            investment_strategy=InvestmentStrategy(task_data.get("investment_strategy", "buy_and_hold"))
        )
        return {"underwriting_report": report.__dict__}
    
    elif task_type == "brrrr_analysis":
        result = await agent.calculate_brrrr_analysis(
            property_data=task_data.get("property_data", {}),
            financial_inputs=task_data.get("financial_inputs", {})
        )
        return {"brrrr_analysis": result}
    
    elif task_type == "flip_analysis":
        result = await agent.analyze_flip_potential(
            property_data=task_data.get("property_data", {}),
            financial_inputs=task_data.get("financial_inputs", {})
        )
        return {"flip_analysis": result}
    
    else:
        raise ValueError(f"Unknown task type: {task_type}")