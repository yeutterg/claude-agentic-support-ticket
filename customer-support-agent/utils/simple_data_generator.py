import json
import random
from datetime import datetime
import uuid


def generate_sample_tickets():
    tickets = [
        {
            "ticket_id": "TICKET-20250706-1001",
            "subject": "Can't log into my account",
            "body": "I've been trying to log in for the past hour but keep getting error code E401. I've tried resetting my password twice. This is really frustrating as I need to access my invoices for tax purposes. Please help ASAP!",
            "category": "technical",
            "timestamp": datetime.now().isoformat(),
            "customer_id": "CUST-12345",
            "product_version": "v2.3.1"
        },
        {
            "ticket_id": "TICKET-20250706-1002",
            "subject": "Unexpected charge on my account",
            "body": "I noticed a charge of $99.99 on my January statement for CloudSync Pro. I don't remember authorizing this. My account shows active subscription. Can you please explain this charge and provide details?",
            "category": "billing",
            "timestamp": datetime.now().isoformat(),
            "customer_id": "CUST-12346",
            "product_version": "v2.2.5"
        },
        {
            "ticket_id": "TICKET-20250706-1003",
            "subject": "DataVault Enterprise is running extremely slow",
            "body": "For the past 3 days, DataVault Enterprise has been loading very slowly. I've tried restarting but nothing works. Error code E500 keeps appearing. This is affecting my entire team's productivity. System specs: Windows 11, 16GB RAM",
            "category": "technical",
            "timestamp": datetime.now().isoformat(),
            "customer_id": "CUST-12347",
            "product_version": "v3.1.0"
        }
    ]
    return tickets


def generate_knowledge_base():
    articles = [
        {
            "article_id": "KB-001",
            "title": "Resolving E401 Authentication Errors",
            "content": "This error typically occurs when authentication tokens expire or become invalid.\n\nSolution Steps:\n1. Clear your browser cache and cookies\n2. Log out completely and log back in\n3. Check if your account is active and not suspended\n4. Verify your email address is confirmed\n5. Try resetting your password if the issue persists\n6. Disable browser extensions that might interfere\n7. Try a different browser or incognito mode\n\nIf the error continues, your account may need manual reset by our support team.",
            "category": "troubleshooting",
            "tags": ["authentication", "login", "E401", "error"]
        },
        {
            "article_id": "KB-002",
            "title": "Understanding Your Billing Statement",
            "content": "Your billing statement includes several components:\n\n1. Subscription Charges: Base monthly/annual fee for your plan\n2. Usage Charges: Additional costs based on usage beyond plan limits\n3. Add-ons: Optional features or increased limits\n4. Taxes: Applied based on your location\n5. Credits: Any discounts or refunds applied\n\nCommon billing issues:\n- Charges appear after cancellation: Usually prorated charges from the final billing period\n- Duplicate charges: May be authorization holds that will be released\n- Unexpected amounts: Check if you exceeded plan limits or had plan changes\n\nFor billing disputes, provide your invoice number and specific charge details.",
            "category": "billing",
            "tags": ["billing", "charges", "invoice", "payment"]
        },
        {
            "article_id": "KB-003",
            "title": "Performance Optimization Guide",
            "content": "If you're experiencing slow performance, follow these steps:\n\n1. System Requirements Check:\n   - Ensure your system meets minimum requirements\n   - Update to the latest version of the software\n   - Check available disk space (minimum 10GB recommended)\n\n2. Network Optimization:\n   - Test your internet speed (minimum 10 Mbps recommended)\n   - Use wired connection instead of WiFi when possible\n   - Check firewall settings for blocked ports\n\n3. Application Settings:\n   - Reduce cache size in settings\n   - Disable unnecessary features\n   - Lower quality settings for better performance\n\n4. Regular Maintenance:\n   - Clear cache weekly\n   - Restart application daily\n   - Update drivers and OS regularly",
            "category": "performance",
            "tags": ["performance", "slow", "optimization", "speed"]
        }
    ]
    return articles


def generate_customer_profiles():
    profiles = [
        {
            "customer_id": "CUST-12345",
            "name": "John Smith",
            "tier": "premium",
            "previous_tickets": 3,
            "satisfaction_score": 4.2,
            "technical_level": "intermediate"
        },
        {
            "customer_id": "CUST-12346",
            "name": "Sarah Johnson",
            "tier": "professional",
            "previous_tickets": 1,
            "satisfaction_score": 4.8,
            "technical_level": "basic"
        },
        {
            "customer_id": "CUST-12347",
            "name": "Mike Wilson",
            "tier": "enterprise",
            "previous_tickets": 8,
            "satisfaction_score": 3.9,
            "technical_level": "advanced"
        }
    ]
    return profiles


def generate_ground_truth():
    return [
        {
            "ticket_id": "TICKET-20250706-1001",
            "expected_category": "technical",
            "expected_priority": "high",
            "expected_sentiment": "negative",
            "requires_escalation": False
        },
        {
            "ticket_id": "TICKET-20250706-1002",
            "expected_category": "billing",
            "expected_priority": "medium",
            "expected_sentiment": "neutral",
            "requires_escalation": False
        }
    ]


def main():
    print("Generating sample data...")
    
    # Generate data
    tickets = generate_sample_tickets()
    articles = generate_knowledge_base()
    profiles = generate_customer_profiles()
    ground_truth = generate_ground_truth()
    
    # Save data
    with open("data/sample_tickets/tickets.json", "w") as f:
        json.dump(tickets, f, indent=2)
    print(f"Generated {len(tickets)} sample tickets")
    
    with open("data/knowledge_base/articles.json", "w") as f:
        json.dump(articles, f, indent=2)
    print(f"Generated {len(articles)} knowledge base articles")
    
    with open("data/customer_profiles/profiles.json", "w") as f:
        json.dump(profiles, f, indent=2)
    print(f"Generated {len(profiles)} customer profiles")
    
    with open("data/ground_truth.json", "w") as f:
        json.dump(ground_truth, f, indent=2)
    print(f"Generated ground truth for {len(ground_truth)} tickets")
    
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "ticket_count": len(tickets),
        "article_count": len(articles),
        "profile_count": len(profiles)
    }
    
    with open("data/dataset_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print("\nSample data generation complete!")
    print("Data saved in: customer-support-agent/data/")


if __name__ == "__main__":
    main()