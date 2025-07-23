#!/usr/bin/env python3
"""
Test script to run all test cases through the Customer Support Agent System
"""

import json
import sys
from main import CustomerSupportPipeline
from config.env_config import EnvConfig

def run_test_cases():
    """Run all test cases and display results"""
    print("Customer Support Agent System - Test Suite")
    print("="*80)
    
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
    
    # Load test cases
    with open("data/sample_tickets/test_cases.json", 'r') as f:
        test_cases = json.load(f)
    
    results = []
    
    # Process each test case
    for i, ticket in enumerate(test_cases):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i+1}/{len(test_cases)}: {ticket['ticket_id']}")
        print(f"Subject: {ticket['subject']}")
        print(f"Category: {ticket['category']}")
        print("-"*80)
        
        # Load customer profile if exists
        customer_profile = pipeline.load_customer_profile(
            ticket.get("customer_id"),
            "data/customer_profiles/profiles.json"
        )
        
        # Process the ticket
        try:
            result = pipeline.process_ticket(ticket, customer_profile)
            
            if result:
                print(f"\n✓ SUCCESS - Ticket processed")
                print(f"  Priority: {result.get('analysis', {}).get('priority', 'N/A')}")
                print(f"  Sentiment: {result.get('analysis', {}).get('sentiment', 'N/A')}")
                print(f"  Escalation: {result.get('response', {}).get('escalation_needed', False)}")
                print(f"  Response preview: {result.get('response', {}).get('response_text', '')[:100]}...")
                
                results.append({
                    "test_case": ticket['ticket_id'],
                    "subject": ticket['subject'],
                    "status": "SUCCESS",
                    "result": result
                })
            else:
                print(f"\n✗ FAILED - Ticket processing failed")
                results.append({
                    "test_case": ticket['ticket_id'],
                    "subject": ticket['subject'],
                    "status": "FAILED",
                    "result": None
                })
                
        except Exception as e:
            print(f"\n✗ ERROR - {str(e)}")
            results.append({
                "test_case": ticket['ticket_id'],
                "subject": ticket['subject'],
                "status": "ERROR",
                "error": str(e)
            })
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print("-"*80)
    
    successful = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"Total test cases: {len(test_cases)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    print(f"Success rate: {(successful/len(test_cases)*100):.1f}%")
    
    # Save detailed results
    with open("data/api_responses/test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: data/api_responses/test_results.json")
    
    # Show failed/error cases
    if failed + errors > 0:
        print(f"\n{'='*80}")
        print("FAILED/ERROR CASES:")
        print("-"*80)
        for r in results:
            if r['status'] != 'SUCCESS':
                print(f"- {r['test_case']}: {r['subject']} ({r['status']})")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        # Run single test case
        print("Running single test case mode...")
        from main import main
        main()
    else:
        # Run all test cases
        run_test_cases()