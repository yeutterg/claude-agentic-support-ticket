#!/usr/bin/env python3
"""
Debug script to isolate the coroutine issue
"""

import json
import asyncio
from main import CustomerSupportPipeline
from config.env_config import EnvConfig

def test_single_ticket():
    """Test a single ticket to debug the issue"""
    print("Debug Test - Single Ticket")
    print("="*60)
    
    # Load configuration
    env_config = EnvConfig()
    config = env_config.get_pipeline_config()
    
    # Initialize pipeline
    pipeline = CustomerSupportPipeline(config, use_promptlayer=bool(config["promptlayer_api_key"]))
    pipeline.load_knowledge_base("data/knowledge_base/articles.json")
    
    # Simple test ticket
    ticket = {
        "ticket_id": "DEBUG-001",
        "subject": "Test ticket",
        "body": "This is a test",
        "category": "technical",
        "timestamp": "2025-07-23T10:00:00.000000",
        "customer_id": "CUST-TEST",
        "product_version": "v4.2.1"
    }
    
    print("\nStep 1: Calling process_ticket_sync...")
    result = pipeline.process_ticket_sync(ticket, None)
    
    print(f"\nStep 2: Result type: {type(result)}")
    print(f"Step 3: Result is dict: {isinstance(result, dict)}")
    print(f"Step 4: Result is None: {result is None}")
    
    if result:
        print("\nStep 5: Result exists, checking contents...")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            print("\nStep 6: Accessing result properties...")
            try:
                analysis = result.get('analysis', {})
                print(f"Analysis type: {type(analysis)}")
                print(f"Analysis: {analysis}")
            except Exception as e:
                print(f"ERROR accessing analysis: {e}")
                
            try:
                response = result.get('response', {})
                print(f"Response type: {type(response)}")
                print(f"Response: {response}")
            except Exception as e:
                print(f"ERROR accessing response: {e}")
    else:
        print("\nResult is None or False")

if __name__ == "__main__":
    test_single_ticket()