import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import anthropic


class ResponseTone(Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    APOLOGETIC = "apologetic"
    TECHNICAL = "technical"


@dataclass
class CustomerProfile:
    customer_id: str
    name: str
    tier: str
    previous_tickets: int
    satisfaction_score: Optional[float]
    technical_level: str  # basic, intermediate, advanced


@dataclass
class SynthesizedResponse:
    response_text: str
    confidence_score: float
    suggested_actions: List[str]
    follow_up_required: bool
    escalation_needed: bool
    response_tone: ResponseTone
    
    def to_dict(self) -> Dict:
        return {
            "response_text": self.response_text,
            "confidence_score": self.confidence_score,
            "suggested_actions": self.suggested_actions,
            "follow_up_required": self.follow_up_required,
            "escalation_needed": self.escalation_needed,
            "response_tone": self.response_tone.value
        }


class ResponseSynthesisAgent:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.temperature = 0.7
        
    def _create_system_prompt(self) -> str:
        return """You are a customer support response specialist. Your job is to synthesize information from multiple sources into a helpful, empathetic customer response.

Guidelines:
1. Be empathetic and acknowledge the customer's frustration when appropriate
2. Provide clear, actionable solutions
3. Use the appropriate tone based on the situation
4. Include specific next steps
5. Escalate when necessary (security issues, data loss, legal threats, extreme dissatisfaction)

Response Requirements:
- Address all customer concerns
- Use simple language for basic technical users, more detail for advanced users
- Include timeline estimates when available
- Apologize for inconveniences when appropriate
- End with clear next steps or call to action

You must provide a JSON response with:
- response_text: The complete customer response
- confidence_score: 0.0-1.0 based on how well we can address the issue
- suggested_actions: List of internal actions for support team
- follow_up_required: Boolean
- escalation_needed: Boolean
- response_tone: one of [professional, friendly, apologetic, technical]"""

    def _determine_tone(self, ticket_analysis: Dict, system_status: Dict) -> ResponseTone:
        if ticket_analysis['sentiment'] in ['negative', 'angry']:
            return ResponseTone.APOLOGETIC
        elif ticket_analysis['category'] == 'technical' and any(system_status.get('current_incidents', [])):
            return ResponseTone.APOLOGETIC
        elif ticket_analysis['category'] == 'technical':
            return ResponseTone.TECHNICAL
        else:
            return ResponseTone.FRIENDLY
    
    def synthesize_response(self, 
                          original_ticket: str,
                          ticket_analysis: Dict,
                          knowledge_results: Dict,
                          system_status: Dict,
                          customer_profile: Optional[CustomerProfile] = None) -> SynthesizedResponse:
        
        customer_context = ""
        if customer_profile:
            customer_context = f"""
Customer Profile:
- Name: {customer_profile.name}
- Tier: {customer_profile.tier}
- Previous Tickets: {customer_profile.previous_tickets}
- Technical Level: {customer_profile.technical_level}
- Satisfaction Score: {customer_profile.satisfaction_score or 'N/A'}"""

        incidents_context = ""
        if system_status.get('system_status', {}).get('current_incidents'):
            incidents_context = "\nCurrent System Issues:\n"
            for incident in system_status['system_status']['current_incidents']:
                incidents_context += f"- {incident['description']} (Impact: {incident['impact']})\n"

        solutions_context = ""
        if knowledge_results.get('recommended_solutions'):
            solutions_context = "\nRecommended Solutions:\n"
            for solution in knowledge_results['recommended_solutions']:
                solutions_context += f"- {solution}\n"

        prompt = f"""Create a customer support response for this ticket:

Original Ticket:
{original_ticket}

Ticket Analysis:
- Category: {ticket_analysis['category']}
- Priority: {ticket_analysis['priority']}
- Sentiment: {ticket_analysis['sentiment']}
- Customer Intent: {ticket_analysis['customer_intent']}
- Key Issues: {', '.join(ticket_analysis['key_issues'])}
- Error Codes: {', '.join(ticket_analysis['error_codes']) if ticket_analysis['error_codes'] else 'None'}
{customer_context}
{incidents_context}
{solutions_context}

System Status: {system_status.get('system_status', {}).get('overall', 'unknown')}
Affected Services: {', '.join(system_status.get('system_status', {}).get('affected_services', [])) or 'None'}

Create a response that:
1. Acknowledges the customer's issue
2. Provides clear solutions or workarounds
3. Sets appropriate expectations
4. Uses {'apologetic' if ticket_analysis['sentiment'] in ['negative', 'angry'] else 'friendly'} tone
5. Includes specific next steps"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=self.temperature,
                system=self._create_system_prompt(),
                messages=[{"role": "user", "content": prompt}]
            )

            # Robust response handling for Claude 4
            if hasattr(response, "stop_reason") and response.stop_reason == "refusal":
                print(f"Claude refused to answer for model '{self.model}'.")
                return None
            if not hasattr(response, "content") or not response.content or not hasattr(response.content[0], "text"):
                print(f"Empty or malformed response from Anthropic for model '{self.model}': {response}")
                return None
            try:
                result_dict = json.loads(response.content[0].text)
            except Exception as e:
                # Try to strip code block markers and parse again
                raw = response.content[0].text if response.content and hasattr(response.content[0], 'text') else response
                if isinstance(raw, str) and raw.strip().startswith('```'):
                    print("Anthropic response wrapped in code block, attempting to strip and parse again...")
                    import re
                    cleaned = re.sub(r'^```[a-zA-Z]*\\n?', '', raw.strip())
                    cleaned = re.sub(r'```$', '', cleaned).strip()
                    try:
                        result_dict = json.loads(cleaned)
                    except Exception as e2:
                        print(f"Could not parse JSON from Anthropic response for model '{self.model}' even after stripping code block. Raw response: {raw}")
                        return None
                else:
                    print(f"Could not parse JSON from Anthropic response for model '{self.model}'. Raw response: {raw}")
                    return None
            
            tone = ResponseTone(result_dict['response_tone'])
            
            escalation_needed = (
                ticket_analysis.get('requires_human_escalation', False) or
                result_dict.get('escalation_needed', False) or
                ticket_analysis['priority'] == 'critical'
            )
            
            return SynthesizedResponse(
                response_text=result_dict['response_text'],
                confidence_score=float(result_dict['confidence_score']),
                suggested_actions=result_dict['suggested_actions'],
                follow_up_required=result_dict['follow_up_required'],
                escalation_needed=escalation_needed,
                response_tone=tone
            )
            
        except anthropic.NotFoundError as e:
            if "model" in str(e) and "not_found_error" in str(e):
                print(f"The specified Anthropic model '{self.model}' was not found or is unavailable. Please check your model name or account access.")
                return None
            else:
                raise
        except anthropic.BadRequestError as e:
            if "credit balance is too low" in str(e):
                print("Your Anthropic API credit balance is too low. Please add credits or enable mock mode in your .env file.")
                return None
            else:
                raise
        except Exception as e:
            print(f"Failed to synthesize response: {str(e)}")
            return None