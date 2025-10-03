from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import json

from core.database import get_db
from models.property_scan import (
    PropertyScan, ScannedProperty, PropertyScanCreate, 
    PropertyScanUpdate, PropertyScanResponse, ScannedPropertyResponse,
    ScanCriteria, ScanProgress, ScanStatus, PropertyType, InvestmentPotential
)
from models.user import User
from core.redis_client import publish_event

router = APIRouter()

# Mock property data sources - in production, these would be real APIs
MOCK_PROPERTY_DATA = [
    {
        "address": "123 Main St, San Francisco, CA 94102",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94102",
        "property_type": "residential",
        "bedrooms": 3,
        "bathrooms": 2.5,
        "square_feet": 1800,
        "list_price": 1200000,
        "year_built": 1995,
        "days_on_market": 45,
        "price_reductions": 2,
        "is_foreclosure": False,
        "is_short_sale": False,
        "is_bank_owned": False
    },
    {
        "address": "456 Oak Ave, Oakland, CA 94601",
        "city": "Oakland",
        "state": "CA",
        "zip_code": "94601",
        "property_type": "residential",
        "bedrooms": 4,
        "bathrooms": 3,
        "square_feet": 2200,
        "list_price": 850000,
        "year_built": 1988,
        "days_on_market": 120,
        "price_reductions": 4,
        "is_foreclosure": True,
        "is_short_sale": False,
        "is_bank_owned": False
    },
    {
        "address": "789 Commercial Blvd, San Jose, CA 95110",
        "city": "San Jose",
        "state": "CA",
        "zip_code": "95110",
        "property_type": "commercial",
        "bedrooms": 0,
        "bathrooms": 2,
        "square_feet": 5000,
        "list_price": 2500000,
        "year_built": 2010,
        "days_on_market": 30,
        "price_reductions": 1,
        "is_foreclosure": False,
        "is_short_sale": True,
        "is_bank_owned": False
    }
]

async def analyze_property(property_data: dict) -> dict:
    """AI-powered property analysis"""
    # Mock AI analysis - in production, this would use real ML models
    analysis = {
        "estimated_value": property_data["list_price"] * 0.95,
        "price_per_sqft": property_data["list_price"] / property_data["square_feet"],
        "investment_potential": "medium",
        "roi_estimate": 8.5,
        "cap_rate": 6.2,
        "cash_flow_estimate": 2500,
        "appreciation_potential": 5.5,
        "is_distressed": property_data.get("is_foreclosure", False) or 
                        property_data.get("is_short_sale", False) or
                        property_data.get("is_bank_owned", False),
        "is_undervalued": property_data["list_price"] < property_data["list_price"] * 0.9,
        "ai_confidence_score": 0.85,
        "ai_analysis": f"Property shows {property_data['days_on_market']} days on market with {property_data['price_reductions']} price reductions. Market analysis suggests moderate investment potential.",
        "risk_factors": ["High days on market", "Multiple price reductions"] if property_data["days_on_market"] > 90 else [],
        "opportunity_factors": ["Good location", "Reasonable price per sqft"] if property_data["list_price"] / property_data["square_feet"] < 1000 else []
    }
    
    # Determine investment potential based on analysis
    if analysis["roi_estimate"] > 12 and analysis["is_undervalued"]:
        analysis["investment_potential"] = "very_high"
    elif analysis["roi_estimate"] > 10:
        analysis["investment_potential"] = "high"
    elif analysis["roi_estimate"] > 7:
        analysis["investment_potential"] = "medium"
    else:
        analysis["investment_potential"] = "low"
    
    return analysis

async def scan_properties_task(scan_id: int, criteria: dict, max_properties: int, db: Session):
    """Background task to scan properties"""
    try:
        # Update scan status to running
        scan = db.query(PropertyScan).filter(PropertyScan.id == scan_id).first()
        if not scan:
            return
        
        scan.status = ScanStatus.RUNNING
        scan.started_at = datetime.utcnow()
        db.commit()
        
        # Publish progress update
        await publish_event("property_scans", "scan_started", {
            "scan_id": scan_id,
            "status": "running"
        })
        
        properties_scanned = 0
        properties_found = 0
        high_potential_count = 0
        distressed_count = 0
        undervalued_count = 0
        
        # Simulate scanning properties
        for i, property_data in enumerate(MOCK_PROPERTY_DATA * 100):  # Simulate scanning more properties
            if properties_scanned >= max_properties:
                break
                
            # Apply search criteria filters
            if not matches_criteria(property_data, criteria):
                continue
                
            # Analyze property with AI
            analysis = await analyze_property(property_data)
            
            # Create scanned property record
            scanned_property = ScannedProperty(
                scan_id=scan_id,
                address=property_data["address"],
                city=property_data["city"],
                state=property_data["state"],
                zip_code=property_data["zip_code"],
                property_type=property_data["property_type"],
                bedrooms=property_data.get("bedrooms"),
                bathrooms=property_data.get("bathrooms"),
                square_feet=property_data["square_feet"],
                list_price=property_data["list_price"],
                year_built=property_data.get("year_built"),
                days_on_market=property_data.get("days_on_market", 0),
                price_reductions=property_data.get("price_reductions", 0),
                is_foreclosure=property_data.get("is_foreclosure", False),
                is_short_sale=property_data.get("is_short_sale", False),
                is_bank_owned=property_data.get("is_bank_owned", False),
                **analysis
            )
            
            db.add(scanned_property)
            properties_scanned += 1
            properties_found += 1
            
            # Update counters
            if analysis["investment_potential"] in ["high", "very_high"]:
                high_potential_count += 1
            if analysis["is_distressed"]:
                distressed_count += 1
            if analysis["is_undervalued"]:
                undervalued_count += 1
            
            # Commit every 10 properties
            if properties_scanned % 10 == 0:
                db.commit()
                
                # Publish progress update
                progress = {
                    "scan_id": scan_id,
                    "status": "running",
                    "total_properties": max_properties,
                    "scanned_count": properties_scanned,
                    "found_count": properties_found,
                    "progress_percentage": (properties_scanned / max_properties) * 100,
                    "current_location": property_data["city"]
                }
                await publish_event("property_scans", "scan_progress", progress)
            
            # Simulate processing time
            await asyncio.sleep(0.1)
        
        # Update scan with final results
        scan.status = ScanStatus.COMPLETED
        scan.completed_at = datetime.utcnow()
        scan.total_scanned = properties_scanned
        scan.properties_found = properties_found
        scan.high_potential_count = high_potential_count
        scan.distressed_count = distressed_count
        scan.undervalued_count = undervalued_count
        db.commit()
        
        # Publish completion event
        await publish_event("property_scans", "scan_completed", {
            "scan_id": scan_id,
            "status": "completed",
            "total_scanned": properties_scanned,
            "properties_found": properties_found,
            "high_potential_count": high_potential_count,
            "distressed_count": distressed_count,
            "undervalued_count": undervalued_count
        })
        
    except Exception as e:
        # Update scan status to failed
        scan = db.query(PropertyScan).filter(PropertyScan.id == scan_id).first()
        if scan:
            scan.status = ScanStatus.FAILED
            scan.completed_at = datetime.utcnow()
            db.commit()
        
        await publish_event("property_scans", "scan_failed", {
            "scan_id": scan_id,
            "status": "failed",
            "error": str(e)
        })

def matches_criteria(property_data: dict, criteria: dict) -> bool:
    """Check if property matches search criteria"""
    # Location filters
    if criteria.get("city") and property_data["city"].lower() != criteria["city"].lower():
        return False
    
    if criteria.get("state") and property_data["state"].lower() != criteria["state"].lower():
        return False
    
    if criteria.get("zip_codes") and property_data["zip_code"] not in criteria["zip_codes"]:
        return False
    
    # Property type filters
    if criteria.get("property_types") and property_data["property_type"] not in criteria["property_types"]:
        return False
    
    # Price filters
    if criteria.get("min_price") and property_data["list_price"] < criteria["min_price"]:
        return False
    
    if criteria.get("max_price") and property_data["list_price"] > criteria["max_price"]:
        return False
    
    # Square footage filters
    if criteria.get("min_sqft") and property_data["square_feet"] < criteria["min_sqft"]:
        return False
    
    if criteria.get("max_sqft") and property_data["square_feet"] > criteria["max_sqft"]:
        return False
    
    # Bedroom filters
    if criteria.get("min_bedrooms") and property_data.get("bedrooms", 0) < criteria["min_bedrooms"]:
        return False
    
    if criteria.get("max_bedrooms") and property_data.get("bedrooms", 0) > criteria["max_bedrooms"]:
        return False
    
    # Distress filters
    if criteria.get("include_distressed", True):
        if not (property_data.get("is_foreclosure", False) or 
                property_data.get("is_short_sale", False) or 
                property_data.get("is_bank_owned", False)):
            return False
    
    return True

@router.post("/scans", response_model=PropertyScanResponse)
async def create_property_scan(
    scan_data: PropertyScanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new property scan"""
    # Create scan record
    scan = PropertyScan(
        name=scan_data.name,
        description=scan_data.description,
        search_criteria=scan_data.search_criteria,
        max_properties=scan_data.max_properties,
        scan_radius_miles=scan_data.scan_radius_miles,
        user_id=1  # In production, get from authenticated user
    )
    
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    # Start background scanning task
    background_tasks.add_task(
        scan_properties_task,
        scan.id,
        scan_data.search_criteria,
        scan_data.max_properties,
        db
    )
    
    return scan

@router.get("/scans", response_model=List[PropertyScanResponse])
async def get_property_scans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ScanStatus] = None,
    db: Session = Depends(get_db)
):
    """Get all property scans with optional filtering"""
    query = db.query(PropertyScan)
    
    if status:
        query = query.filter(PropertyScan.status == status)
    
    scans = query.offset(skip).limit(limit).all()
    return scans

@router.get("/scans/{scan_id}", response_model=PropertyScanResponse)
async def get_property_scan(scan_id: int, db: Session = Depends(get_db)):
    """Get a specific property scan"""
    scan = db.query(PropertyScan).filter(PropertyScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Property scan not found")
    return scan

@router.put("/scans/{scan_id}", response_model=PropertyScanResponse)
async def update_property_scan(
    scan_id: int,
    scan_update: PropertyScanUpdate,
    db: Session = Depends(get_db)
):
    """Update a property scan"""
    scan = db.query(PropertyScan).filter(PropertyScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Property scan not found")
    
    for field, value in scan_update.dict(exclude_unset=True).items():
        setattr(scan, field, value)
    
    db.commit()
    db.refresh(scan)
    return scan

@router.delete("/scans/{scan_id}")
async def delete_property_scan(scan_id: int, db: Session = Depends(get_db)):
    """Delete a property scan"""
    scan = db.query(PropertyScan).filter(PropertyScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Property scan not found")
    
    db.delete(scan)
    db.commit()
    return {"message": "Property scan deleted successfully"}

@router.get("/scans/{scan_id}/properties", response_model=List[ScannedPropertyResponse])
async def get_scanned_properties(
    scan_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    investment_potential: Optional[InvestmentPotential] = None,
    is_distressed: Optional[bool] = None,
    is_undervalued: Optional[bool] = None,
    min_roi: Optional[float] = None,
    max_roi: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get scanned properties with filtering options"""
    query = db.query(ScannedProperty).filter(ScannedProperty.scan_id == scan_id)
    
    if investment_potential:
        query = query.filter(ScannedProperty.investment_potential == investment_potential)
    
    if is_distressed is not None:
        query = query.filter(ScannedProperty.is_distressed == is_distressed)
    
    if is_undervalued is not None:
        query = query.filter(ScannedProperty.is_undervalued == is_undervalued)
    
    if min_roi is not None:
        query = query.filter(ScannedProperty.roi_estimate >= min_roi)
    
    if max_roi is not None:
        query = query.filter(ScannedProperty.roi_estimate <= max_roi)
    
    properties = query.offset(skip).limit(limit).all()
    return properties

@router.get("/scans/{scan_id}/progress", response_model=ScanProgress)
async def get_scan_progress(scan_id: int, db: Session = Depends(get_db)):
    """Get real-time scan progress"""
    scan = db.query(PropertyScan).filter(PropertyScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Property scan not found")
    
    progress_percentage = 0
    if scan.max_properties > 0:
        progress_percentage = (scan.total_scanned / scan.max_properties) * 100
    
    estimated_completion = None
    if scan.status == ScanStatus.RUNNING and scan.started_at:
        # Simple estimation based on current progress
        elapsed = datetime.utcnow() - scan.started_at
        if scan.total_scanned > 0:
            rate = scan.total_scanned / elapsed.total_seconds()
            remaining = (scan.max_properties - scan.total_scanned) / rate
            estimated_completion = datetime.utcnow() + timedelta(seconds=remaining)
    
    return ScanProgress(
        scan_id=scan_id,
        status=scan.status,
        total_properties=scan.max_properties,
        scanned_count=scan.total_scanned,
        found_count=scan.properties_found,
        progress_percentage=progress_percentage,
        estimated_completion=estimated_completion
    )

@router.post("/scans/{scan_id}/cancel")
async def cancel_property_scan(scan_id: int, db: Session = Depends(get_db)):
    """Cancel a running property scan"""
    scan = db.query(PropertyScan).filter(PropertyScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Property scan not found")
    
    if scan.status not in [ScanStatus.PENDING, ScanStatus.RUNNING]:
        raise HTTPException(status_code=400, detail="Scan cannot be cancelled in current status")
    
    scan.status = ScanStatus.CANCELLED
    scan.completed_at = datetime.utcnow()
    db.commit()
    
    await publish_event("property_scans", "scan_cancelled", {
        "scan_id": scan_id,
        "status": "cancelled"
    })
    
    return {"message": "Property scan cancelled successfully"}

@router.get("/scans/{scan_id}/export")
async def export_scan_results(scan_id: int, format: str = "json", db: Session = Depends(get_db)):
    """Export scan results in various formats"""
    scan = db.query(PropertyScan).filter(PropertyScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Property scan not found")
    
    properties = db.query(ScannedProperty).filter(ScannedProperty.scan_id == scan_id).all()
    
    if format == "json":
        return {
            "scan": scan,
            "properties": properties
        }
    elif format == "csv":
        # In production, generate actual CSV
        return {"message": "CSV export not implemented yet"}
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")
