import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid
from faker import Faker
from agents.knowledge_retrieval import Article
from agents.response_synthesis import CustomerProfile


class DataGenerator:
    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
        self.fake = Faker()
        if seed:
            Faker.seed(seed)
        
        self.products = ["CloudSync Pro", "DataVault Enterprise", "SecureAPI Gateway", "Analytics Dashboard"]
        self.error_codes = ["E401", "E402", "E500", "E503", "E1001", "E2002", "E3003"]
        self.categories = ["technical", "billing", "feature_request", "complaint", "other"]
        
    def generate_support_ticket(self) -> Dict[str, str]:
        templates = [
            {
                "category": "technical",
                "subject": "Can't log into my account",
                "body": "I've been trying to log in for the past {time} but keep getting error code {error}. I've tried resetting my password {attempts} times. This is really frustrating as I need to {purpose}. Please help ASAP!",
                "params": {
                    "time": ["hour", "30 minutes", "2 hours"],
                    "error": self.error_codes,
                    "attempts": ["twice", "three times", "multiple times"],
                    "purpose": ["access my invoices for tax purposes", "update my payment method", "download important files", "check my usage statistics"]
                }
            },
            {
                "category": "billing",
                "subject": "Unexpected charge on my account",
                "body": "I noticed a charge of ${amount} on my {date} statement for {product}. I don't remember authorizing this. My account shows {status}. Can you please explain this charge and {action}?",
                "params": {
                    "amount": ["99.99", "149.99", "299.99", "49.99"],
                    "date": ["January", "last month's", "February", "recent"],
                    "product": self.products,
                    "status": ["active subscription", "cancelled subscription", "free trial", "inactive"],
                    "action": ["issue a refund", "provide details", "reverse the charge", "explain the billing"]
                }
            },
            {
                "category": "technical",
                "subject": "{product} is running extremely slow",
                "body": "For the past {duration}, {product} has been {issue}. I've tried {attempted_fixes} but nothing works. Error code {error} keeps appearing. This is affecting my {impact}. System specs: {specs}",
                "params": {
                    "product": self.products,
                    "duration": ["3 days", "week", "few hours", "2 weeks"],
                    "issue": ["loading very slowly", "timing out constantly", "crashing frequently", "not responding"],
                    "attempted_fixes": ["restarting", "clearing cache", "reinstalling", "updating"],
                    "error": self.error_codes,
                    "impact": ["entire team's productivity", "client deliverables", "daily operations", "business processes"],
                    "specs": ["Windows 11, 16GB RAM", "macOS Ventura", "Ubuntu 22.04", "Windows 10 Pro"]
                }
            },
            {
                "category": "feature_request",
                "subject": "Feature Request: {feature}",
                "body": "I've been using {product} for {duration} and it's great! However, I really need {feature_detail}. This would help me {benefit}. Many of my colleagues also need this. Is this on your roadmap?",
                "params": {
                    "feature": ["Batch export functionality", "API integration", "Dark mode", "Mobile app", "Real-time collaboration"],
                    "product": self.products,
                    "duration": ["6 months", "over a year", "3 months", "2 years"],
                    "feature_detail": ["the ability to export multiple files at once", "better API documentation", "a dark theme option", "mobile access", "real-time editing with my team"],
                    "benefit": ["save hours of work daily", "integrate with our systems", "reduce eye strain", "work remotely", "improve team efficiency"]
                }
            },
            {
                "category": "complaint",
                "subject": "Terrible customer service experience",
                "body": "I contacted support {when} about {issue} and {experience}. Ticket #{ticket_num} was {status}. This is unacceptable for a {tier} customer. I'm considering {action} if this isn't resolved immediately.",
                "params": {
                    "when": ["yesterday", "last week", "3 days ago", "on Monday"],
                    "issue": ["a critical bug", "billing problem", "account access", "data loss"],
                    "experience": ["never got a response", "was told to wait 48 hours", "got a generic response", "was transferred 5 times"],
                    "ticket_num": [str(random.randint(10000, 99999)) for _ in range(4)],
                    "status": ["closed without resolution", "still pending", "marked as resolved but isn't", "ignored"],
                    "tier": ["premium", "enterprise", "professional", "business"],
                    "action": ["switching to a competitor", "cancelling my subscription", "escalating to management", "posting negative reviews"]
                }
            }
        ]
        
        template = random.choice(templates)
        body = template["body"]
        
        for param, values in template["params"].items():
            body = body.replace(f"{{{param}}}", random.choice(values))
        
        ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        return {
            "ticket_id": ticket_id,
            "subject": template["subject"].format(**{k: random.choice(v) for k, v in template.get("params", {}).items()}),
            "body": body,
            "category": template["category"],
            "timestamp": datetime.now().isoformat(),
            "customer_id": f"CUST-{random.randint(10000, 99999)}",
            "product_version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 99)}"
        }
    
    def generate_knowledge_base_articles(self, count: int = 50) -> List[Article]:
        articles = []
        
        article_templates = [
            {
                "title": "Resolving E401 Authentication Errors",
                "content": """This error typically occurs when authentication tokens expire or become invalid.

Solution Steps:
1. Clear your browser cache and cookies
2. Log out completely and log back in
3. Check if your account is active and not suspended
4. Verify your email address is confirmed
5. Try resetting your password if the issue persists
6. Disable browser extensions that might interfere
7. Try a different browser or incognito mode

If the error continues, your account may need manual reset by our support team.""",
                "category": "troubleshooting",
                "tags": ["authentication", "login", "E401", "error"]
            },
            {
                "title": "Understanding Your Billing Statement",
                "content": """Your billing statement includes several components:

1. Subscription Charges: Base monthly/annual fee for your plan
2. Usage Charges: Additional costs based on usage beyond plan limits
3. Add-ons: Optional features or increased limits
4. Taxes: Applied based on your location
5. Credits: Any discounts or refunds applied

Common billing issues:
- Charges appear after cancellation: Usually prorated charges from the final billing period
- Duplicate charges: May be authorization holds that will be released
- Unexpected amounts: Check if you exceeded plan limits or had plan changes

For billing disputes, provide your invoice number and specific charge details.""",
                "category": "billing",
                "tags": ["billing", "charges", "invoice", "payment"]
            },
            {
                "title": "Performance Optimization Guide",
                "content": """If you're experiencing slow performance, follow these steps:

1. System Requirements Check:
   - Ensure your system meets minimum requirements
   - Update to the latest version of the software
   - Check available disk space (minimum 10GB recommended)

2. Network Optimization:
   - Test your internet speed (minimum 10 Mbps recommended)
   - Use wired connection instead of WiFi when possible
   - Check firewall settings for blocked ports

3. Application Settings:
   - Reduce cache size in settings
   - Disable unnecessary features
   - Lower quality settings for better performance

4. Regular Maintenance:
   - Clear cache weekly
   - Restart application daily
   - Update drivers and OS regularly""",
                "category": "performance",
                "tags": ["performance", "slow", "optimization", "speed"]
            }
        ]
        
        for i in range(count):
            if i < len(article_templates):
                template = article_templates[i]
                articles.append(Article(
                    article_id=f"KB-{str(uuid.uuid4())[:8]}",
                    title=template["title"],
                    content=template["content"],
                    category=template["category"],
                    tags=template["tags"]
                ))
            else:
                articles.append(Article(
                    article_id=f"KB-{str(uuid.uuid4())[:8]}",
                    title=self.fake.sentence(nb_words=6)[:-1],
                    content=self.fake.text(max_nb_chars=500),
                    category=random.choice(["troubleshooting", "billing", "features", "getting-started"]),
                    tags=random.sample(["error", "setup", "configuration", "api", "integration", "security"], 3)
                ))
        
        return articles
    
    def generate_customer_profiles(self, count: int = 20) -> List[CustomerProfile]:
        profiles = []
        
        for _ in range(count):
            satisfaction = random.uniform(2.0, 5.0) if random.random() > 0.2 else None
            
            profiles.append(CustomerProfile(
                customer_id=f"CUST-{random.randint(10000, 99999)}",
                name=self.fake.name(),
                tier=random.choice(["free", "basic", "professional", "enterprise"]),
                previous_tickets=random.randint(0, 50),
                satisfaction_score=round(satisfaction, 1) if satisfaction else None,
                technical_level=random.choice(["basic", "intermediate", "advanced"])
            ))
        
        return profiles
    
    def generate_test_dataset(self) -> Dict[str, any]:
        tickets = [self.generate_support_ticket() for _ in range(100)]
        articles = self.generate_knowledge_base_articles(50)
        profiles = self.generate_customer_profiles(20)
        
        ground_truth = []
        for ticket in tickets[:20]:  
            ground_truth.append({
                "ticket_id": ticket["ticket_id"],
                "expected_category": ticket["category"],
                "expected_priority": random.choice(["low", "medium", "high", "critical"]),
                "expected_sentiment": random.choice(["positive", "neutral", "negative", "angry"]),
                "requires_escalation": random.choice([True, False])
            })
        
        return {
            "tickets": tickets,
            "knowledge_base": [article.__dict__ for article in articles],
            "customer_profiles": [profile.__dict__ for profile in profiles],
            "ground_truth": ground_truth,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "ticket_count": len(tickets),
                "article_count": len(articles),
                "profile_count": len(profiles)
            }
        }