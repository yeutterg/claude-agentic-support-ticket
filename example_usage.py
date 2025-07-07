import os
import json
from datetime import datetime
from main import CustomerSupportPipeline
from agents.response_synthesis import CustomerProfile
from utils.data_generator import DataGenerator
from evaluation.metrics import PerformanceMetrics, ABTestFramework


def basic_example():
    print("\n=== BASIC EXAMPLE ===")
    print("Processing a single support ticket\n")
    
    try:
        from config.env_config import EnvConfig
        env_config = EnvConfig()
        config = env_config.get_pipeline_config()
    except Exception as e:
        print(f"Error loading config: {e}")
        return
    
    pipeline = CustomerSupportPipeline(config, use_promptlayer=False)
    
    ticket = {
        "ticket_id": "DEMO-001",
        "subject": "Unable to export data",
        "body": "I'm trying to export my analytics data but the export button is grayed out. I'm on the Professional plan and should have this feature. Error code E1001 appears when I hover over the button.",
        "customer_id": "CUST-DEMO",
        "timestamp": datetime.now().isoformat()
    }
    
    result = pipeline.process_ticket_sync(ticket)
    
    print("Analysis Results:")
    print(f"- Category: {result['analysis']['category']}")
    print(f"- Priority: {result['analysis']['priority']}")
    print(f"- Sentiment: {result['analysis']['sentiment']}")
    
    print("\nGenerated Response:")
    print("-" * 60)
    print(result['response']['response_text'])
    print("-" * 60)


def batch_processing_example():
    print("\n=== BATCH PROCESSING EXAMPLE ===")
    print("Processing multiple tickets with evaluation\n")
    
    generator = DataGenerator(seed=42)
    tickets = [generator.generate_support_ticket() for _ in range(5)]
    
    try:
        from config.env_config import EnvConfig
        env_config = EnvConfig()
        config = env_config.get_pipeline_config()
    except Exception as e:
        print(f"Error loading config: {e}")
        return
    
    pipeline = CustomerSupportPipeline(config, use_promptlayer=False)
    
    results = []
    categories = []
    priorities = []
    processing_times = []
    
    for i, ticket in enumerate(tickets):
        print(f"Processing ticket {i+1}/5: {ticket['subject'][:50]}...")
        result = pipeline.process_ticket_sync(ticket)
        results.append(result)
        
        categories.append(result['analysis']['category'])
        priorities.append(result['analysis']['priority'])
        processing_times.append(result['processing_time_seconds'])
    
    print("\n=== BATCH SUMMARY ===")
    print(f"Total tickets processed: {len(tickets)}")
    print(f"Average processing time: {sum(processing_times)/len(processing_times):.2f} seconds")
    print(f"Categories: {dict((c, categories.count(c)) for c in set(categories))}")
    print(f"Priorities: {dict((p, priorities.count(p)) for p in set(priorities))}")


def ab_testing_example():
    print("\n=== A/B TESTING EXAMPLE ===")
    print("Comparing two different response generation approaches\n")
    
    ab_test = ABTestFramework()
    
    test_metrics_a = [
        {"response_quality": 0.82, "processing_time": 4.5, "cost": 0.45},
        {"response_quality": 0.78, "processing_time": 4.2, "cost": 0.43},
        {"response_quality": 0.85, "processing_time": 4.8, "cost": 0.47},
        {"response_quality": 0.80, "processing_time": 4.3, "cost": 0.44},
        {"response_quality": 0.83, "processing_time": 4.6, "cost": 0.46}
    ]
    
    test_metrics_b = [
        {"response_quality": 0.88, "processing_time": 5.2, "cost": 0.52},
        {"response_quality": 0.91, "processing_time": 5.5, "cost": 0.55},
        {"response_quality": 0.87, "processing_time": 5.1, "cost": 0.51},
        {"response_quality": 0.89, "processing_time": 5.3, "cost": 0.53},
        {"response_quality": 0.90, "processing_time": 5.4, "cost": 0.54}
    ]
    
    for metrics in test_metrics_a:
        ab_test.add_result("A", metrics)
    
    for metrics in test_metrics_b:
        ab_test.add_result("B", metrics)
    
    summary = ab_test.get_summary()
    
    print("A/B Test Results:")
    for metric, results in summary.items():
        print(f"\n{metric}:")
        print(f"  Variant A mean: {results['mean_a']:.3f}")
        print(f"  Variant B mean: {results['mean_b']:.3f}")
        print(f"  Improvement: {results['improvement_percent']:.1f}%")
        print(f"  Statistically significant: {results['significant']}")


def knowledge_base_example():
    print("\n=== KNOWLEDGE BASE EXAMPLE ===")
    print("Setting up and querying the knowledge base\n")
    
    from agents.knowledge_retrieval import KnowledgeRetrievalAgent, Article
    
    try:
        from config.env_config import EnvConfig
        env_config = EnvConfig()
        api_key = env_config.anthropic_api_key
    except Exception as e:
        print(f"Error loading config: {e}")
        return
    
    kb_agent = KnowledgeRetrievalAgent(api_key)
    
    articles = [
        Article(
            article_id="KB-001",
            title="How to Reset Your Password",
            content="To reset your password: 1. Click 'Forgot Password' on login page 2. Enter your email 3. Check your email for reset link 4. Create new password with 8+ characters",
            category="account",
            tags=["password", "login", "account", "reset"]
        ),
        Article(
            article_id="KB-002",
            title="Troubleshooting Export Issues",
            content="If export is disabled: 1. Verify your plan includes export features 2. Check if you have sufficient permissions 3. Ensure data size is within limits 4. Try different export format",
            category="features",
            tags=["export", "data", "troubleshooting", "permissions"]
        ),
        Article(
            article_id="KB-003",
            title="Understanding Error Code E1001",
            content="Error E1001 indicates insufficient permissions. This occurs when: User lacks export rights, Plan doesn't include feature, or Account is in read-only mode. Contact admin to update permissions.",
            category="errors",
            tags=["E1001", "error", "permissions", "export"]
        )
    ]
    
    kb_agent.load_knowledge_base(articles)
    
    test_query = {
        "key_issues": ["export disabled", "E1001 error"],
        "customer_intent": "export analytics data",
        "error_codes": ["E1001"],
        "category": "technical"
    }
    
    results = kb_agent.retrieve_knowledge(test_query)
    
    print("Knowledge Base Query Results:")
    for article in results.relevant_articles:
        print(f"\n- {article.title}")
        print(f"  Relevance: {article.relevance_score:.2f}")
        print(f"  Summary: {article.summary}")
    
    print(f"\nRecommended Solutions:")
    for solution in results.recommended_solutions:
        print(f"- {solution}")


def main():
    print("Customer Support Agent System - Examples")
    print("=" * 60)
    
    try:
        from config.env_config import EnvConfig
        env_config = EnvConfig()
        print(f"Configuration loaded successfully. Environment: {env_config.environment}")
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Please ensure you have:")
        print("1. Created a .env file (copy from .env.example)")
        print("2. Set your ANTHROPIC_API_KEY in the .env file")
        return
    
    basic_example()
    
    
    
    
    print("\n" + "=" * 60)
    print("Examples completed!")


if __name__ == "__main__":
    main()