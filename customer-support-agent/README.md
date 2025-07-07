# Customer Support Ticket Resolution System

A multi-agent system designed to automatically process, analyze, and resolve customer support tickets using specialized AI agents powered by Claude.

## Overview

This system uses 4 specialized agents working together:
- **Ticket Analyzer Agent**: Extracts key information and classifies tickets
- **Knowledge Retrieval Agent**: Searches documentation and knowledge bases
- **System Status Agent**: Queries APIs for real-time system/product status
- **Response Synthesis Agent**: Generates personalized, contextual responses

## Features

- Automated ticket classification and prioritization
- Semantic search through knowledge base articles
- Real-time system status integration
- Personalized response generation based on customer history
- Comprehensive evaluation framework with PromptLayer integration
- A/B testing capabilities for continuous improvement
- Cost tracking and optimization

## Installation

### Quick Setup (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd customer-support-agent
```

2. Run the setup script:
```bash
python setup.py
```

3. Edit `.env` file and add your API key:
```bash
# Edit .env with your API keys
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

### Manual Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd customer-support-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment configuration:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
# Required:
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional:
PROMPTLAYER_API_KEY=your-promptlayer-api-key-here
```

4. Generate sample data:
```bash
python utils/simple_data_generator.py
```

## Quick Start

After installation, you can immediately run the system:

```bash
# Run the main demo
python main.py

# Or try the examples
python example_usage.py
```

The system will use the pre-generated sample data to demonstrate all features.

## Docker Installation (Alternative)

If you prefer to run the system in Docker:

### Prerequisites
- Docker and Docker Compose installed on your system

### Quick Docker Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd customer-support-agent
```

2. Create your `.env` file:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. Build and run with Docker Compose:
```bash
# Run the main application
docker-compose up customer-support-agent

# Or run in detached mode
docker-compose up -d customer-support-agent
```

### Docker Development Setup

For development with live code reloading:

```bash
# Run the development service
docker-compose --profile dev up customer-support-agent-dev

# Or run examples
docker-compose --profile dev run --rm customer-support-agent-dev python example_usage.py
```

### Manual Docker Commands

If you prefer not to use Docker Compose:

```bash
# Build the image
docker build -t customer-support-agent .

# Run the container
docker run -it --rm \
  -e ANTHROPIC_API_KEY=your-api-key-here \
  -v $(pwd)/data:/app/data \
  customer-support-agent

# Run examples
docker run -it --rm \
  -e ANTHROPIC_API_KEY=your-api-key-here \
  -v $(pwd)/data:/app/data \
  customer-support-agent python example_usage.py
```

### Docker Benefits

- **Consistent Environment**: Same runtime across all systems
- **Easy Deployment**: No local Python setup required
- **Isolation**: Doesn't affect your system Python installation
- **Scalability**: Easy to deploy to cloud platforms

### Docker Troubleshooting

#### Health Check
The Docker container includes a built-in health check. You can manually run it:

```bash
# Check health status
docker-compose exec customer-support-agent python health_check.py

# View container health
docker ps  # Look for "healthy" status
```

#### Common Issues

**Issue: Container fails to start**
```bash
# Check logs
docker-compose logs customer-support-agent

# Check if .env file is properly mounted
docker-compose exec customer-support-agent cat .env
```

**Issue: API key not working**
```bash
# Verify environment variables
docker-compose exec customer-support-agent printenv | grep ANTHROPIC

# Test with mock data (no API key required)
docker-compose run --rm -e USE_MOCK_DATA=true customer-support-agent
```

**Issue: Permission errors**
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER ./data
```

#### Development with Docker

```bash
# Interactive shell in container
docker-compose exec customer-support-agent /bin/bash

# Run specific scripts
docker-compose exec customer-support-agent python example_usage.py

# View real-time logs
docker-compose logs -f customer-support-agent
```

## Project Structure

```
customer-support-agent/
├── agents/                  # Core agent implementations
│   ├── ticket_analyzer.py   # Ticket analysis and classification
│   ├── knowledge_retrieval.py # Knowledge base search
│   ├── system_status.py     # System status checking
│   └── response_synthesis.py # Response generation
├── evaluation/              # Evaluation and metrics
│   ├── promptlayer_integration.py
│   └── metrics.py
├── data/                    # Sample data and storage
│   ├── knowledge_base/
│   ├── sample_tickets/
│   └── customer_profiles/
├── config/                  # Configuration files
│   ├── agent_configs.py
│   └── evaluation_configs.py
├── utils/                   # Utility functions
│   └── data_generator.py
└── main.py                  # Main orchestration script
```

## Usage Example

```python
from main import CustomerSupportPipeline
from agents.response_synthesis import CustomerProfile
from config.env_config import EnvConfig

# Initialize pipeline with environment configuration
env_config = EnvConfig()
config = env_config.get_pipeline_config()
pipeline = CustomerSupportPipeline(config)

# Load knowledge base
pipeline.load_knowledge_base("data/knowledge_base/articles.json")

# Process a ticket
ticket = {
    "ticket_id": "TICKET-12345",
    "subject": "Can't log into my account",
    "body": "I keep getting error E401 when trying to log in...",
    "customer_id": "CUST-67890"
}

# Optional: Load customer profile
customer_profile = CustomerProfile(
    customer_id="CUST-67890",
    name="John Doe",
    tier="premium",
    previous_tickets=5,
    satisfaction_score=4.2,
    technical_level="intermediate"
)

# Process the ticket
result = pipeline.process_ticket_sync(ticket, customer_profile)
print(result["response"]["response_text"])
```

## Agent Details

### Ticket Analyzer Agent
- Extracts: category, priority, sentiment, key issues, error codes
- Uses Claude Opus for high accuracy
- Includes escalation detection for critical issues

### Knowledge Retrieval Agent
- Implements semantic search using sentence transformers
- Returns relevant articles with solution steps
- Uses FAISS for efficient vector search

### System Status Agent
- Checks real-time system health
- Identifies ongoing incidents
- Links issues to recent deployments

### Response Synthesis Agent
- Generates contextual, empathetic responses
- Adapts tone based on customer sentiment
- Includes clear action steps

## Evaluation Framework

The system includes comprehensive evaluation metrics:

- **Classification Accuracy**: Measures correct categorization
- **Response Quality**: Tracks customer satisfaction metrics
- **Performance Metrics**: Monitors latency and throughput
- **Cost Analysis**: Calculates per-ticket processing costs

### Running Evaluations

```python
from evaluation.metrics import PerformanceMetrics, ABTestFramework

# Calculate classification metrics
predictions = ["technical", "billing", "technical"]
ground_truth = ["technical", "billing", "complaint"]
metrics = PerformanceMetrics.calculate_classification_metrics(predictions, ground_truth)

# Run A/B tests
ab_test = ABTestFramework()
ab_test.add_result("A", {"response_quality": 0.85})
ab_test.add_result("B", {"response_quality": 0.92})
significance = ab_test.calculate_significance("response_quality")
```

## Configuration

### Environment Configuration (.env)
The system uses a `.env` file for configuration. See `.env.example` for all available options:

```env
# Required
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional
PROMPTLAYER_API_KEY=your-promptlayer-api-key-here
ENVIRONMENT=development
USE_MOCK_DATA=true
LOG_LEVEL=INFO
```

### Agent Configuration
Key configuration options in `config/agent_configs.py`:

- Model selection per agent
- Temperature settings
- Retry policies
- Escalation thresholds
- Quality requirements

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Performance Considerations

- Average processing time: ~5-10 seconds per ticket
- Supports concurrent processing for batch operations
- Knowledge base supports up to 10,000 articles efficiently
- Caching reduces repeat query costs

## Cost Optimization

- Uses different models based on complexity
- Caches frequent queries
- Batch processes when possible
- Monitors token usage per agent

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.