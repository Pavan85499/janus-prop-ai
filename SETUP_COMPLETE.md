# Janus Prop AI - Complete Setup Guide

This guide will help you set up the complete Janus Prop AI system with Gemini API and ATTOM Real Estate Data integration.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+ installed
- Node.js 18+ installed
- Git installed
- API keys for Gemini and ATTOM (see API Setup section)

### 2. Clone and Setup
```bash
git clone <your-repo-url>
cd janus-prop-ai
```

## 🔧 Backend Setup

### 1. Install Python Dependencies
```bash
cd Backend/AI_bot
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in `Backend/AI_bot/` directory:

```bash
# OpenAI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini Configuration (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# ATTOM Data Configuration (Required)
ATTOM_API_KEY=your_attom_api_key_here
ATTOM_BASE_URL=https://api.attomdata.com/v3.0

# System Configuration
LOG_LEVEL=INFO
MAX_CONCURRENT_AGENTS=10
SYSTEM_TIMEOUT=300
```

### 3. Start Backend Server
```bash
python api_server.py
```

The backend will start on `http://localhost:8000`

## 🎨 Frontend Setup

### 1. Install Dependencies
```bash
cd Frontend
npm install
```

### 2. Configure Environment Variables
Create a `.env.local` file in the `Frontend/` directory:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Feature Flags
VITE_ENABLE_REAL_TIME_UPDATES=false
VITE_ENABLE_AGENT_CONSOLE=true

# Development Settings
VITE_DEBUG_MODE=true
VITE_LOG_LEVEL=info
```

### 3. Start Frontend Development Server
```bash
npm run dev
```

The frontend will start on `http://localhost:5173`

## 🔑 API Key Setup

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key (it's free with generous quotas)

### ATTOM Real Estate Data API
1. Visit [ATTOM Data Solutions](https://api.attomdata.com/)
2. Sign up for an account
3. Choose your subscription plan
4. Generate an API key

## 🧪 Testing the System

### 1. Backend Health Check
```bash
curl http://localhost:8000/health
```

### 2. Test Gemini AI Agent
```bash
curl -X POST http://localhost:8000/api/gemini/analyze-property \
  -H "Content-Type: application/json" \
  -d '{"property_data": {"address": "123 Main St", "price": 500000}}'
```

### 3. Test ATTOM Data Agent
```bash
curl http://localhost:8000/api/attom/property/123%20Main%20St
```

### 4. Check Agent Activity Console
```bash
curl http://localhost:8000/api/agents/activity
```

## 🌐 Frontend Features

### Agent Activity Console
- **Location**: Floating button (bottom-right corner)
- **Features**: 
  - Real-time agent status monitoring
  - Activity feed with Gemini and ATTOM integrations
  - Connection status indicators
  - Manual refresh capabilities

### AI Insights Panel
- **Location**: Dashboard tab
- **Features**:
  - Property analysis using Gemini AI
  - Explainable insights with confidence scores
  - Actionable recommendations

### Data Integration Dashboard
- **Location**: Dashboard tab
- **Features**:
  - ATTOM data source monitoring
  - Property search and filtering
  - Market trend analysis

## 🔍 Troubleshooting

### Common Issues

#### Backend Won't Start
- Check if all dependencies are installed
- Verify API keys are set correctly
- Check if port 8000 is available

#### Frontend Can't Connect to Backend
- Ensure backend is running on port 8000
- Check CORS settings
- Verify API base URL in frontend config

#### Gemini API Errors
- Verify API key is correct
- Check if you have sufficient quota
- Ensure proper environment variable format

#### ATTOM API Errors
- Verify API key and subscription status
- Check rate limits
- Ensure proper URL encoding

### Debug Mode
Enable debug logging in backend:
```bash
LOG_LEVEL=DEBUG
```

### Network Issues
- Check firewall settings
- Verify localhost access
- Test with different ports if needed

## 📊 System Architecture

### Backend Agents
1. **Gemini AI Agent**: AI-powered property analysis
2. **ATTOM Data Agent**: Real estate data integration
3. **AI Insights Agent**: OpenAI-powered insights (optional)
4. **Data Integration Agent**: Multi-source data management
5. **Feedback Learning Agent**: Continuous improvement

### Frontend Components
1. **Agent Activity Console**: Real-time monitoring
2. **AI Insights Panel**: Gemini-powered analysis
3. **Data Integration Dashboard**: ATTOM data management
4. **Property Management**: Search and filtering
5. **Market Intelligence**: Trend analysis

## 🚀 Production Deployment

### Backend
1. Use proper secret management
2. Implement rate limiting
3. Set up monitoring and logging
4. Use HTTPS
5. Implement authentication

### Frontend
1. Build for production: `npm run build`
2. Deploy to CDN or hosting service
3. Configure environment variables
4. Set up proper CORS policies

## 📚 API Documentation

### Core Endpoints
- `GET /health` - Health check
- `GET /api/agents/activity` - Agent activities
- `GET /api/agents/status` - Agent statuses

### Gemini AI Endpoints
- `POST /api/gemini/analyze-property` - Property analysis
- `POST /api/gemini/generate-insights` - Generate insights
- `POST /api/gemini/market-analysis` - Market analysis

### ATTOM Data Endpoints
- `GET /api/attom/property/{address}` - Property data
- `POST /api/attom/search` - Property search
- `GET /api/attom/market/{location}` - Market data
- `POST /api/attom/comparables` - Comparable sales
- `GET /api/attom/foreclosure/{location}` - Foreclosure data

## 🆘 Support

### Documentation
- Backend: `Backend/AI_bot/CONFIGURATION_GUIDE.md`
- Frontend: `Frontend/AGENT_CONSOLE_SETUP.md`

### API References
- [Google Gemini API](https://ai.google.dev/docs)
- [ATTOM Data API](https://api.attomdata.com/docs)
- [OpenAI API](https://platform.openai.com/docs)

### Getting Help
1. Check the troubleshooting section
2. Review configuration guides
3. Test individual components
4. Check logs for error messages

## 🎯 Next Steps

1. **Customize Agents**: Modify agent behavior and capabilities
2. **Add Data Sources**: Integrate additional real estate APIs
3. **Enhance UI**: Customize frontend components and styling
4. **Scale System**: Add more agents and improve performance
5. **Production Ready**: Implement authentication and security measures

---

**🎉 Congratulations!** You now have a fully functional AI-powered real estate analysis system with Gemini AI and ATTOM data integration.
