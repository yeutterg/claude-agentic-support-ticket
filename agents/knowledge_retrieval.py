import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import anthropic
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


@dataclass
class Article:
    article_id: str
    title: str
    content: str
    category: str
    tags: List[str]


@dataclass
class RetrievalResult:
    article_id: str
    title: str
    relevance_score: float
    summary: str
    solution_steps: List[str]

    def to_dict(self) -> Dict:
        return {
            "article_id": self.article_id,
            "title": self.title,
            "relevance_score": self.relevance_score,
            "summary": self.summary,
            "solution_steps": self.solution_steps
        }


@dataclass
class KnowledgeRetrievalResult:
    relevant_articles: List[RetrievalResult]
    recommended_solutions: List[str]
    related_issues: List[str]

    def to_dict(self) -> Dict:
        return {
            "relevant_articles": [article.to_dict() for article in self.relevant_articles],
            "recommended_solutions": self.recommended_solutions,
            "related_issues": self.related_issues
        }


class KnowledgeRetrievalAgent:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.temperature = 0.3
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.articles = []
        
    def _create_system_prompt(self) -> str:
        return """You are a knowledge retrieval specialist for customer support. 
        
Given search results from our knowledge base, analyze and extract:
1. The most relevant solution steps from the articles
2. Recommended solutions based on the issue
3. Related issues that might be connected

Focus on practical, actionable solutions. Respond with valid JSON only."""

    def load_knowledge_base(self, articles: List[Article]):
        self.articles = articles
        
        if not articles:
            return
            
        article_texts = [f"{article.title} {article.content}" for article in articles]
        embeddings = self.encoder.encode(article_texts)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
    def _search_similar_articles(self, query: str, k: int = 5) -> List[tuple]:
        if not self.index or not self.articles:
            return []
            
        query_embedding = self.encoder.encode([query])
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.articles):
                relevance_score = 1 / (1 + dist)
                results.append((self.articles[idx], relevance_score))
                
        return results
    
    def retrieve_knowledge(self, ticket_analysis: Dict, search_params: Optional[Dict] = None) -> KnowledgeRetrievalResult:
        search_query = f"{' '.join(ticket_analysis['key_issues'])} {ticket_analysis['customer_intent']}"
        
        if ticket_analysis['error_codes']:
            search_query += f" {' '.join(ticket_analysis['error_codes'])}"
            
        k = search_params.get('top_k', 5) if search_params else 5
        similar_articles = self._search_similar_articles(search_query, k)
        
        if not similar_articles:
            return KnowledgeRetrievalResult(
                relevant_articles=[],
                recommended_solutions=["No relevant articles found. Consider escalating to human support."],
                related_issues=[]
            )
        
        articles_context = "\n\n".join([
            f"Article {i+1} (Relevance: {score:.2f}):\nTitle: {article.title}\nContent: {article.content[:500]}..."
            for i, (article, score) in enumerate(similar_articles[:3])
        ])
        
        prompt = f"""Based on these knowledge base articles, provide solutions for the customer issue:

Customer Issue Summary:
- Category: {ticket_analysis['category']}
- Key Issues: {', '.join(ticket_analysis['key_issues'])}
- Error Codes: {', '.join(ticket_analysis['error_codes']) if ticket_analysis['error_codes'] else 'None'}
- Customer Intent: {ticket_analysis['customer_intent']}

Relevant Articles:
{articles_context}

Provide a JSON response with:
1. relevant_articles: Array of the most relevant articles with summaries and solution steps
2. recommended_solutions: Array of recommended solutions based on all articles
3. related_issues: Array of related issues that might be connected"""

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
            
            retrieval_results = []
            for i, (article, score) in enumerate(similar_articles[:3]):
                if i < len(result_dict.get('relevant_articles', [])):
                    article_result = result_dict['relevant_articles'][i]
                    retrieval_results.append(RetrievalResult(
                        article_id=article.article_id,
                        title=article.title,
                        relevance_score=float(score),
                        summary=article_result.get('summary', ''),
                        solution_steps=article_result.get('solution_steps', [])
                    ))
            
            return KnowledgeRetrievalResult(
                relevant_articles=retrieval_results,
                recommended_solutions=result_dict.get('recommended_solutions', []),
                related_issues=result_dict.get('related_issues', [])
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
            print(f"Failed to retrieve knowledge: {str(e)}")
            return None