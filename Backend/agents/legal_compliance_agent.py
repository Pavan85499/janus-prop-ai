"""
Legal & Compliance Agent for Janus Prop AI Backend

This agent specializes in automated review of ownership, zoning, permits, liens, 
tax history and generates reports for legal validation.
"""

import asyncio
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import re
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

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_VERIFICATION = "pending_verification"
    REQUIRES_ATTENTION = "requires_attention"
    UNKNOWN = "unknown"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class OwnershipRecord:
    """Property ownership information."""
    current_owner: str
    owner_type: str  # "individual", "corporation", "trust", "llc"
    ownership_percentage: float
    acquisition_date: datetime
    deed_type: str
    recording_info: Dict[str, str]
    previous_owners: List[Dict[str, Any]]
    chain_of_title_clear: bool
    ownership_disputes: List[str]
    power_of_attorney: Optional[str]

@dataclass
class LienRecord:
    """Property lien information."""
    lien_type: str  # "mortgage", "tax", "mechanic", "judgment", "hoa"
    lien_holder: str
    amount: float
    recorded_date: datetime
    priority: int
    status: str  # "active", "satisfied", "partial"
    satisfaction_date: Optional[datetime]
    legal_description: str
    recording_reference: str

@dataclass
class ZoningInfo:
    """Property zoning information."""
    current_zoning: str
    zoning_description: str
    permitted_uses: List[str]
    setback_requirements: Dict[str, float]
    height_restrictions: Dict[str, Any]
    density_limits: Dict[str, Any]
    parking_requirements: Dict[str, int]
    special_conditions: List[str]
    pending_zoning_changes: List[Dict[str, Any]]
    variance_history: List[Dict[str, Any]]

@dataclass
class PermitRecord:
    """Building permit information."""
    permit_number: str
    permit_type: str  # "building", "electrical", "plumbing", "mechanical", "demo"
    issue_date: datetime
    expiration_date: Optional[datetime]
    status: str  # "issued", "expired", "pending", "approved", "rejected"
    work_description: str
    contractor: Optional[str]
    valuation: Optional[float]
    inspections_required: List[str]
    inspections_completed: List[Dict[str, Any]]
    final_approval: Optional[datetime]

@dataclass
class TaxRecord:
    """Property tax information."""
    tax_year: int
    assessed_value: float
    taxable_value: float
    annual_tax_amount: float
    payment_status: str  # "current", "delinquent", "paid", "pending"
    payment_due_date: datetime
    last_payment_date: Optional[datetime]
    exemptions: List[str]
    assessor_notes: List[str]
    appeal_history: List[Dict[str, Any]]

@dataclass
class EnvironmentalRecord:
    """Environmental compliance information."""
    environmental_reports: List[str]
    hazmat_concerns: List[str]
    flood_zone: str
    wetlands_proximity: bool
    contamination_history: List[Dict[str, Any]]
    environmental_liens: List[str]
    regulatory_violations: List[Dict[str, Any]]
    cleanup_orders: List[Dict[str, Any]]

@dataclass
class ComplianceIssue:
    """Individual compliance issue."""
    issue_type: str
    severity: RiskLevel
    description: str
    legal_implications: str
    recommended_action: str
    estimated_cost: Optional[float]
    timeline_to_resolve: str
    responsible_party: str
    supporting_documents: List[str]

@dataclass
class LegalComplianceReport:
    """Comprehensive legal compliance report."""
    property_id: str
    property_address: str
    report_date: datetime
    ownership_analysis: OwnershipRecord
    lien_analysis: List[LienRecord]
    zoning_analysis: ZoningInfo
    permit_analysis: List[PermitRecord]
    tax_analysis: List[TaxRecord]
    environmental_analysis: EnvironmentalRecord
    compliance_issues: List[ComplianceIssue]
    overall_compliance_status: ComplianceStatus
    risk_assessment: RiskLevel
    legal_recommendations: List[str]
    due_diligence_checklist: Dict[str, bool]
    confidence_score: float

class LegalComplianceAgent:
    """AI Agent specialized in legal and compliance analysis."""
    
    def __init__(self):
        self.agent_id = "legal_compliance_agent"
        self.name = "Legal Compliance Agent"
        self.settings = get_settings()
        self.gemini_api_key = self.settings.GEMINI_API_KEY
        self.is_initialized = False
        
        # Legal knowledge base patterns
        self.red_flag_patterns = {
            "ownership": [
                r"quit.?claim deed",
                r"ownership dispute",
                r"foreclosure",
                r"bankruptcy",
                r"estate sale",
                r"power of attorney",
                r"guardianship"
            ],
            "liens": [
                r"tax lien",
                r"irs lien",
                r"judgment lien",
                r"mechanic.?lien",
                r"hoa lien",
                r"child support",
                r"unsatisfied"
            ],
            "zoning": [
                r"non.?conforming",
                r"variance required",
                r"zoning violation",
                r"code violation",
                r"pending rezoning",
                r"grandfathered use"
            ],
            "environmental": [
                r"contamination",
                r"hazardous material",
                r"asbestos",
                r"lead paint",
                r"underground storage",
                r"brownfield",
                r"superfund"
            ]
        }
        
        # Compliance requirements by property type
        self.compliance_requirements = {
            "residential": [
                "building_permits",
                "occupancy_permits",
                "zoning_compliance",
                "tax_compliance",
                "title_clear",
                "environmental_clear"
            ],
            "commercial": [
                "building_permits",
                "business_license",
                "zoning_compliance",
                "ada_compliance",
                "fire_safety",
                "environmental_compliance",
                "tax_compliance",
                "title_clear"
            ],
            "multi_family": [
                "building_permits",
                "rental_license",
                "zoning_compliance",
                "habitability_standards",
                "fire_safety",
                "tax_compliance",
                "title_clear"
            ]
        }
        
        if self._has_required_libraries():
            self._initialize_agent()
    
    def _has_required_libraries(self) -> bool:
        """Check if required libraries are available."""
        return bool(self.gemini_api_key)
    
    def _initialize_agent(self):
        """Initialize the legal compliance agent."""
        try:
            if GEMINI_AVAILABLE and self.gemini_api_key:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel("gemini-pro")
                self.chat_model = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.gemini_api_key,
                    temperature=0.1,  # Very low temperature for legal accuracy
                    max_output_tokens=4096
                )
            
            self.is_initialized = True
            logger.info("Legal Compliance Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Legal Compliance Agent: {e}")
            self.is_initialized = False
    
    async def generate_compliance_report(
        self,
        property_data: Dict[str, Any],
        legal_documents: Optional[List[Dict[str, Any]]] = None
    ) -> LegalComplianceReport:
        """
        Generate comprehensive legal compliance report for a property.
        
        Args:
            property_data: Property details (address, type, parcel number, etc.)
            legal_documents: Optional legal documents to analyze
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Analyze ownership
            ownership_analysis = await self._analyze_ownership(property_data, legal_documents)
            
            # Step 2: Analyze liens
            lien_analysis = await self._analyze_liens(property_data)
            
            # Step 3: Analyze zoning
            zoning_analysis = await self._analyze_zoning(property_data)
            
            # Step 4: Analyze permits
            permit_analysis = await self._analyze_permits(property_data)
            
            # Step 5: Analyze tax records
            tax_analysis = await self._analyze_tax_records(property_data)
            
            # Step 6: Analyze environmental issues
            environmental_analysis = await self._analyze_environmental(property_data)
            
            # Step 7: Identify compliance issues
            compliance_issues = await self._identify_compliance_issues(
                ownership_analysis, lien_analysis, zoning_analysis,
                permit_analysis, tax_analysis, environmental_analysis
            )
            
            # Step 8: Determine overall compliance status
            overall_status = self._determine_overall_compliance(compliance_issues)
            
            # Step 9: Assess risk level
            risk_level = self._assess_risk_level(compliance_issues)
            
            # Step 10: Generate legal recommendations
            legal_recommendations = await self._generate_legal_recommendations(
                compliance_issues, property_data
            )
            
            # Step 11: Create due diligence checklist
            due_diligence_checklist = self._create_due_diligence_checklist(
                property_data, compliance_issues
            )
            
            # Create comprehensive report
            report = LegalComplianceReport(
                property_id=property_data.get("id", ""),
                property_address=property_data.get("address", ""),
                report_date=start_time,
                ownership_analysis=ownership_analysis,
                lien_analysis=lien_analysis,
                zoning_analysis=zoning_analysis,
                permit_analysis=permit_analysis,
                tax_analysis=tax_analysis,
                environmental_analysis=environmental_analysis,
                compliance_issues=compliance_issues,
                overall_compliance_status=overall_status,
                risk_assessment=risk_level,
                legal_recommendations=legal_recommendations,
                due_diligence_checklist=due_diligence_checklist,
                confidence_score=self._calculate_confidence_score(property_data, legal_documents)
            )
            
            # Cache the report
            await cache_set(f"legal_compliance_report:{property_data.get('id', 'unknown')}", 
                          report.__dict__, expire=7200)
            
            # Publish real-time update
            await self._publish_compliance_update(report)
            
            logger.info(f"Legal compliance report generated for {property_data.get('address', 'unknown')}")
            return report
            
        except Exception as e:
            logger.error(f"Legal compliance analysis failed: {e}")
            raise
    
    async def _analyze_ownership(self, property_data: Dict[str, Any], legal_documents: Optional[List[Dict[str, Any]]]) -> OwnershipRecord:
        """Analyze property ownership structure and history."""
        # Mock ownership analysis - replace with real title/deed research
        return OwnershipRecord(
            current_owner=property_data.get("owner", "Unknown Owner"),
            owner_type="individual",
            ownership_percentage=100.0,
            acquisition_date=datetime(2020, 1, 1),
            deed_type="warranty_deed",
            recording_info={
                "book": "1234",
                "page": "567",
                "instrument": "202012345678"
            },
            previous_owners=[
                {
                    "name": "Previous Owner",
                    "ownership_period": "2015-2020",
                    "deed_type": "warranty_deed"
                }
            ],
            chain_of_title_clear=True,
            ownership_disputes=[],
            power_of_attorney=None
        )
    
    async def _analyze_liens(self, property_data: Dict[str, Any]) -> List[LienRecord]:
        """Analyze property liens and encumbrances."""
        # Mock lien analysis - replace with real public records search
        liens = []
        
        # Example mortgage lien
        liens.append(LienRecord(
            lien_type="mortgage",
            lien_holder="First National Bank",
            amount=150000.0,
            recorded_date=datetime(2020, 1, 15),
            priority=1,
            status="active",
            satisfaction_date=None,
            legal_description="Lot 123, Block 4, Subdivision Name",
            recording_reference="Book 1234, Page 567"
        ))
        
        # Check for potential tax liens
        if property_data.get("tax_delinquent", False):
            liens.append(LienRecord(
                lien_type="tax",
                lien_holder="County Tax Assessor",
                amount=5000.0,
                recorded_date=datetime(2023, 1, 1),
                priority=0,  # Tax liens typically have first priority
                status="active",
                satisfaction_date=None,
                legal_description="Tax Parcel " + str(property_data.get("parcel_number", "")),
                recording_reference="Tax Roll 2023"
            ))
        
        return liens
    
    async def _analyze_zoning(self, property_data: Dict[str, Any]) -> ZoningInfo:
        """Analyze zoning compliance and restrictions."""
        # Mock zoning analysis - replace with real zoning lookup
        property_type = property_data.get("property_type", "residential")
        
        if property_type == "residential":
            zoning = "R-1"
            description = "Single Family Residential"
            permitted_uses = ["single family dwelling", "home office", "accessory structures"]
        elif property_type == "commercial":
            zoning = "C-1"
            description = "Neighborhood Commercial"
            permitted_uses = ["retail", "office", "restaurant", "service business"]
        else:
            zoning = "R-2"
            description = "Multi-Family Residential"
            permitted_uses = ["multi-family dwelling", "duplex", "apartment"]
        
        return ZoningInfo(
            current_zoning=zoning,
            zoning_description=description,
            permitted_uses=permitted_uses,
            setback_requirements={
                "front": 25.0,
                "rear": 10.0,
                "side": 5.0
            },
            height_restrictions={
                "max_height": 35.0,
                "max_stories": 2
            },
            density_limits={
                "max_units_per_acre": 8 if property_type != "residential" else 1
            },
            parking_requirements={
                "spaces_per_unit": 2 if property_type == "residential" else 1
            },
            special_conditions=[],
            pending_zoning_changes=[],
            variance_history=[]
        )
    
    async def _analyze_permits(self, property_data: Dict[str, Any]) -> List[PermitRecord]:
        """Analyze building permits and code compliance."""
        # Mock permit analysis - replace with real permit lookup
        permits = []
        
        # Example building permit
        permits.append(PermitRecord(
            permit_number="BP-2020-001234",
            permit_type="building",
            issue_date=datetime(2020, 6, 1),
            expiration_date=datetime(2021, 6, 1),
            status="approved",
            work_description="Kitchen remodel",
            contractor="ABC Construction LLC",
            valuation=25000.0,
            inspections_required=["rough", "final"],
            inspections_completed=[
                {"type": "rough", "date": "2020-07-15", "result": "passed"},
                {"type": "final", "date": "2020-08-30", "result": "passed"}
            ],
            final_approval=datetime(2020, 8, 30)
        ))
        
        return permits
    
    async def _analyze_tax_records(self, property_data: Dict[str, Any]) -> List[TaxRecord]:
        """Analyze property tax compliance."""
        # Mock tax analysis - replace with real tax record lookup
        tax_records = []
        
        for year in [2021, 2022, 2023]:
            assessed_value = property_data.get("assessed_value", 200000) * (1 + (year - 2021) * 0.03)
            annual_tax = assessed_value * 0.015  # 1.5% tax rate
            
            tax_records.append(TaxRecord(
                tax_year=year,
                assessed_value=assessed_value,
                taxable_value=assessed_value,
                annual_tax_amount=annual_tax,
                payment_status="current" if year < 2024 else "pending",
                payment_due_date=datetime(year, 12, 31),
                last_payment_date=datetime(year, 11, 15) if year < 2024 else None,
                exemptions=["homestead"] if property_data.get("owner_occupied") else [],
                assessor_notes=[],
                appeal_history=[]
            ))
        
        return tax_records
    
    async def _analyze_environmental(self, property_data: Dict[str, Any]) -> EnvironmentalRecord:
        """Analyze environmental compliance and concerns."""
        # Mock environmental analysis - replace with real environmental database lookup
        year_built = property_data.get("year_built", 1980)
        
        hazmat_concerns = []
        if year_built < 1978:
            hazmat_concerns.append("Potential lead paint")
        if year_built < 1980:
            hazmat_concerns.append("Potential asbestos")
        
        return EnvironmentalRecord(
            environmental_reports=[],
            hazmat_concerns=hazmat_concerns,
            flood_zone=property_data.get("flood_zone", "X"),
            wetlands_proximity=False,
            contamination_history=[],
            environmental_liens=[],
            regulatory_violations=[],
            cleanup_orders=[]
        )
    
    async def _identify_compliance_issues(
        self,
        ownership: OwnershipRecord,
        liens: List[LienRecord],
        zoning: ZoningInfo,
        permits: List[PermitRecord],
        taxes: List[TaxRecord],
        environmental: EnvironmentalRecord
    ) -> List[ComplianceIssue]:
        """Identify compliance issues from analysis results."""
        issues = []
        
        # Check for ownership issues
        if not ownership.chain_of_title_clear:
            issues.append(ComplianceIssue(
                issue_type="ownership",
                severity=RiskLevel.HIGH,
                description="Chain of title issues detected",
                legal_implications="May affect marketability and insurability of title",
                recommended_action="Conduct thorough title examination and clear defects",
                estimated_cost=5000.0,
                timeline_to_resolve="30-60 days",
                responsible_party="Title attorney",
                supporting_documents=["title_report", "deed_records"]
            ))
        
        # Check for active liens
        active_liens = [lien for lien in liens if lien.status == "active"]
        if active_liens:
            total_lien_amount = sum(lien.amount for lien in active_liens)
            issues.append(ComplianceIssue(
                issue_type="liens",
                severity=RiskLevel.MEDIUM if total_lien_amount < 50000 else RiskLevel.HIGH,
                description=f"{len(active_liens)} active liens totaling ${total_lien_amount:,.2f}",
                legal_implications="Liens must be satisfied at closing or assumed by buyer",
                recommended_action="Negotiate lien satisfaction or payoff at closing",
                estimated_cost=total_lien_amount,
                timeline_to_resolve="At closing",
                responsible_party="Seller/Title company",
                supporting_documents=["lien_records", "payoff_statements"]
            ))
        
        # Check for expired permits
        expired_permits = [p for p in permits if p.status == "expired"]
        if expired_permits:
            issues.append(ComplianceIssue(
                issue_type="permits",
                severity=RiskLevel.MEDIUM,
                description=f"{len(expired_permits)} expired permits found",
                legal_implications="May indicate unpermitted work or code violations",
                recommended_action="Verify work completion and obtain final approvals",
                estimated_cost=2000.0,
                timeline_to_resolve="2-4 weeks",
                responsible_party="Property owner",
                supporting_documents=["permit_records", "inspection_reports"]
            ))
        
        # Check for tax delinquency
        delinquent_taxes = [t for t in taxes if t.payment_status == "delinquent"]
        if delinquent_taxes:
            total_delinquent = sum(t.annual_tax_amount for t in delinquent_taxes)
            issues.append(ComplianceIssue(
                issue_type="taxes",
                severity=RiskLevel.HIGH,
                description=f"Delinquent taxes of ${total_delinquent:,.2f}",
                legal_implications="Property may be subject to tax foreclosure",
                recommended_action="Pay delinquent taxes immediately",
                estimated_cost=total_delinquent * 1.2,  # Include penalties
                timeline_to_resolve="Immediate",
                responsible_party="Property owner",
                supporting_documents=["tax_records", "payment_history"]
            ))
        
        # Check for environmental concerns
        if environmental.hazmat_concerns:
            issues.append(ComplianceIssue(
                issue_type="environmental",
                severity=RiskLevel.MEDIUM,
                description=f"Environmental concerns: {', '.join(environmental.hazmat_concerns)}",
                legal_implications="May require disclosure and remediation",
                recommended_action="Conduct environmental assessment",
                estimated_cost=1500.0,
                timeline_to_resolve="1-2 weeks",
                responsible_party="Property owner",
                supporting_documents=["environmental_report"]
            ))
        
        return issues
    
    def _determine_overall_compliance(self, issues: List[ComplianceIssue]) -> ComplianceStatus:
        """Determine overall compliance status."""
        if not issues:
            return ComplianceStatus.COMPLIANT
        
        critical_issues = [i for i in issues if i.severity == RiskLevel.CRITICAL]
        high_issues = [i for i in issues if i.severity == RiskLevel.HIGH]
        
        if critical_issues:
            return ComplianceStatus.NON_COMPLIANT
        elif high_issues:
            return ComplianceStatus.REQUIRES_ATTENTION
        else:
            return ComplianceStatus.PENDING_VERIFICATION
    
    def _assess_risk_level(self, issues: List[ComplianceIssue]) -> RiskLevel:
        """Assess overall risk level."""
        if not issues:
            return RiskLevel.LOW
        
        max_severity = max(issue.severity for issue in issues)
        return max_severity
    
    async def _generate_legal_recommendations(self, issues: List[ComplianceIssue], property_data: Dict[str, Any]) -> List[str]:
        """Generate AI-powered legal recommendations."""
        if not issues:
            return ["Property appears to be in good legal standing with no major compliance issues identified."]
        
        recommendations = []
        
        # Group issues by type
        issue_types = {}
        for issue in issues:
            if issue.issue_type not in issue_types:
                issue_types[issue.issue_type] = []
            issue_types[issue.issue_type].append(issue)
        
        # Generate recommendations by issue type
        for issue_type, type_issues in issue_types.items():
            if issue_type == "ownership":
                recommendations.append("Engage a qualified title attorney to resolve ownership issues before proceeding.")
            elif issue_type == "liens":
                total_amount = sum(issue.estimated_cost or 0 for issue in type_issues)
                recommendations.append(f"Budget ${total_amount:,.0f} for lien satisfaction and obtain payoff statements.")
            elif issue_type == "permits":
                recommendations.append("Contact local building department to verify permit status and obtain required approvals.")
            elif issue_type == "taxes":
                recommendations.append("Immediately address tax delinquency to avoid foreclosure proceedings.")
            elif issue_type == "environmental":
                recommendations.append("Conduct Phase I Environmental Site Assessment to identify potential liabilities.")
        
        # Add general recommendations
        high_risk_issues = [i for i in issues if i.severity in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        if high_risk_issues:
            recommendations.append("Consider requiring seller to cure all high-risk issues before closing.")
            recommendations.append("Obtain appropriate title insurance coverage for identified risks.")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _create_due_diligence_checklist(self, property_data: Dict[str, Any], issues: List[ComplianceIssue]) -> Dict[str, bool]:
        """Create due diligence checklist based on property type and issues."""
        property_type = property_data.get("property_type", "residential")
        requirements = self.compliance_requirements.get(property_type, self.compliance_requirements["residential"])
        
        checklist = {}
        issue_types = set(issue.issue_type for issue in issues)
        
        for requirement in requirements:
            if requirement == "title_clear":
                checklist["Clear Title"] = "ownership" not in issue_types and "liens" not in issue_types
            elif requirement == "tax_compliance":
                checklist["Tax Compliance"] = "taxes" not in issue_types
            elif requirement == "zoning_compliance":
                checklist["Zoning Compliance"] = "zoning" not in issue_types
            elif requirement == "building_permits":
                checklist["Building Permits"] = "permits" not in issue_types
            elif requirement == "environmental_clear":
                checklist["Environmental Clear"] = "environmental" not in issue_types
            else:
                # Default to true for requirements we don't specifically check
                checklist[requirement.replace("_", " ").title()] = True
        
        return checklist
    
    def _calculate_confidence_score(self, property_data: Dict[str, Any], legal_documents: Optional[List[Dict[str, Any]]]) -> float:
        """Calculate confidence score for the legal analysis."""
        score = 0.5  # Base confidence
        
        # Property data completeness
        required_fields = ["address", "parcel_number", "owner", "property_type"]
        completeness = sum(1 for field in required_fields if property_data.get(field)) / len(required_fields)
        score += completeness * 0.3
        
        # Legal documents availability
        if legal_documents:
            score += min(0.3, len(legal_documents) * 0.1)
        
        # Public records access (mock - would be real in production)
        score += 0.2  # Assume we have good public records access
        
        return min(1.0, score)
    
    async def _publish_compliance_update(self, report: LegalComplianceReport):
        """Publish real-time update about compliance analysis completion."""
        try:
            websocket_manager = get_websocket_manager()
            if websocket_manager:
                await websocket_manager.broadcast_to_all({
                    "type": "legal_compliance_complete",
                    "property_id": report.property_id,
                    "property_address": report.property_address,
                    "compliance_status": report.overall_compliance_status.value,
                    "risk_level": report.risk_assessment.value,
                    "issues_count": len(report.compliance_issues),
                    "confidence_score": report.confidence_score
                })
            
            # Publish to Redis
            await publish_event("agent_activity", "legal_compliance_complete", {
                "agent_id": self.agent_id,
                "report_summary": {
                    "property_id": report.property_id,
                    "compliance_status": report.overall_compliance_status.value,
                    "risk_level": report.risk_assessment.value,
                    "issues_count": len(report.compliance_issues)
                }
            })
            
        except Exception as e:
            logger.warning(f"Failed to publish compliance update: {e}")
    
    async def check_title_issues(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Quick check for potential title issues."""
        try:
            issues = []
            
            # Check for common title red flags
            owner = property_data.get("owner", "").lower()
            if any(flag in owner for flag in ["estate", "trust", "deceased", "bankruptcy"]):
                issues.append("Potential estate or trust issues")
            
            # Check deed type
            deed_type = property_data.get("deed_type", "").lower()
            if "quitclaim" in deed_type:
                issues.append("Quitclaim deed may indicate title issues")
            
            # Check for tax liens
            if property_data.get("tax_delinquent", False):
                issues.append("Tax delinquency may result in liens")
            
            return {
                "title_issues_found": len(issues) > 0,
                "issues": issues,
                "recommendation": "Order title report" if issues else "Standard title insurance recommended"
            }
            
        except Exception as e:
            logger.error(f"Title check failed: {e}")
            return {"error": str(e)}
    
    async def verify_zoning_compliance(self, property_data: Dict[str, Any], intended_use: str) -> Dict[str, Any]:
        """Verify if intended use complies with zoning."""
        try:
            zoning_info = await self._analyze_zoning(property_data)
            
            is_compliant = intended_use.lower() in [use.lower() for use in zoning_info.permitted_uses]
            
            result = {
                "compliant": is_compliant,
                "current_zoning": zoning_info.current_zoning,
                "permitted_uses": zoning_info.permitted_uses,
                "intended_use": intended_use
            }
            
            if not is_compliant:
                result["recommendation"] = "Apply for variance or conditional use permit"
                result["alternatives"] = [
                    "Modify intended use to fit zoning",
                    "Apply for rezoning",
                    "Seek zoning variance"
                ]
            
            return result
            
        except Exception as e:
            logger.error(f"Zoning verification failed: {e}")
            return {"error": str(e)}
    
    async def estimate_compliance_costs(self, compliance_issues: List[ComplianceIssue]) -> Dict[str, Any]:
        """Estimate costs to resolve compliance issues."""
        try:
            total_cost = 0
            cost_breakdown = {}
            
            for issue in compliance_issues:
                cost = issue.estimated_cost or 0
                total_cost += cost
                
                if issue.issue_type not in cost_breakdown:
                    cost_breakdown[issue.issue_type] = 0
                cost_breakdown[issue.issue_type] += cost
            
            # Add buffer for unexpected costs
            contingency = total_cost * 0.2
            total_with_contingency = total_cost + contingency
            
            return {
                "total_estimated_cost": total_cost,
                "contingency_buffer": contingency,
                "total_with_contingency": total_with_contingency,
                "cost_breakdown": cost_breakdown,
                "timeline_estimate": self._estimate_resolution_timeline(compliance_issues)
            }
            
        except Exception as e:
            logger.error(f"Cost estimation failed: {e}")
            return {"error": str(e)}
    
    def _estimate_resolution_timeline(self, compliance_issues: List[ComplianceIssue]) -> str:
        """Estimate timeline to resolve all compliance issues."""
        if not compliance_issues:
            return "No issues to resolve"
        
        # Parse timeline strings and find the longest
        max_timeline = 0
        for issue in compliance_issues:
            timeline = issue.timeline_to_resolve.lower()
            if "immediate" in timeline:
                days = 1
            elif "week" in timeline:
                weeks = 1
                if "1-2" in timeline:
                    weeks = 2
                elif "2-4" in timeline:
                    weeks = 4
                days = weeks * 7
            elif "month" in timeline or "day" in timeline:
                if "30-60" in timeline:
                    days = 60
                elif "60-90" in timeline:
                    days = 90
                else:
                    days = 30
            else:
                days = 30  # Default
            
            max_timeline = max(max_timeline, days)
        
        if max_timeline <= 7:
            return "1 week"
        elif max_timeline <= 30:
            return "1 month"
        elif max_timeline <= 60:
            return "2 months"
        else:
            return "3+ months"

# Global instance
_legal_compliance_agent = None

def get_legal_compliance_agent() -> LegalComplianceAgent:
    """Get global legal compliance agent instance."""
    global _legal_compliance_agent
    if _legal_compliance_agent is None:
        _legal_compliance_agent = LegalComplianceAgent()
    return _legal_compliance_agent

async def legal_compliance_agent_handler(task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler function for legal compliance agent tasks."""
    agent = get_legal_compliance_agent()
    
    if not agent.is_initialized:
        raise RuntimeError("Legal Compliance Agent not properly initialized")
    
    if task_type == "generate_compliance_report":
        report = await agent.generate_compliance_report(
            property_data=task_data.get("property_data", {}),
            legal_documents=task_data.get("legal_documents")
        )
        return {"compliance_report": report.__dict__}
    
    elif task_type == "check_title":
        result = await agent.check_title_issues(
            property_data=task_data.get("property_data", {})
        )
        return {"title_check": result}
    
    elif task_type == "verify_zoning":
        result = await agent.verify_zoning_compliance(
            property_data=task_data.get("property_data", {}),
            intended_use=task_data.get("intended_use", "")
        )
        return {"zoning_verification": result}
    
    elif task_type == "estimate_costs":
        # Convert dict to ComplianceIssue objects
        issues_data = task_data.get("compliance_issues", [])
        issues = []  # In production, would properly deserialize
        
        result = await agent.estimate_compliance_costs(issues)
        return {"cost_estimate": result}
    
    else:
        raise ValueError(f"Unknown task type: {task_type}")