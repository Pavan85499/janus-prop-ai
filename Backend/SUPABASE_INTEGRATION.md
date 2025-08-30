# Supabase Integration Guide for Janus Prop AI Backend

This guide explains how to configure and use Supabase as the database for the Janus Prop AI Backend.

## Overview

The Backend has been updated to support both local PostgreSQL and Supabase databases. When Supabase is configured, it will automatically use the Supabase database instead of the local one.

## Environment Variables

Add these environment variables to your `.env` file:

```bash
# Supabase Configuration
SUPABASE_PROJECT_ID=your_project_id_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
SUPABASE_URL=https://your_project_id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here

# Optional: Keep local database as fallback
DATABASE_URL=postgresql://user:password@localhost:5432/janus_prop_ai
```

## Getting Supabase Credentials

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up/Login and create a new project
3. Wait for the project to be ready

### 2. Get Project Credentials
1. Go to Project Settings → API
2. Copy the following values:
   - **Project ID**: Found in the URL and Project Settings
   - **Project URL**: The full URL of your project
   - **Anon Key**: Public API key for client-side operations
   - **Service Role Key**: Secret key for server-side operations (keep this secure!)

## Database Setup

### 1. Apply the Schema
The Backend includes a pre-configured schema with RLS policies. Apply it using:

```bash
# Option 1: Use the Python script
cd Backend
python scripts/apply_supabase_schema.py

# Option 2: Use Supabase CLI
supabase db reset

# Option 3: Copy-paste in Supabase Dashboard
# Go to SQL Editor and paste the contents of supabase_schema.sql
```

### 2. Verify Tables
After applying the schema, you should see these tables:
- `users`
- `agents`
- `properties`
- `leads`
- `market_data`
- `ai_insights`
- `user_agent_assignments`

## Features

### 1. Automatic Database Selection
The Backend automatically detects Supabase configuration and switches to it:

```python
from config.settings import get_settings

settings = get_settings()
if settings.is_supabase_enabled:
    print("Using Supabase database")
else:
    print("Using local database")
```

### 2. Row Level Security (RLS)
All tables have RLS enabled with appropriate policies:
- **Public Access**: Market data, active properties, active insights
- **Authenticated Users**: Full access to their data and public data
- **Data Isolation**: Users can only access their own data

### 3. Supabase Client Integration
```python
from core.supabase_client import get_supabase_client

# Get Supabase client
client = get_supabase_client()

# Query data
response = client.table('properties').select('*').execute()
properties = response.data
```

### 4. Database Adapters
Use the Supabase adapters for CRUD operations:

```python
from core.supabase_adapter import properties_adapter

# Create property
property_data = {
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "property_type": "residential"
}
new_property = await properties_adapter.create(property_data)

# Get property by ID
property = await properties_adapter.get_by_id("uuid-here")

# Search properties
results = await properties_adapter.search("New York", ["city", "state"])
```

## API Endpoints

### Health Check
- **GET** `/api/v1/health/` - Includes Supabase status
- **GET** `/api/v1/health/detailed` - Detailed system status

### Supabase Configuration
- **GET** `/api/v1/supabase/config` - Get Supabase config for frontend
- **GET** `/api/v1/supabase/status` - Check Supabase connection status
- **POST** `/api/v1/supabase/test-connection` - Test Supabase connectivity

## Testing the Integration

### 1. Health Check
```bash
curl http://localhost:8000/api/v1/health/
```

Expected response includes Supabase status:
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "websocket": "healthy",
    "supabase": "healthy"
  }
}
```

### 2. Supabase Status
```bash
curl http://localhost:8000/api/v1/supabase/status
```

Expected response:
```json
{
  "enabled": true,
  "connected": true,
  "project_id": "your_project_id",
  "url": "https://your_project_id.supabase.co"
}
```

### 3. Test Connection
```bash
curl -X POST http://localhost:8000/api/v1/supabase/test-connection
```

## Troubleshooting

### Common Issues

#### 1. "Supabase not configured" Error
- Check that all environment variables are set
- Verify the variable names match exactly
- Restart the application after setting environment variables

#### 2. Connection Failed
- Verify the service role key is correct
- Check that the project ID matches the URL
- Ensure the project is active and not paused

#### 3. RLS Policy Errors
- Verify the schema was applied correctly
- Check that RLS is enabled on all tables
- Ensure policies are created without errors

#### 4. Permission Denied
- Check that the service role key has proper permissions
- Verify RLS policies are working correctly
- Test with a simple query first

### Debug Steps

1. **Check Environment Variables**
   ```bash
   echo $SUPABASE_PROJECT_ID
   echo $SUPABASE_URL
   ```

2. **Test Supabase Connection**
   ```bash
   python -c "
   from core.supabase_client import test_supabase_connection
   import asyncio
   print(asyncio.run(test_supabase_connection()))
   "
   ```

3. **Check Database Logs**
   - Look for connection errors in application logs
   - Check Supabase dashboard for any errors

4. **Verify Schema**
   - Check that all tables exist in Supabase
   - Verify RLS is enabled on all tables
   - Check that policies are created

## Performance Considerations

### 1. Connection Pooling
- Supabase handles connection pooling automatically
- The Backend uses appropriate pool settings for Supabase

### 2. Query Optimization
- Use the provided search functions for complex queries
- Leverage Supabase's built-in full-text search
- Use appropriate indexes (already configured in schema)

### 3. Caching
- Redis is still used for session management
- Consider implementing query result caching for frequently accessed data

## Security

### 1. Environment Variables
- Never commit `.env` files to version control
- Use secure methods to manage production credentials
- Rotate service role keys regularly

### 2. RLS Policies
- All tables have RLS enabled
- Policies enforce data isolation
- Users can only access their own data

### 3. API Keys
- Anon key is safe for client-side use
- Service role key should only be used server-side
- Monitor API usage in Supabase dashboard

## Migration from Local Database

### 1. Data Export
```bash
# Export from local PostgreSQL
pg_dump -h localhost -U username -d janus_prop_ai > backup.sql
```

### 2. Data Import
```bash
# Import to Supabase (using service role key)
psql "postgresql://postgres.your_project_id:service_role_key@host.supabase.co:5432/postgres" < backup.sql
```

### 3. Update Configuration
- Set Supabase environment variables
- Restart the application
- Verify data is accessible

## Next Steps

1. **Apply the Schema**: Use the provided script or Supabase dashboard
2. **Test Connectivity**: Verify all endpoints work correctly
3. **Monitor Performance**: Check Supabase dashboard for query performance
4. **Set Up Monitoring**: Configure alerts for connection issues
5. **Backup Strategy**: Set up regular database backups

## Support

For additional help:
- Check Supabase documentation
- Review the schema file for table structures
- Test individual components step by step
- Monitor application logs for errors
