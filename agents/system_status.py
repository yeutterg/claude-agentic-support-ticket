import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import anthropic
import aiohttp
import asyncio


class SystemStatus(Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    DOWN = "down"


@dataclass
class Incident:
    incident_id: str
    description: str
    impact: str
    estimated_resolution: Optional[datetime]
    
    def to_dict(self) -> Dict:
        return {
            "incident_id": self.incident_id,
            "description": self.description,
            "impact": self.impact,
            "estimated_resolution": self.estimated_resolution.isoformat() if self.estimated_resolution else None
        }


@dataclass
class SystemStatusResult:
    overall_status: SystemStatus
    affected_services: List[str]
    current_incidents: List[Incident]
    recent_deployments: List[str]
    known_issues: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "system_status": {
                "overall": self.overall_status.value,
                "affected_services": self.affected_services,
                "current_incidents": [incident.to_dict() for incident in self.current_incidents]
            },
            "recent_deployments": self.recent_deployments,
            "known_issues": self.known_issues
        }


class SystemStatusAgent:
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307", api_endpoints: Optional[Dict] = None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.temperature = 0.1
        self.api_endpoints = api_endpoints or {
            "status": "https://api.example.com/status",
            "incidents": "https://api.example.com/incidents",
            "deployments": "https://api.example.com/deployments"
        }
        
    def _create_system_prompt(self) -> str:
        return """You are a system status analyzer. Parse API responses and extract relevant system health information.

Analyze the provided system data and determine:
1. Overall system status (operational, degraded, or down)
2. Which services are affected
3. Current incidents and their impact
4. Recent deployments that might be related
5. Known issues

Be precise and factual. Respond only with valid JSON."""

    async def _fetch_api_data(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"API returned status {response.status}"}
            except Exception as e:
                return {"error": str(e)}
    
    def _mock_api_data(self, products: List[str], error_codes: List[str]) -> Dict:
        has_error = bool(error_codes)
        
        mock_data = {
            "status": {
                "overall": "degraded" if has_error else "operational",
                "services": {
                    "authentication": "degraded" if "E401" in error_codes else "operational",
                    "api": "operational",
                    "database": "operational",
                    "payment": "degraded" if "E402" in error_codes else "operational"
                }
            },
            "incidents": [],
            "deployments": [
                {
                    "id": "deploy-123",
                    "service": "authentication",
                    "timestamp": datetime.now().isoformat(),
                    "version": "2.3.1"
                }
            ]
        }
        
        if "E401" in error_codes:
            mock_data["incidents"].append({
                "id": "INC-789",
                "title": "Authentication Service Degradation",
                "description": "Intermittent login failures affecting 15% of users",
                "impact": "Some users may experience login delays or failures",
                "status": "investigating",
                "started_at": datetime.now().isoformat(),
                "estimated_resolution": datetime.now().isoformat()
            })
            
        return mock_data
    
    async def check_system_status(self, products: List[str], error_codes: List[str], 
                                 timestamp_range: Optional[Dict] = None) -> SystemStatusResult:
        
        if hasattr(self, '_use_mock_data') and self._use_mock_data:
            api_data = self._mock_api_data(products, error_codes)
        else:
            status_data = await self._fetch_api_data(self.api_endpoints["status"])
            incidents_data = await self._fetch_api_data(self.api_endpoints["incidents"])
            deployments_data = await self._fetch_api_data(self.api_endpoints["deployments"])
            
            api_data = {
                "status": status_data,
                "incidents": incidents_data,
                "deployments": deployments_data
            }
        
        prompt = f"""Analyze this system status data for the following context:
Products: {', '.join(products)}
Error Codes: {', '.join(error_codes)}
Timestamp Range: {timestamp_range if timestamp_range else 'Last 24 hours'}

API Data:
{json.dumps(api_data, indent=2)}

Determine the system status and extract relevant information."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=self.temperature,
                system=self._create_system_prompt(),
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_dict = json.loads(response.content[0].text)
            
            incidents = []
            for inc in result_dict.get('system_status', {}).get('current_incidents', []):
                est_resolution = None
                if inc.get('estimated_resolution'):
                    try:
                        est_resolution = datetime.fromisoformat(inc['estimated_resolution'])
                    except:
                        pass
                        
                incidents.append(Incident(
                    incident_id=inc['incident_id'],
                    description=inc['description'],
                    impact=inc['impact'],
                    estimated_resolution=est_resolution
                ))
            
            return SystemStatusResult(
                overall_status=SystemStatus(result_dict['system_status']['overall']),
                affected_services=result_dict['system_status']['affected_services'],
                current_incidents=incidents,
                recent_deployments=result_dict.get('recent_deployments', []),
                known_issues=result_dict.get('known_issues', [])
            )
            
        except Exception as e:
            raise Exception(f"Failed to check system status: {str(e)}")
    
    def check_status_sync(self, products: List[str], error_codes: List[str], 
                         timestamp_range: Optional[Dict] = None) -> SystemStatusResult:
        return asyncio.run(self.check_system_status(products, error_codes, timestamp_range))