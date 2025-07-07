# Docker Quick Reference

## Setup
```bash
# Copy environment file
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# Build and start
docker-compose up --build customer-support-agent
```

## Common Commands

### Running the Application
```bash
# Start in foreground
docker-compose up customer-support-agent

# Start in background
docker-compose up -d customer-support-agent

# Stop the application
docker-compose down
```

### Development
```bash
# Run development version
docker-compose --profile dev up customer-support-agent-dev

# Run examples
docker-compose run --rm customer-support-agent python example_usage.py

# Interactive shell
docker-compose exec customer-support-agent /bin/bash
```

### Debugging
```bash
# View logs
docker-compose logs customer-support-agent
docker-compose logs -f customer-support-agent  # Follow logs

# Check health
docker-compose exec customer-support-agent python health_check.py

# Check environment
docker-compose exec customer-support-agent printenv

# Inspect container
docker-compose exec customer-support-agent ls -la
```

### Data Management
```bash
# View generated data
docker-compose exec customer-support-agent ls -la data/

# Regenerate sample data
docker-compose exec customer-support-agent python utils/simple_data_generator.py

# Backup data
docker cp $(docker-compose ps -q customer-support-agent):/app/data ./data-backup
```

### Cleanup
```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove containers, volumes, and images
docker-compose down -v --rmi all

# Clean up unused Docker resources
docker system prune -a
```

## Environment Variables

Set these in your `.env` file:

```env
# Required
ANTHROPIC_API_KEY=your-key-here

# Optional
PROMPTLAYER_API_KEY=your-promptlayer-key
ENVIRONMENT=development
USE_MOCK_DATA=true
LOG_LEVEL=INFO
```

## Port Mapping

- `8000`: Main application port
- `8001`: Development service port

## Volume Mounts

- `./data:/app/data` - Data persistence
- `./.env:/app/.env:ro` - Environment configuration (read-only)