"""
Test script for Investment Opportunities API
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_investment_opportunities_api():
    """Test the investment opportunities API endpoints."""
    
    base_url = "http://localhost:8001"
    
    print("Testing Investment Opportunities API...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        async with aiohttp.ClientSession() as session:
            print("1. Testing Health Check...")
            async with session.get(f"{base_url}/api/v1/investment-opportunities/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✓ Health Check: {health_data}")
                else:
                    print(f"✗ Health Check failed: {response.status}")
                    return
    except Exception as e:
        print(f"✗ Health Check error: {e}")
        return
    
    # Test opportunities endpoint
    try:
        async with aiohttp.ClientSession() as session:
            print("\n2. Testing Investment Opportunities...")
            async with session.get(f"{base_url}/api/v1/investment-opportunities/opportunities?limit=5") as response:
                if response.status == 200:
                    opportunities_data = await response.json()
                    print(f"✓ Opportunities API: {len(opportunities_data['opportunities'])} properties found")
                    
                    # Display first property details
                    if opportunities_data['opportunities']:
                        first_prop = opportunities_data['opportunities'][0]
                        print(f"\nFirst Property Details:")
                        print(f"  Address: {first_prop['address']}")
                        print(f"  Price: ${first_prop['price']:,.2f}")
                        print(f"  Estimated Value: ${first_prop['estimated_value']:,.2f}")
                        print(f"  Equity Gain: ${first_prop['equity_gain']:,.2f} ({first_prop['equity_percentage']}%)")
                        print(f"  Janus Score: {first_prop['janus_score']}/100")
                        print(f"  Strategy: {first_prop['strategy']}")
                        print(f"  Risk Level: {first_prop['risk_level']}")
                        
                        print(f"\nAgent Insights:")
                        for insight in first_prop['agent_insights']:
                            print(f"  • {insight}")
                    
                    # Display summary
                    summary = opportunities_data['summary']
                    print(f"\nSummary:")
                    print(f"  Total Opportunities: {summary['total_opportunities']}")
                    print(f"  Average Price: ${summary['average_price']:,.2f}")
                    print(f"  Average Janus Score: {summary['average_janus_score']}")
                    print(f"  Average Cap Rate: {summary['average_cap_rate']}%")
                    
                else:
                    print(f"✗ Opportunities API failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error details: {error_text}")
                    
    except Exception as e:
        print(f"✗ Opportunities API error: {e}")

async def test_with_fallback():
    """Test the API with fallback data if the server isn't running."""
    print("\nTesting with fallback data...")
    print("=" * 50)
    
    # Generate sample opportunities data
    opportunities = [
        {
            "id": "test_1",
            "address": "123 Oak Street, Brooklyn, NY 11201",
            "price": 485000,
            "estimated_value": 557750,
            "equity_gain": 72750,
            "equity_percentage": 15.0,
            "property_type": "Single Family",
            "beds": 3,
            "baths": 2,
            "sqft": 1200,
            "janus_score": 85,
            "distress_level": "Low",
            "cap_rate": 8.5,
            "roi_estimate": 11.5,
            "strategy": "Buy-to-Hold",
            "risk_level": "Medium",
            "market_trend": "Rising",
            "last_updated": datetime.now().isoformat(),
            "analysis_timestamp": datetime.now().isoformat(),
            "agent_insights": [
                "Eden: Strong investment potential with 15.0% equity gain",
                "Orion: Market data shows rising trend in this area",
                "Osiris: Projected ROI of 11.5% based on current market conditions",
                "Valyria: Buy-to-Hold strategy recommended for this property type"
            ],
            "data_sources": [
                "ATTOM Property Database",
                "ESTATED Property Details",
                "County Records",
                "Market Analysis",
                "AI Agent Analysis"
            ]
        },
        {
            "id": "test_2",
            "address": "456 Maple Ave, Queens, NY 11355",
            "price": 325000,
            "estimated_value": 373750,
            "equity_gain": 48750,
            "equity_percentage": 15.0,
            "property_type": "Multi Family",
            "beds": 4,
            "baths": 3,
            "sqft": 1800,
            "janus_score": 90,
            "distress_level": "Low",
            "cap_rate": 9.0,
            "roi_estimate": 12.0,
            "strategy": "Rental Income",
            "risk_level": "Low",
            "market_trend": "Rising",
            "last_updated": datetime.now().isoformat(),
            "analysis_timestamp": datetime.now().isoformat(),
            "agent_insights": [
                "Eden: Excellent investment potential with 15.0% equity gain",
                "Orion: Market data shows strong rising trend in this area",
                "Osiris: Projected ROI of 12.0% based on current market conditions",
                "Valyria: Rental Income strategy recommended for this property type"
            ],
            "data_sources": [
                "ATTOM Property Database",
                "ESTATED Property Details",
                "County Records",
                "Market Analysis",
                "AI Agent Analysis"
            ]
        }
    ]
    
    print(f"Generated {len(opportunities)} sample opportunities:")
    
    for i, opp in enumerate(opportunities, 1):
        print(f"\n{i}. {opp['address']}")
        print(f"   Price: ${opp['price']:,.2f} | Est. Value: ${opp['estimated_value']:,.2f}")
        print(f"   Equity: ${opp['equity_gain']:,.2f} ({opp['equity_percentage']}%) | Score: {opp['janus_score']}/100")
        print(f"   Strategy: {opp['strategy']} | Risk: {opp['risk_level']} | Cap Rate: {opp['cap_rate']}%")

if __name__ == "__main__":
    print("Investment Opportunities API Test")
    print("=" * 50)
    
    try:
        # Try to test the actual API
        asyncio.run(test_investment_opportunities_api())
    except Exception as e:
        print(f"API test failed: {e}")
        print("\nFalling back to sample data...")
        asyncio.run(test_with_fallback())
    
    print("\n" + "=" * 50)
    print("Test completed!")
