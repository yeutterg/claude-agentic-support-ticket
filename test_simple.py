#!/usr/bin/env python3
"""
Simple test to debug the coroutine issue
"""

import json
from main import CustomerSupportPipeline
from config.env_config import EnvConfig

print("Starting simple test...")

# Load configuration
env_config = EnvConfig()
config = env_config.get_pipeline_config()

# Initialize pipeline - disable PromptLayer for tests
pipeline = CustomerSupportPipeline(config, use_promptlayer=False)
pipeline.load_knowledge_base("data/knowledge_base/articles.json")

# Single test ticket
ticket = {
    "ticket_id": "SIMPLE-001",
    "subject": "Test ticket",
    "body": "This is a simple test",
    "category": "technical",
    "timestamp": "2025-07-23T10:00:00.000000",
    "customer_id": "CUST-TEST",
    "product_version": "v4.2.1"
}

print("\nProcessing ticket...")
result = pipeline.process_ticket_sync(ticket, None)

print(f"\nResult type: {type(result)}")
print(f"Result is None: {result is None}")
print(f"Result is dict: {isinstance(result, dict)}")

if result:
    print("\nResult structure:")
    for key in result.keys() if isinstance(result, dict) else []:
        value = result[key]
        print(f"  {key}: {type(value).__name__}")

print("\nTest complete.")