# Janus Prop AI - Real Estate AI Agent System

A comprehensive AI-powered real estate analysis system that provides explainable insights, data integration, and continuous learning capabilities.

## Features

### 1. Data Integration First
- **Realie API Integration**: Immediate integration for speed and freshness (baseline property coverage)
- **ATTOM Data Preparation**: Historical data and deeper analytics (coming soon)
- **Modular Architecture**: Easy swapping/adding of new data sources
- **Scalable Design**: Built for millions of records and thousands of users

### 2. AI Insights Must Be Explainable
- **Clear Explanations**: Every prediction comes with a short, clear "why" in plain English
- **Consistent Pipeline**: Built-in system to generate and display explanations
- **No Black Box**: Users never see scores without context
- **Confidence Levels**: Transparent confidence scoring for all insights

### 3. Actionable UX, Not Just Analysis
- **Action Buttons**: Every AI insight paired with actionable next steps
- **Simple Interface**: Collapsible, fast UI that avoids overwhelming users
- **Smart Workflows**: "Add to Leads," "Contact Owner," "Run Financing" actions
- **User-Centric Design**: Focus on what users can do, not just what they can see

### 4. Scalable, Modular Backend
- **Microservice Design**: Each agent/service built and scaled independently
- **Agent2Agent Protocol**: Inter-agent communication for complex workflows
- **Horizontal Scaling**: Easy scaling for millions of records and thousands of users
- **Async Architecture**: Built on asyncio for high performance

### 5. Feedback & Learning Loop
- **Continuous Learning**: Results fed back into retraining/adjustments
- **Internal Dashboard**: Monitor AI accuracy and user behavior
- **Performance Metrics**: Track improvement over time
- **User Feedback**: Collect and analyze user satisfaction

## System Architecture

### Core Agents

1. **AI Insights Agent** (`agents/ai_insights_agent.py`)
   - Generates explainable property insights
   - Provides actionable recommendations
   - Calculates confidence scores
   - Supports multiple insight types

2. **Data Integration Agent** (`agents/data_integration_agent.py`)
   - Manages multiple data sources
   - Handles Realie API integration
   - Prepares for ATTOM data enrichment
   - Provides unified data interface

3. **Feedback & Learning Agent** (`agents/feedback_learning_agent.py`)
   - Collects user feedback
   - Tracks prediction accuracy
   - Generates learning metrics
   - Enables continuous improvement

4. **Legal Agent** (`agents/legal_agent.py`)
   - Legal analysis and compliance checking
   - Contract review capabilities
   - Regulatory compliance monitoring

### Communication System

- **Agent Manager** (`core/agent_manager.py`): Central orchestration
- **Communication Manager** (`core/communication.py`): Inter-agent messaging
- **Workflow Engine**: Complex multi-step processes

## Quick Start

### Prerequisites

- Python 3.8+
- pip or poetry
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd janus-prop-ai/Backend/AI_bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

### Running the System

#### Option 1: FastAPI Server (Recommended for Development)

```bash
python api_server.py
```

The API server will start on `http://localhost:8000`

- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **System Status**: `http://localhost:8000/api/system/status`

#### Option 2: Direct Agent System

```bash
python main.py
```

This runs the full agent system with console output.

### Frontend Integration

The frontend is built with React + TypeScript and includes:

- **AI Insights Panel**: Display explainable insights with actionable steps
- **Data Integration Dashboard**: Monitor data sources and sync status
- **Learning Metrics Dashboard**: Track AI performance and improvement
- **Tabbed Interface**: Organized view of all system components

To run the frontend:

```bash
cd ../Frontend
npm install
npm start
```

## API Endpoints

### AI Insights
- `POST /api/ai-insights/analyze` - Analyze property and generate insights
- `GET /api/ai-insights/capabilities` - Get agent capabilities

### Data Integration
- `POST /api/data-integration/search` - Search properties
- `POST /api/data-integration/sync` - Sync data source
- `POST /api/data-integration/add-source` - Add new data source
- `GET /api/data-integration/status` - Get integration status

### Feedback & Learning
- `POST /api/feedback/collect` - Collect user feedback
- `POST /api/feedback/track-accuracy` - Track prediction accuracy
- `GET /api/feedback/learning-metrics` - Get learning metrics
- `GET /api/feedback/agent-performance` - Get agent performance

### System
- `GET /health` - Health check
- `GET /api/system/status` - Overall system status

## Configuration

### Environment Variables

Create a `.env` file with:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Realie API Configuration
REALIE_API_KEY=your_realie_api_key
REALIE_BASE_URL=https://api.realie.com/v1

# ATTOM Data Configuration (Future)
ATTOM_API_KEY=your_attom_api_key
ATTOM_BASE_URL=https://api.attomdata.com/v3.0

# System Configuration
LOG_LEVEL=INFO
MAX_CONCURRENT_AGENTS=10
SYSTEM_TIMEOUT=300
```

### Agent Configuration

Modify `config/agents.yaml` to customize agent behavior:

```yaml
ai_insights_agent:
  model: gpt-4
  temperature: 0.1
  max_tokens: 4000
  timeout: 60

data_integration_agent:
  realie_api:
    rate_limit: 60
    timeout: 30
  attom_data:
    rate_limit: 30
    timeout: 45
```

## Development

### Project Structure

```
Backend/AI_bot/
├── agents/                 # AI agent implementations
│   ├── base_agent.py      # Base agent class
│   ├── ai_insights_agent.py
│   ├── data_integration_agent.py
│   ├── feedback_learning_agent.py
│   └── legal_agent.py
├── core/                  # Core system components
│   ├── agent_manager.py   # Agent orchestration
│   ├── communication.py   # Inter-agent messaging
│   └── exceptions.py      # Custom exceptions
├── config/                # Configuration files
│   └── agents.yaml       # Agent configurations
├── api_server.py          # FastAPI server
├── main.py               # Direct agent system
└── requirements.txt      # Python dependencies
```

### Adding New Agents

1. **Create agent class** inheriting from `BaseAgent`
2. **Implement required methods**:
   - `get_capabilities()`
   - `process_request()`
   - `health_check()`
   - `shutdown()`
3. **Register in main.py** and `api_server.py`
4. **Add configuration** in `config/agents.yaml`

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=agents --cov=core

# Run specific test file
pytest tests/test_ai_insights_agent.py
```

## Deployment

### Production Considerations

- **Environment Variables**: Use proper secret management
- **Database**: Configure persistent storage for feedback and metrics
- **Monitoring**: Add logging and metrics collection
- **Scaling**: Use load balancers and multiple instances
- **Security**: Implement proper authentication and authorization

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "api_server.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add your license information here]

## Support

For questions and support:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Roadmap

### Phase 1 (Current)
- ✅ Core agent system
- ✅ AI insights generation
- ✅ Data integration framework
- ✅ Feedback collection system

### Phase 2 (Next)
- 🔄 ATTOM data integration
- 🔄 Advanced market analysis
- 🔄 Predictive modeling
- 🔄 User authentication

### Phase 3 (Future)
- 📋 Advanced AI models
- 📋 Real-time data streaming
- 📋 Mobile applications
- 📋 Enterprise features
