#!/usr/bin/env python3
"""
Demo Script for Real Estate AI Agent System

This script demonstrates the system's capabilities with real-world
real estate scenarios and workflows.
"""

import asyncio
import json
from datetime import datetime

from agents.base_agent import AgentConfig
from agents.legal_agent import LegalAgent
from core.agent_manager import AgentManager


async def demo_property_purchase_workflow():
    """Demonstrate a complete property purchase workflow."""
    print("🏠 Property Purchase Workflow Demo")
    print("=" * 40)
    
    # Create agent manager
    manager = AgentManager()
    
    try:
        # Start the manager
        await manager.start()
        print("✅ System started")
        
        # Register legal agent
        legal_config = AgentConfig(
            name="Legal Analysis Agent",
            description="Specializes in legal analysis and compliance",
            model="gpt-4",
            temperature=0.1,
            max_tokens=4000,
            timeout=60
        )
        
        legal_agent = LegalAgent(legal_config)
        await manager.register_agent(legal_agent, "legal")
        print("✅ Legal Agent registered")
        
        # Define the property purchase workflow
        workflow_definition = [
            {
                "agent": "legal",
                "task": "contract_review",
                "data": {
                    "contract_type": "purchase_agreement",
                    "property_address": "123 Main Street, Anytown, USA",
                    "purchase_price": "$500,000",
                    "buyer": "John Doe",
                    "seller": "Jane Smith"
                }
            },
            {
                "agent": "legal",
                "task": "compliance_check",
                "data": {
                    "check_type": "fair_housing",
                    "property_type": "residential",
                    "transaction_type": "purchase"
                },
                "dependencies": [0]  # Depends on contract review
            },
            {
                "agent": "legal",
                "task": "risk_assessment",
                "data": {
                    "assessment_type": "legal_risks",
                    "property_value": "$500,000",
                    "transaction_complexity": "standard"
                },
                "dependencies": [0, 1]  # Depends on previous steps
            }
        ]
        
        # Create the workflow
        workflow = await manager.create_workflow(workflow_definition)
        print(f"✅ Workflow created: {workflow.workflow_id}")
        print(f"📋 Workflow steps: {len(workflow.steps)}")
        
        # Execute the workflow
        print("\n🔄 Executing workflow...")
        start_time = datetime.utcnow()
        
        results = await manager.execute_workflow(workflow.workflow_id)
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        print(f"✅ Workflow completed in {execution_time:.2f} seconds")
        
        # Display results
        print("\n📊 Workflow Results:")
        for step_id, result in results.items():
            step = next(s for s in workflow.steps if s.step_id == step_id)
            print(f"\n   Step {step_id}: {step.task}")
            print(f"   Analysis Type: {result['analysis_type']}")
            print(f"   Confidence: {result['confidence_score']}")
            
            if step.task == "contract_review":
                print(f"   Contract Type: {result['result']['contract_type']}")
                print(f"   Parties: {', '.join(result['result']['parties_identified'])}")
                print(f"   Key Clauses: {', '.join(result['result']['key_clauses'])}")
            
            elif step.task == "compliance_check":
                print(f"   Compliance Score: {result['result']['compliance_score']}")
                print(f"   Federal: {result['result']['federal_compliance']['status']}")
                print(f"   State: {result['result']['state_compliance']['status']}")
            
            elif step.task == "risk_assessment":
                print(f"   Risk Level: {result['result']['risk_level']}")
                print(f"   High Risk Areas: {len(result['result']['high_risk_areas'])}")
                print(f"   Medium Risk Areas: {len(result['result']['medium_risk_areas'])}")
        
    finally:
        await manager.stop()
        print("\n✅ System stopped")


async def demo_contract_generation():
    """Demonstrate contract generation capabilities."""
    print("\n📄 Contract Generation Demo")
    print("=" * 35)
    
    # Create legal agent directly
    config = AgentConfig(
        name="Contract Generation Agent",
        description="Specializes in contract creation and customization",
        model="gpt-4",
        temperature=0.1,
        max_tokens=6000,
        timeout=90
    )
    
    legal_agent = LegalAgent(config)
    
    # Generate a lease agreement
    print("🏠 Generating Lease Agreement...")
    
    lease_requirements = """
    Create a residential lease agreement for:
    - Property: 456 Oak Avenue, Suburbia, USA
    - Landlord: ABC Properties LLC
    - Tenant: Sarah Johnson
    - Term: 12 months
    - Monthly Rent: $2,500
    - Security Deposit: $2,500
    - Pet Policy: No pets allowed
    - Utilities: Tenant pays electricity, landlord pays water
    """
    
    response = await legal_agent.process_request(
        "Generate a lease agreement based on these requirements",
        {"requirements": lease_requirements}
    )
    
    if response.success:
        print("✅ Lease agreement generated successfully")
        print(f"📊 Analysis Type: {response.data['analysis_type']}")
        print(f"🎯 Confidence Score: {response.data['confidence_score']}")
        
        # Safely access result fields
        result = response.data.get('result', {})
        if 'template_used' in result:
            print(f"📋 Template Used: {result['template_used']}")
        if 'key_sections' in result:
            print(f"🔑 Key Sections: {', '.join(result['key_sections'])}")
        
        # Show a preview of the generated contract
        if 'contract_text' in result:
            contract_preview = result['contract_text'][:200] + "..."
            print(f"\n📄 Contract Preview:")
            print(f"   {contract_preview}")
    else:
        print(f"❌ Contract generation failed: {response.error}")


async def demo_compliance_analysis():
    """Demonstrate compliance analysis capabilities."""
    print("\n⚖️ Compliance Analysis Demo")
    print("=" * 35)
    
    # Create legal agent
    config = AgentConfig(
        name="Compliance Analysis Agent",
        description="Specializes in regulatory compliance and risk assessment",
        model="gpt-4",
        temperature=0.1,
        max_tokens=5000,
        timeout=75
    )
    
    legal_agent = LegalAgent(config)
    
    # Analyze a complex transaction
    print("🏘️ Analyzing Multi-Unit Property Transaction...")
    
    transaction_details = """
    Transaction: Purchase of 4-unit apartment building
    Location: 789 Business District, Metro City, USA
    Purchase Price: $1,200,000
    Buyer: Real Estate Investment Group LLC
    Seller: Individual Owner
    Property Type: Multi-family residential
    Zoning: R-4 (Multi-family residential)
    Current Use: Rental apartments
    Planned Use: Renovate and continue as rentals
    """
    
    response = await legal_agent.process_request(
        "Analyze this transaction for compliance with all applicable regulations",
        {"transaction": transaction_details}
    )
    
    if response.success:
        print("✅ Compliance analysis completed successfully")
        print(f"📊 Analysis Type: {response.data['analysis_type']}")
        print(f"🎯 Confidence Score: {response.data['confidence_score']}")
        
        result = response.data['result']
        print(f"\n📋 Compliance Results:")
        print(f"   Federal Compliance: {result['federal_compliance']['status']}")
        print(f"   State Compliance: {result['state_compliance']['status']}")
        print(f"   Local Compliance: {result['local_compliance']['status']}")
        print(f"   Overall Score: {result['compliance_score']}")
        
        if result['violations']:
            print(f"   ⚠️  Violations Found: {len(result['violations'])}")
            for violation in result['violations']:
                print(f"      - {violation}")
        else:
            print("   ✅ No compliance violations found")
        
        if result['required_actions']:
            print(f"\n🔧 Required Actions:")
            for action in result['required_actions']:
                print(f"   - {action}")
    else:
        print(f"❌ Compliance analysis failed: {response.error}")


async def demo_regulatory_guidance():
    """Demonstrate regulatory guidance capabilities."""
    print("\n📚 Regulatory Guidance Demo")
    print("=" * 35)
    
    # Create legal agent
    config = AgentConfig(
        name="Regulatory Guidance Agent",
        description="Specializes in regulatory updates and guidance",
        model="gpt-4",
        temperature=0.1,
        max_tokens=4000,
        timeout=60
    )
    
    legal_agent = LegalAgent(config)
    
    # Get guidance on new regulations
    print("🔍 Getting Guidance on New Fair Housing Regulations...")
    
    guidance_request = """
    What are the latest updates to Fair Housing Act regulations
    that affect real estate agents and property managers?
    Include compliance steps and best practices.
    """
    
    response = await legal_agent.process_request(
        guidance_request,
        {"context": "fair_housing_updates"}
    )
    
    if response.success:
        print("✅ Regulatory guidance provided successfully")
        print(f"📊 Analysis Type: {response.data['analysis_type']}")
        print(f"🎯 Confidence Score: {response.data['confidence_score']}")
        
        result = response.data.get('result', {})
        print(f"\n📚 Regulatory Guidance:")
        
        if 'relevant_regulations' in result:
            print(f"   Relevant Regulations: {', '.join(result['relevant_regulations'])}")
        
        if 'current_requirements' in result and isinstance(result['current_requirements'], dict):
            print(f"   Current Requirements: {result['current_requirements'].get('status', 'N/A')}")
        
        if 'recent_changes' in result and result['recent_changes']:
            print(f"   Recent Changes: {', '.join(result['recent_changes'])}")
        else:
            print("   Recent Changes: None identified")
        
        if 'compliance_steps' in result:
            print(f"\n📋 Compliance Steps:")
            for i, step in enumerate(result['compliance_steps'], 1):
                print(f"   {i}. {step}")
        
        if 'resources' in result:
            print(f"\n🔗 Resources:")
            for resource in result['resources'][:3]:  # Show first 3
                print(f"   - {resource}")
        
    else:
        print(f"❌ Regulatory guidance failed: {response.error}")


async def main():
    """Main demo function."""
    print("🏠 Real Estate AI Agent System - Live Demo")
    print("=" * 55)
    print("This demo showcases the system's capabilities with real-world scenarios.")
    print()
    
    try:
        # Run all demos
        await demo_property_purchase_workflow()
        await demo_contract_generation()
        await demo_compliance_analysis()
        await demo_regulatory_guidance()
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Key Benefits Demonstrated:")
        print("   ✅ Multi-step workflow orchestration")
        print("   ✅ Specialized agent capabilities")
        print("   ✅ Automated compliance checking")
        print("   ✅ Contract generation and review")
        print("   ✅ Risk assessment and mitigation")
        print("   ✅ Regulatory guidance and updates")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
