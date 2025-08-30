# Frontend-Backend Connection Guide

This guide explains how to connect your Frontend to the Backend and test the connection.

## 🚀 **Quick Start**

### **1. Start the Backend**
```bash
cd Backend
python quick_fix.py  # Creates minimal .env file
python start.py      # Starts the backend server
```

The Backend will start on `http://localhost:8000` with:
- ✅ Basic API endpoints working
- ✅ Health check available at `/health`
- ✅ CORS enabled for Frontend requests
- ⚠️ Database and Redis disabled (gracefully handled)

### **2. Start the Frontend**
```bash
cd Frontend
npm run dev
```

The Frontend will start on `http://localhost:5173` and automatically connect to the Backend.

## 🔧 **Connection Status**

### **Real-time Status Indicator**
- **Top-right corner**: Shows backend connection status
- **Green badge**: Connected to backend
- **Red badge**: Disconnected from backend
- **Click to expand**: See detailed status information

### **Status Meanings**
- 🟢 **Connected**: Backend is reachable and responding
- 🔴 **Disconnected**: Backend is not reachable
- 🟡 **Connecting**: Attempting to connect
- ⚠️ **Degraded**: Some services are unavailable

## 📡 **API Endpoints Available**

### **Health & Status**
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system status
- `GET /supabase/status` - Supabase connection status
- `GET /supabase/config` - Supabase configuration

### **Agents & AI**
- `GET /api/agents/activity` - Agent activity feed
- `GET /api/agents/status` - Agent status overview
- `POST /api/gemini/analyze-property` - AI property analysis
- `POST /api/attom/property/{address}` - Property data lookup

## 🧪 **Testing the Connection**

### **Backend Test Page**
Visit `/backend-test` to run comprehensive connection tests:

1. **Health Check**: Basic backend responsiveness
2. **Detailed Health**: System component status
3. **Supabase Config**: Database configuration
4. **Supabase Status**: Database connectivity
5. **Connection Test**: Quick connectivity verification

### **Manual Testing**
```bash
# Test backend health
curl http://localhost:8000/health

# Test CORS (from browser console)
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
```

## ⚙️ **Configuration**

### **Frontend Environment Variables**
```bash
# .env.local (optional)
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
```

### **Backend Environment Variables**
```bash
# Backend/.env
DEBUG=true
LOG_LEVEL=INFO

# For Supabase (optional)
SUPABASE_PROJECT_ID=your_project_id
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_URL=https://your_project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Backend Won't Start**
```bash
# Check if port 8000 is available
netstat -an | findstr :8000  # Windows
lsof -i :8000                # Mac/Linux

# Kill process using port 8000
taskkill /PID <PID> /F       # Windows
kill -9 <PID>                # Mac/Linux
```

#### **2. CORS Errors**
- Ensure Backend is running on `http://localhost:8000`
- Check that CORS middleware is enabled in Backend
- Verify Frontend is making requests to correct URL

#### **3. Connection Timeout**
- Check if Backend is responding: `curl http://localhost:8000/health`
- Verify network connectivity
- Check firewall settings

#### **4. API Endpoints Not Found**
- Ensure Backend started successfully
- Check Backend logs for startup errors
- Verify API routes are properly registered

### **Debug Steps**

1. **Check Backend Logs**
   ```bash
   cd Backend
   python start.py
   # Look for startup messages and errors
   ```

2. **Check Frontend Console**
   - Open browser DevTools
   - Look for network errors
   - Check console for connection messages

3. **Test Individual Endpoints**
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Detailed health
   curl http://localhost:8000/health/detailed
   ```

## 🎯 **Next Steps**

### **Enable Full Functionality**

1. **Configure Supabase**
   ```bash
   cd Backend
   python setup_env.py
   # Choose option 1 (Supabase)
   ```

2. **Apply Database Schema**
   ```bash
   cd Backend
   python scripts/apply_supabase_schema.py
   ```

3. **Start with Full Features**
   ```bash
   python start.py
   # Backend will now have database and full functionality
   ```

### **Test AI Features**

1. **Property Analysis**
   - Navigate to dashboard
   - Select a property
   - Use AI insights panel

2. **Agent Activity**
   - Monitor agent console
   - View real-time updates
   - Test agent interactions

## 📊 **Monitoring & Health**

### **Health Check Endpoints**
- `/health` - Quick status check
- `/health/detailed` - Comprehensive system status
- `/supabase/status` - Database connectivity

### **Real-time Monitoring**
- Backend status indicator in Frontend
- Automatic health checks every 30 seconds
- Connection status updates in real-time

## 🔐 **Security Considerations**

### **Development Environment**
- CORS enabled for localhost
- No authentication required for health endpoints
- Debug mode enabled

### **Production Considerations**
- Disable debug mode
- Implement proper authentication
- Configure CORS for production domains
- Use environment variables for sensitive data

## 📚 **Additional Resources**

- [Backend API Documentation](./Backend/README.md)
- [Supabase Integration Guide](./Backend/SUPABASE_INTEGRATION.md)
- [Frontend Component Library](./Frontend/src/components/ui/)
- [API Service Layer](./Frontend/src/lib/)

## 🆘 **Getting Help**

If you encounter issues:

1. Check the troubleshooting section above
2. Review Backend logs for error messages
3. Test individual endpoints manually
4. Verify environment configuration
5. Check network connectivity

The connection should work out of the box with the minimal configuration. If you need help, start with the health check endpoint and work your way up to more complex features.
