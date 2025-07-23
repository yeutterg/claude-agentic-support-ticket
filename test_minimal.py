#!/usr/bin/env python3
"""
Minimal test to isolate coroutine issue
"""

import json
import asyncio
from main import CustomerSupportPipeline
from config.env_config import EnvConfig

# Load configuration
env_config = EnvConfig()
config = env_config.get_pipeline_config()

# Initialize pipeline
pipeline = CustomerSupportPipeline(config, use_promptlayer=bool(config["promptlayer_api_key"]))

# Test 1: Check if process_ticket is a coroutine
print(f"process_ticket is coroutine: {asyncio.iscoroutinefunction(pipeline.process_ticket)}")
print(f"process_ticket_sync is coroutine: {asyncio.iscoroutinefunction(pipeline.process_ticket_sync)}")

# Test 2: Simple call
ticket = {
    "ticket_id": "TEST-001",
    "subject": "Test",
    "body": "Test body",
    "category": "technical"
}

print("\nCalling process_ticket_sync...")
result = pipeline.process_ticket_sync(ticket, None)
print(f"Result type: {type(result)}")
print(f"Result: {result}")

# Test 3: Check if any methods return coroutines
if result and isinstance(result, dict):
    for key, value in result.items():
        print(f"{key}: type={type(value)}, is_coroutine={asyncio.iscoroutine(value)}")