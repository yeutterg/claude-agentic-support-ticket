import asyncio
import json
import os
from typing import Dict, Optional
from datetime import datetime

from agents.ticket_analyzer import TicketAnalyzerAgent
from agents.knowledge_retrieval import KnowledgeRetrievalAgent, Article
from agents.system_status import SystemStatusAgent
from agents.response_synthesis import ResponseSynthesisAgent, CustomerProfile
from evaluation.promptlayer_integration import PromptLayerEvaluator, EvaluationOrchestrator
from evaluation.metrics import CostCalculator
from utils.data_generator import DataGenerator


class CustomerSupportPipeline:
    def __init__(self, config: Dict[str, str], use_promptlayer: bool = True):
        self.config = config
        api_key = config.get("anthropic_api_key")
        
        if use_promptlayer and config.get("promptlayer_api_key"):
            self.evaluator = PromptLayerEvaluator(
                api_key=config["promptlayer_api_key"],
                anthropic_api_key=api_key
            )
            # Keep using the original API key for agents
            # PromptLayer tracking will be handled differently
        else:
            self.evaluator = None
        
        # Always use the original API key for agents
        self.ticket_analyzer = TicketAnalyzerAgent(api_key)
        self.knowledge_retrieval = KnowledgeRetrievalAgent(api_key)
        self.system_status = SystemStatusAgent(api_key)
        self.response_synthesis = ResponseSynthesisAgent(api_key)
        
        self.system_status._use_mock_data = config.get("use_mock_data", True)
        
        self.cost_calculator = CostCalculator()
        self.evaluation_orchestrator = EvaluationOrchestrator(self.evaluator) if self.evaluator else None
        
    def load_knowledge_base(self, articles_path: str):
        with open(articles_path, 'r') as f:
            articles_data = json.load(f)
            
        articles = [
            Article(
                article_id=a["article_id"],
                title=a["title"],
                content=a["content"],
                category=a["category"],
                tags=a["tags"]
            )
            for a in articles_data
        ]
        
        self.knowledge_retrieval.load_knowledge_base(articles)
        print(f"Loaded {len(articles)} knowledge base articles")
        
    def load_customer_profile(self, customer_id: str, profiles_path: str) -> Optional[CustomerProfile]:
        with open(profiles_path, 'r') as f:
            profiles_data = json.load(f)
            
        for profile in profiles_data:
            if profile["customer_id"] == customer_id:
                return CustomerProfile(
                    customer_id=profile["customer_id"],
                    name=profile["name"],
                    tier=profile["tier"],
                    previous_tickets=profile["previous_tickets"],
                    satisfaction_score=profile.get("satisfaction_score"),
                    technical_level=profile["technical_level"]
                )
        
        return None
    
    async def process_ticket(self, ticket: Dict[str, str], customer_profile: Optional[CustomerProfile] = None) -> Dict:
        start_time = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"Processing Ticket: {ticket.get('ticket_id', 'Unknown')}")
        print(f"Subject: {ticket.get('subject', 'No subject')}")
        print(f"{'='*60}\n")
        
        ticket_text = f"Subject: {ticket.get('subject', '')}\n\n{ticket.get('body', '')}"
        ticket_metadata = {
            "ticket_id": ticket.get("ticket_id"),
            "timestamp": ticket.get("timestamp"),
            "customer_id": ticket.get("customer_id"),
            "product_version": ticket.get("product_version")
        }
        
        print("Step 1: Analyzing ticket...")
        analysis = self.ticket_analyzer.analyze_ticket(ticket_text, ticket_metadata)
        if analysis is None:
            print("Ticket analysis failed. Skipping ticket processing.")
            return None
        analysis_dict = analysis.to_dict()
        print(f"  Category: {analysis_dict['category']}")
        print(f"  Priority: {analysis_dict['priority']}")
        print(f"  Sentiment: {analysis_dict['sentiment']}")
        
        print("\nStep 2: Retrieving relevant knowledge...")
        knowledge_results = self.knowledge_retrieval.retrieve_knowledge(analysis_dict)
        if knowledge_results is None:
            print("Knowledge retrieval failed. Skipping ticket processing.")
            return None
        knowledge_dict = knowledge_results.to_dict()
        print(f"  Found {len(knowledge_dict['relevant_articles'])} relevant articles")
        
        print("\nStep 3: Checking system status...")
        status_results = await self.system_status.check_system_status(
            analysis_dict.get("mentioned_products", []),
            analysis_dict.get("error_codes", [])
        )
        if status_results is None:
            print("System status check failed. Skipping ticket processing.")
            return None
        status_dict = status_results.to_dict()
        print(f"  System Status: {status_dict['system_status']['overall']}")
        
        print("\nStep 4: Synthesizing response...")
        response = self.response_synthesis.synthesize_response(
            ticket_text,
            analysis_dict,
            knowledge_dict,
            status_dict,
            customer_profile
        )
        if response is None:
            print("Response synthesis failed. Skipping ticket processing.")
            return None
        response_dict = response.to_dict()
        print(f"  Confidence Score: {response_dict['confidence_score']:.2f}")
        print(f"  Escalation Needed: {response_dict['escalation_needed']}")
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        if self.evaluation_orchestrator:
            evaluation_results = self.evaluation_orchestrator.evaluate_full_pipeline(
                ticket_text,
                analysis_dict,
                knowledge_dict,
                status_dict,
                response_dict
            )
        else:
            evaluation_results = None
        
        return {
            "ticket_id": ticket.get("ticket_id"),
            "analysis": analysis_dict,
            "knowledge_results": knowledge_dict,
            "system_status": status_dict,
            "response": response_dict,
            "processing_time_seconds": processing_time,
            "evaluation": evaluation_results,
            "timestamp": datetime.now().isoformat()
        }
    
    def process_ticket_sync(self, ticket: Dict[str, str], customer_profile: Optional[CustomerProfile] = None) -> Dict:
        """Synchronous wrapper for process_ticket"""
        return asyncio.run(self.process_ticket(ticket, customer_profile))


def main():
    print("Customer Support Agent System - Demo Run")
    print("="*60)
    
    try:
        from config.env_config import EnvConfig
        env_config = EnvConfig()
        config = env_config.get_pipeline_config()
    except ValueError as e:
        print(f"ERROR: {e}")
        print("Please ensure you have created a .env file with the required variables.")
        print("See .env.example for the required format.")
        return
    except Exception as e:
        print(f"ERROR loading configuration: {e}")
        return
    
    pipeline = CustomerSupportPipeline(config, use_promptlayer=bool(config["promptlayer_api_key"]))
    
    pipeline.load_knowledge_base("data/knowledge_base/articles.json")
    
    with open("data/sample_tickets/tickets.json", 'r') as f:
        tickets = json.load(f)
    
    sample_ticket = tickets[0]
    
    customer_profile = pipeline.load_customer_profile(
        sample_ticket.get("customer_id"),
        "data/customer_profiles/profiles.json"
    )
    
    result = pipeline.process_ticket_sync(sample_ticket, customer_profile)
    
    print("\n" + "="*60)
    print("FINAL RESPONSE TO CUSTOMER:")
    print("="*60)
    print(result["response"]["response_text"])
    print("\n" + "="*60)
    
    if result.get("evaluation"):
        print("\nEVALUATION RESULTS:")
        print(f"Overall Score: {result['evaluation']['overall_score']:.2f}")
        print("\nAgent Metrics:")
        for agent, metrics in result['evaluation']['agent_metrics'].items():
            print(f"\n{agent}:")
            for metric, value in metrics.items():
                print(f"  {metric}: {value:.2f}")
    
    with open("data/api_responses/sample_result.json", 'w') as f:
        json.dump(result, f, indent=2)
        
    print(f"\nFull results saved to: data/api_responses/sample_result.json")


if __name__ == "__main__":
    main()