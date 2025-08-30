# Janus Prop AI Backend

A comprehensive real estate AI agent system built with FastAPI, featuring real-time APIs, WebSocket support, and integration with multiple AI services.

## Features

- **AI Agent Management**: Coordinated system of specialized AI agents
- **Real-time Communication**: WebSocket and Redis-based real-time updates
- **Property Management**: Comprehensive property data handling
- **Lead Management**: Lead tracking and qualification
- **Market Intelligence**: Market trends and analysis
- **AI Insights**: AI-generated property insights and recommendations
- **Multiple AI Integrations**: Gemini AI, ATTOM Data, and more

## Architecture

```
Backend/
├── agents/                 # AI Agent implementations
│   ├── agent_manager.py   # Central agent coordinator
│   ├── gemini_ai_agent.py # Google Gemini AI integration
│   └── attom_data_agent.py # ATTOM Real Estate Data
├── api/                   # REST API endpoints
│   └── v1/               # API version 1
│       ├── endpoints/    # Individual endpoint modules
│       └── api.py        # Main API router
├── config/               # Configuration management
│   └── settings.py       # Environment-based settings
├── core/                 # Core system components
│   ├── database.py       # Database connection & models
│   ├── redis_client.py   # Redis caching & pub/sub
│   ├── websocket_manager.py # WebSocket handling
│   └── realtime_manager.py # Real-time data sync
├── models/               # Database models
│   ├── property.py       # Property model
│   └── ...              # Other models
├── main.py               # Application entry point
├── start.py              # Startup script
└── requirements.txt      # Python dependencies
```

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- API Keys for:
  - Google Gemini AI
  - ATTOM Data Solutions

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd janus-prop-ai/Backend
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
   Create a `.env` file in the Backend directory:
   ```env
   # Database
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/janus_prop_ai
   
   # Redis
   REDIS_URL=redis://localhost:6379
   
   # API Keys
   GEMINI_API_KEY=your_gemini_api_key
   ATTOM_API_KEY=your_attom_api_key
   
   # Server
   HOST=0.0.0.0
   PORT=8000
   DEBUG=true
   
   # CORS
   CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb janus_prop_ai
   
   # Run database migrations (when implemented)
   # alembic upgrade head
   ```

6. **Start Redis**
   ```bash
   redis-server
   ```

## Usage

### Starting the Backend

**Option 1: Using the startup script**
```bash
python start.py
```

**Option 2: Using main.py directly**
```bash
python main.py
```

**Option 3: Using uvicorn**
```bash
uvicorn main:create_app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

The backend provides the following API endpoints:

- **Agents**: `/api/v1/agents/*` - AI agent management
- **Properties**: `/api/v1/properties/*` - Property data
- **Market Data**: `/api/v1/market-data/*` - Market intelligence
- **Leads**: `/api/v1/leads/*` - Lead management
- **AI Insights**: `/api/v1/ai-insights/*` - AI-generated insights
- **WebSocket**: `/api/v1/ws/*` - Real-time communication
- **Health**: `/api/v1/health/*` - System health checks

### WebSocket Connection

Connect to the WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/your-client-id');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Real-time update:', data);
};
```

### AI Agents

The system includes several specialized AI agents:

- **Eden**: AI Insights and Property Analysis
- **Orion**: Google Gemini AI Integration
- **Atelius**: ATTOM Real Estate Data
- **Nova**: Market Intelligence and Trends
- **Zenith**: Lead Qualification and Management

## Development

### Project Structure

- **agents/**: AI agent implementations
- **api/**: REST API endpoints and routing
- **config/**: Configuration management
- **core/**: Core system components
- **models/**: Database models and schemas

### Adding New Agents

1. Create a new agent class in `agents/`
2. Implement the required methods
3. Register the agent in `AgentManager`
4. Add API endpoints if needed

### Adding New Endpoints

1. Create endpoint module in `api/v1/endpoints/`
2. Define routes and handlers
3. Include in `api/v1/api.py`

## Configuration

The system uses environment-based configuration through `config/settings.py`. Key settings include:

- Database connection
- Redis configuration
- API keys
- Server settings
- CORS configuration
- Logging levels

## Monitoring

- **Health Checks**: `/health` and `/api/v1/health/*`
- **Logging**: Structured logging with structlog
- **Metrics**: Built-in performance monitoring

## Troubleshooting

### Common Issues

1. **Database Connection**: Verify PostgreSQL is running and credentials are correct
2. **Redis Connection**: Ensure Redis server is running
3. **API Keys**: Verify all required API keys are set in `.env`
4. **Port Conflicts**: Check if port 8000 is available

### Logs

Check the application logs for detailed error information. The system uses structured logging for better debugging.

## Contributing

1. Follow the existing code structure
2. Add proper error handling
3. Include type hints
4. Write docstrings for all functions
5. Test your changes thoroughly

## License

[Add your license information here]

## Support

For support and questions, please refer to the project documentation or create an issue in the repository.
