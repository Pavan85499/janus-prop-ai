# AI Agents System for Janus Prop AI

A comprehensive AI agent management and orchestration system built for real estate investment analysis and automation.

## 🚀 Features

### Core Capabilities
- **Multi-Agent Architecture**: Coordinated system of specialized AI agents
- **Real-time Communication**: WebSocket and Redis-based real-time updates
- **Task Management**: Intelligent task distribution and processing
- **Workflow Orchestration**: Complex multi-step workflows across agents
- **Health Monitoring**: Comprehensive agent health and performance tracking
- **Activity Logging**: Detailed activity logs and audit trails

### Specialized Agents

#### 🤖 Eden - AI Insights Agent
- **Type**: AI Insights and Property Analysis
- **Capabilities**: Property valuation, investment scoring, risk assessment, market analysis
- **Max Concurrent Tasks**: 3
- **Priority**: High

#### 🧠 Orion - Gemini AI Agent
- **Type**: Google Gemini AI Integration
- **Capabilities**: Natural language processing, content generation, data analysis
- **Max Concurrent Tasks**: 5
- **Priority**: High

#### 📊 Atelius - ATTOM Data Agent
- **Type**: ATTOM Real Estate Data
- **Capabilities**: Property data collection, market data analysis, comparable research
- **Max Concurrent Tasks**: 4
- **Priority**: High

#### 📈 Nova - Market Analysis Agent
- **Type**: Market Intelligence and Trends
- **Capabilities**: Market condition analysis, trend prediction, economic analysis
- **Max Concurrent Tasks**: 3
- **Priority**: Normal

#### 🎯 Zenith - Lead Management Agent
- **Type**: Lead Qualification and Management
- **Capabilities**: Lead scoring, qualification, automated follow-up
- **Max Concurrent Tasks**: 2
- **Priority**: Normal

#### 🏠 Aurora - Property Analysis Agent
- **Type**: Advanced Property Analysis
- **Capabilities**: Property inspection analysis, renovation estimation, investment strategies
- **Max Concurrent Tasks**: 2
- **Priority**: Normal

#### 📄 Celestia - Document Processing Agent
- **Type**: Document Processing
- **Capabilities**: Document analysis, data extraction, contract review
- **Max Concurrent Tasks**: 3
- **Priority**: Normal

#### 🏛️ Valyria - Investment Committee Agent
- **Type**: Investment Committee
- **Capabilities**: Investment decisions, committee debates, memo generation
- **Max Concurrent Tasks**: 2
- **Priority**: High

## 🏗️ Architecture

### Database Schema

#### AI Agents Table
```sql
CREATE TABLE ai_agents (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    description TEXT,
    version VARCHAR(20) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT TRUE,
    config JSONB,
    capabilities JSONB,
    limitations JSONB,
    max_concurrent_tasks INTEGER DEFAULT 5,
    priority VARCHAR(20) DEFAULT 'normal',
    health_score DECIMAL(3,2) DEFAULT 1.0,
    average_response_time DECIMAL(10,2) DEFAULT 0.0,
    total_tasks_completed INTEGER DEFAULT 0,
    total_tasks_failed INTEGER DEFAULT 0,
    total_runtime_hours DECIMAL(10,2) DEFAULT 0.0,
    current_status VARCHAR(20) DEFAULT 'offline',
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_error TEXT,
    last_error_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID
);
```

#### Agent Tasks Table
```sql
CREATE TABLE agent_tasks (
    id UUID PRIMARY KEY,
    agent_id UUID NOT NULL REFERENCES ai_agents(id),
    task_type VARCHAR(100) NOT NULL,
    title VARCHAR(200),
    description TEXT,
    priority VARCHAR(20) DEFAULT 'normal',
    status VARCHAR(20) DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    progress DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    estimated_duration INTEGER,
    actual_duration INTEGER,
    metadata JSONB,
    tags JSONB,
    created_by UUID
);
```

#### Agent Activities Table
```sql
CREATE TABLE agent_activities (
    id UUID PRIMARY KEY,
    agent_id UUID NOT NULL REFERENCES ai_agents(id),
    activity_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    level VARCHAR(20) DEFAULT 'info',
    status VARCHAR(20) DEFAULT 'in_progress',
    task_id UUID,
    property_id UUID,
    user_id UUID,
    data JSONB,
    metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    duration INTEGER
);
```

#### Agent Capabilities Table
```sql
CREATE TABLE agent_capabilities (
    id UUID PRIMARY KEY,
    agent_id UUID NOT NULL REFERENCES ai_agents(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    version VARCHAR(20) DEFAULT '1.0.0',
    is_enabled BOOLEAN DEFAULT TRUE,
    config JSONB,
    parameters JSONB,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    average_duration DECIMAL(10,2) DEFAULT 0.0,
    total_executions INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔧 API Endpoints

### Agent Management
- `GET /api/v1/ai-agents/` - List all agents
- `POST /api/v1/ai-agents/` - Create new agent
- `GET /api/v1/ai-agents/{agent_id}` - Get specific agent
- `PUT /api/v1/ai-agents/{agent_id}` - Update agent
- `DELETE /api/v1/ai-agents/{agent_id}` - Delete agent

### Agent Control
- `POST /api/v1/ai-agents/{agent_id}/start` - Start agent
- `POST /api/v1/ai-agents/{agent_id}/stop` - Stop agent
- `POST /api/v1/ai-agents/{agent_id}/restart` - Restart agent

### Task Management
- `POST /api/v1/ai-agents/{agent_id}/tasks` - Create task for agent
- `GET /api/v1/ai-agents/{agent_id}/tasks` - Get agent tasks
- `GET /api/v1/ai-agents/tasks/{task_id}` - Get specific task
- `PUT /api/v1/ai-agents/tasks/{task_id}` - Update task
- `POST /api/v1/ai-agents/{agent_id}/tasks/cancel` - Cancel agent tasks

### Activity Management
- `POST /api/v1/ai-agents/{agent_id}/activities` - Create activity log
- `GET /api/v1/ai-agents/{agent_id}/activities` - Get agent activities

### Health & Monitoring
- `GET /api/v1/ai-agents/{agent_id}/health` - Get agent health
- `GET /api/v1/ai-agents/health/system` - Get system health

### Capability Management
- `POST /api/v1/ai-agents/{agent_id}/capabilities` - Create capability
- `GET /api/v1/ai-agents/{agent_id}/capabilities` - Get agent capabilities

### Real-time Updates
- `WebSocket /api/v1/ai-agents/ws/{agent_id}` - Real-time agent updates

## 🚀 Quick Start

### 1. Initialize the System
```bash
cd Backend
python scripts/initialize_ai_agents.py
```

### 2. Start the Backend
```bash
python main.py
```

### 3. Create a Task
```python
import requests

# Create a property analysis task
task_data = {
    "agent_id": "eden-agent-id",
    "task_type": "property_valuation",
    "title": "Property Valuation Analysis",
    "description": "Analyze property value for investment decision",
    "input_data": {
        "property": {
            "address": "123 Main Street, New York, NY 10001",
            "price": 500000,
            "sqft": 2000,
            "beds": 3,
            "baths": 2
        }
    },
    "priority": "high"
}

response = requests.post(
    "cdhttp://localhost:8000/api/v1/ai-agents/eden-agent-id/tasks",
    json=task_data
)
```

### 4. Monitor Progress
```python
# Get task status
task_id = response.json()["id"]
status_response = requests.get(
    f"http://localhost:8000/api/v1/ai-agents/tasks/{task_id}"
)

print(f"Task Status: {status_response.json()['status']}")
print(f"Progress: {status_response.json()['progress'] * 100}%")
```

## 🔄 Workflow Examples

### Property Analysis Workflow
1. **Atelius** collects property data from ATTOM
2. **Nova** analyzes market conditions
3. **Eden** performs property valuation
4. **Eden** calculates investment score
5. **Orion** generates comprehensive report

### Lead Qualification Workflow
1. **Zenith** scores lead quality
2. **Atelius** looks up property information
3. **Eden** assesses investment potential
4. **Orion** generates qualification summary

## 📊 Monitoring & Health

### Agent Health Metrics
- **Health Score**: 0.0 to 1.0 based on performance
- **Success Rate**: Percentage of completed tasks
- **Average Response Time**: Mean task completion time
- **Current Tasks**: Number of tasks currently running
- **Total Runtime**: Hours of active operation

### System Health
- **Total Agents**: Number of registered agents
- **Online Agents**: Number of currently active agents
- **Error Agents**: Number of agents in error state
- **System Health**: Overall system status (healthy/degraded/critical)

## 🔧 Configuration

### Environment Variables
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/janus_prop_ai

# AI Service Keys
GEMINI_API_KEY=your_gemini_api_key
ATTOM_API_KEY=your_attom_api_key
```

### Agent Configuration
```python
agent_config = {
    "max_concurrent_tasks": 5,
    "priority": "high",
    "health_check_interval": 30,
    "task_timeout": 300,
    "retry_attempts": 3
}
```

## 🛠️ Development

### Adding New Agents
1. Create agent class in `agents/` directory
2. Implement required methods: `start()`, `stop()`, `process_task()`
3. Register agent in orchestrator
4. Add agent type to `AgentType` enum
5. Update initialization script

### Adding New Capabilities
1. Define capability in agent class
2. Add capability to agent's capabilities list
3. Implement capability logic
4. Update database schema if needed

### Custom Workflows
1. Define workflow steps in orchestrator
2. Map input/output data between steps
3. Handle error cases and retries
4. Add workflow type to system

## 📈 Performance Optimization

### Task Distribution
- Agents automatically balance task load
- Priority-based task queuing
- Intelligent agent selection based on capabilities

### Caching
- Redis-based caching for frequently accessed data
- Agent status caching
- Task result caching

### Monitoring
- Real-time performance metrics
- Automated health checks
- Error detection and recovery

## 🔒 Security

### Authentication
- JWT-based authentication for API access
- Role-based access control
- Agent-specific permissions

### Data Protection
- Encrypted data transmission
- Secure credential storage
- Audit logging for all activities

## 📚 Documentation

### API Documentation
- Swagger UI available at `/docs`
- OpenAPI specification
- Interactive API explorer

### Code Documentation
- Comprehensive docstrings
- Type hints throughout
- Architecture diagrams

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation wiki

---

**Built with ❤️ for the Janus Prop AI platform**
