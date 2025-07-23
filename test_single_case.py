#!/usr/bin/env python3
"""
Test a single case from the test suite
"""

import json
import sys
from main import CustomerSupportPipeline
from config.env_config import EnvConfig

def test_single_case(case_number):
    """Test a specific case number"""
    # Load test cases
    with open("data/sample_tickets/test_cases.json", 'r') as f:
        test_cases = json.load(f)
    
    if case_number < 1 or case_number > len(test_cases):
        print(f"Invalid case number. Please choose between 1 and {len(test_cases)}")
        return
    
    ticket = test_cases[case_number - 1]
    
    print("Customer Support Agent System - Single Test Case")
    print("="*60)
    print(f"Testing Case #{case_number}: {ticket['ticket_id']}")
    print(f"Subject: {ticket['subject']}")
    print("-"*60)
    
    # Load configuration
    try:
        env_config = EnvConfig()
        config = env_config.get_pipeline_config()
    except Exception as e:
        print(f"ERROR loading configuration: {e}")
        return
    
    # Initialize pipeline
    pipeline = CustomerSupportPipeline(config, use_promptlayer=bool(config["promptlayer_api_key"]))
    pipeline.load_knowledge_base("data/knowledge_base/articles.json")
    
    # Load customer profile
    customer_profile = pipeline.load_customer_profile(
        ticket.get("customer_id"),
        "data/customer_profiles/profiles.json"
    )
    
    # Process the ticket
    result = pipeline.process_ticket(ticket, customer_profile)
    
    if result:
        print("\n" + "="*60)
        print("RESPONSE TO CUSTOMER:")
        print("="*60)
        print(result.get('response', {}).get('response_text', 'No response generated'))
        
        # Save result
        filename = f"data/api_responses/test_case_{case_number}_result.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nFull result saved to: {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_single_case.py <case_number>")
        print("\nAvailable test cases:")
        with open("data/sample_tickets/test_cases.json", 'r') as f:
            cases = json.load(f)
        for i, case in enumerate(cases, 1):
            print(f"  {i}: {case['subject']}")
    else:
        try:
            case_num = int(sys.argv[1])
            test_single_case(case_num)
        except ValueError:
            print("Please provide a valid case number")