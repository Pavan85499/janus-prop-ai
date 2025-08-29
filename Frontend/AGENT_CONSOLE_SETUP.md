# AI Agent Activity Console Setup Guide

This guide explains how to set up and connect the AI Agent Activity Console to the backend.

## Prerequisites

1. **Backend Running**: Ensure the Python backend is running on `http://localhost:8000`
2. **Frontend Dependencies**: Install frontend dependencies with `npm install`

## Configuration

### Environment Variables

Create a `.env.local` file in the Frontend directory with:

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

### Backend Configuration

Ensure your backend has the following endpoints available:

- `GET /health` - Health check endpoint
- `GET /api/agents/activity` - Get agent activities
- `GET /api/agents/status` - Get agent statuses
- `POST /api/agents/activity/dismiss` - Dismiss activity
- `GET /api/system/status` - Get system status

## Features

### Real-time Updates
- **Polling**: Automatically refreshes data every 10 seconds
- **Connection Monitoring**: Shows connection status to backend
- **Error Handling**: Displays connection errors and retry options

### Agent Activity Display
- **Live Status**: Shows current agent activities and statuses
- **Activity Types**: In-progress, completed, and alert activities
- **Agent Icons**: Visual representation of different agent types
- **Dismiss Actions**: Remove completed or alert activities

### Connection Indicators
- **WiFi Icon**: Shows connection status on the floating button
- **Offline Badge**: Indicates when backend is unreachable
- **Refresh Button**: Manual refresh option

## Usage

1. **Start Backend**: Run the Python backend server
2. **Start Frontend**: Run `npm run dev` in the Frontend directory
3. **Access Console**: Click the floating activity button (bottom-right)
4. **Monitor Activities**: View real-time agent activities and statuses

## Troubleshooting

### Backend Connection Issues
- Check if backend is running on the correct port
- Verify CORS settings in backend
- Check network connectivity

### No Activities Displayed
- Ensure backend agents are running
- Check backend logs for errors
- Verify API endpoints are working

### Performance Issues
- Adjust polling interval in `src/lib/config.ts`
- Check backend response times
- Monitor network requests in browser dev tools

## Development

### Adding New Agent Types
1. Update `agentIcons` and `agentColors` in `AgentActivityConsole.tsx`
2. Add new agent types to backend configuration
3. Update agent status endpoints

### Customizing Polling
- Modify `pollingInterval` in `useAgentActivity` hook
- Update `config.agentConsole.pollingInterval`
- Adjust connection check intervals

### Error Handling
- Customize error messages in `agentService.ts`
- Add toast notifications for user feedback
- Implement retry logic for failed requests

## API Reference

### Agent Activity Response
```typescript
interface AgentActivityResponse {
  activities: AgentActivity[];
  summary: {
    total_activities: number;
    active_tasks: number;
    completed_tasks: number;
    alerts: number;
    system_status: any;
  };
}
```

### Agent Status Response
```typescript
interface AgentsStatusResponse {
  agents: Record<string, AgentStatus>;
  total_agents: number;
  healthy_agents: number;
  timestamp: string;
}
```

## Security Considerations

- API endpoints should implement proper authentication
- CORS settings should be configured appropriately
- Rate limiting should be implemented on backend
- Sensitive agent information should be filtered

## Future Enhancements

- WebSocket support for real-time updates
- Push notifications for critical alerts
- Agent performance metrics dashboard
- Activity filtering and search capabilities
- Export functionality for activity logs
