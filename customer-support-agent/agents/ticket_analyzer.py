import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import anthropic
from datetime import datetime


class TicketCategory(Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    FEATURE_REQUEST = "feature_request"
    COMPLAINT = "complaint"
    OTHER = "other"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Sentiment(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    ANGRY = "angry"


@dataclass
class TicketAnalysis:
    ticket_id: str
    category: TicketCategory
    priority: Priority
    sentiment: Sentiment
    key_issues: List[str]
    mentioned_products: List[str]
    error_codes: List[str]
    customer_intent: str
    requires_human_escalation: bool

    def to_dict(self) -> Dict:
        return {
            "ticket_id": self.ticket_id,
            "category": self.category.value,
            "priority": self.priority.value,
            "sentiment": self.sentiment.value,
            "key_issues": self.key_issues,
            "mentioned_products": self.mentioned_products,
            "error_codes": self.error_codes,
            "customer_intent": self.customer_intent,
            "requires_human_escalation": self.requires_human_escalation
        }


class TicketAnalyzerAgent:
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.temperature = 0.2
        
    def _create_system_prompt(self) -> str:
        return """You are a customer support ticket analyzer. Your job is to extract structured information from support tickets.

Analyze the ticket and provide a JSON response with the following fields:
- category: One of [technical, billing, feature_request, complaint, other]
- priority: One of [low, medium, high, critical] based on urgency and impact
- sentiment: One of [positive, neutral, negative, angry]
- key_issues: List of main problems or requests mentioned
- mentioned_products: List of any products or services mentioned
- error_codes: List of any error codes or IDs mentioned
- customer_intent: A brief summary of what the customer wants to achieve
- requires_human_escalation: Boolean indicating if this needs immediate human attention

Consider escalation for: legal threats, security breaches, data loss, extreme anger, or complex technical issues.

Respond ONLY with valid JSON."""

    def analyze_ticket(self, ticket_text: str, ticket_metadata: Optional[Dict] = None) -> TicketAnalysis:
        ticket_id = ticket_metadata.get("ticket_id", f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}") if ticket_metadata else f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        prompt = f"""Analyze this customer support ticket:

Ticket ID: {ticket_id}
{f"Timestamp: {ticket_metadata.get('timestamp')}" if ticket_metadata and 'timestamp' in ticket_metadata else ""}
{f"Customer ID: {ticket_metadata.get('customer_id')}" if ticket_metadata and 'customer_id' in ticket_metadata else ""}
{f"Product Version: {ticket_metadata.get('product_version')}" if ticket_metadata and 'product_version' in ticket_metadata else ""}

Ticket Content:
{ticket_text}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=self.temperature,
                system=self._create_system_prompt(),
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis_dict = json.loads(response.content[0].text)
            
            return TicketAnalysis(
                ticket_id=ticket_id,
                category=TicketCategory(analysis_dict["category"]),
                priority=Priority(analysis_dict["priority"]),
                sentiment=Sentiment(analysis_dict["sentiment"]),
                key_issues=analysis_dict["key_issues"],
                mentioned_products=analysis_dict["mentioned_products"],
                error_codes=analysis_dict["error_codes"],
                customer_intent=analysis_dict["customer_intent"],
                requires_human_escalation=analysis_dict["requires_human_escalation"]
            )
            
        except Exception as e:
            raise Exception(f"Failed to analyze ticket: {str(e)}")