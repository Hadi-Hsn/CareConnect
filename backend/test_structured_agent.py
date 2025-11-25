"""Test script for structured agent service."""
import asyncio
from app.core.db import async_session_maker
from app.services.structured_agent import StructuredAgentService


async def test_structured_agent():
    """Test the three-layer structured agent."""
    
    test_messages = [
        "Book me an appointment with cardiology tomorrow at 10am",
        "I want to see Dr. Smith next week",
        "What are the visiting hours?",
        "Cancel my appointment",
        "Show me my appointments",
    ]
    
    async with async_session_maker() as session:
        agent = StructuredAgentService(session)
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n{'='*80}")
            print(f"Test {i}: {message}")
            print('='*80)
            
            try:
                # Layer 1: Parse Intent
                print("\n[LAYER 1] Parsing Intent...")
                intent = await agent.parse_intent(message, user_id=1)
                print(f"  Action: {intent.action}")
                print(f"  Confidence: {intent.confidence}")
                print(f"  Summary: {intent.user_message_summary}")
                print(f"  Requires Clarification: {intent.requires_clarification}")
                if intent.requires_clarification:
                    print(f"  Questions: {intent.clarification_questions}")
                print(f"  Entities: {intent.extracted_entities}")
                
                # Layer 2: Extract Parameters (skip if clarification needed or general conversation)
                if not intent.requires_clarification and intent.action not in ["general_conversation", "query_information", "emergency"]:
                    print("\n[LAYER 2] Extracting Parameters...")
                    params = await agent.extract_parameters(intent, message, user_id=1)
                    print(f"  Action: {params.action}")
                    print(f"  Date: {params.date}")
                    print(f"  Time: {params.time_hour}:{params.time_minute if params.time_minute else 0}")
                    print(f"  Provider: {params.provider_name or params.provider_id}")
                    print(f"  Department: {params.department}")
                    print(f"  Has All Info: {params.has_all_required_info}")
                    print(f"  Missing: {params.missing_fields}")
                    print(f"  Ambiguities: {params.ambiguities}")
                    print(f"  Notes: {params.validation_notes}")
                    
                    # Layer 3: Create Execution Plan (only if we have all info)
                    if params.has_all_required_info:
                        print("\n[LAYER 3] Creating Execution Plan...")
                        plan = await agent.create_execution_plan(params, message, user_id=1)
                        print(f"  Description: {plan.action_description}")
                        print(f"  Tools: {plan.tools_to_call}")
                        print(f"  Can Execute: {plan.can_execute}")
                        print(f"  Requires Confirmation: {plan.requires_user_confirmation}")
                        if plan.warning_messages:
                            print(f"  Warnings: {plan.warning_messages}")
                        if plan.blocking_issues:
                            print(f"  Blocking Issues: {plan.blocking_issues}")
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_structured_agent())
