# Backend Configuration Guide

This guide explains how to configure the Janus Prop AI backend with Gemini API and ATTOM Real Estate Data APIs.

## Environment Variables

Create a `.env` file in the `Backend/AI_bot/` directory with the following variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# ATTOM Data Configuration
ATTOM_API_KEY=your_attom_api_key_here
ATTOM_BASE_URL=https://api.attomdata.com/v3.0

# Realie API Configuration
REALIE_API_KEY=your_realie_api_key_here
REALIE_BASE_URL=https://api.realie.com/v1

# System Configuration
LOG_LEVEL=INFO
MAX_CONCURRENT_AGENTS=10
SYSTEM_TIMEOUT=300

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/janus_prop_ai

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Security Configuration
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API Key Setup

### 1. Google Gemini API

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key and add it to your `.env` file
5. The Gemini API is free for development with generous quotas

### 2. ATTOM Real Estate Data API

1. Visit [ATTOM Data Solutions](https://api.attomdata.com/)
2. Sign up for an account
3. Choose your subscription plan
4. Generate an API key
5. Add the API key to your `.env` file

### 3. OpenAI API (Optional)

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or sign in
3. Navigate to API Keys
4. Create a new API key
5. Add it to your `.env` file

## Installation

1. **Install Dependencies**
   ```bash
   cd Backend/AI_bot
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the Backend**
   ```bash
   python api_server.py
   ```

## API Endpoints

### Gemini AI Endpoints

- `POST /api/gemini/analyze-property` - Analyze properties using Gemini
- `POST /api/gemini/generate-insights` - Generate AI insights
- `POST /api/gemini/market-analysis` - Perform market analysis

### ATTOM Data Endpoints

- `GET /api/attom/property/{address}` - Get property data
- `POST /api/attom/search` - Search properties
- `GET /api/attom/market/{location}` - Get market data
- `POST /api/attom/comparables` - Get comparable sales
- `GET /api/attom/foreclosure/{location}` - Get foreclosure data

### Agent Activity Endpoints

- `GET /api/agents/activity` - Get agent activities
- `GET /api/agents/status` - Get agent statuses
- `POST /api/agents/activity/dismiss` - Dismiss activities

## Testing the Setup

1. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Gemini Agent**
   ```bash
   curl -X POST http://localhost:8000/api/gemini/analyze-property \
     -H "Content-Type: application/json" \
     -d '{"property_data": {"address": "123 Main St", "price": 500000}}'
   ```

3. **Test ATTOM Agent**
   ```bash
   curl http://localhost:8000/api/attom/property/123%20Main%20St
   ```

4. **Check Agent Activity**
   ```bash
   curl http://localhost:8000/api/agents/activity
   ```

## Troubleshooting

### Common Issues

1. **Gemini API Key Error**
   - Verify your API key is correct
   - Check if you have sufficient quota
   - Ensure the key is properly set in `.env`

2. **ATTOM API Connection Issues**
   - Verify your API key and subscription status
   - Check rate limits
   - Ensure proper URL formatting

3. **Agent Initialization Failures**
   - Check all required environment variables
   - Verify API keys are valid
   - Check network connectivity

### Debug Mode

Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

### Rate Limiting

ATTOM API has rate limits based on your subscription:
- Basic: 100 requests/minute
- Professional: 500 requests/minute
- Enterprise: Custom limits

## Security Considerations

1. **Never commit API keys to version control**
2. **Use environment variables for sensitive data**
3. **Implement proper authentication for production**
4. **Monitor API usage and costs**
5. **Set up alerts for quota limits**

## Production Deployment

1. **Use proper secret management**
2. **Implement rate limiting**
3. **Set up monitoring and logging**
4. **Use HTTPS in production**
5. **Implement proper CORS policies**
6. **Set up health checks and alerts**

## Support

- **Gemini API**: [Google AI Studio Documentation](https://ai.google.dev/docs)
- **ATTOM API**: [ATTOM API Documentation](https://api.attomdata.com/docs)
- **OpenAI API**: [OpenAI API Documentation](https://platform.openai.com/docs)
