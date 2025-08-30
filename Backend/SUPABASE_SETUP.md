# Supabase Setup Guide for Janus Prop AI

This guide explains how to set up and use the Supabase database schema for the Janus Prop AI platform.

## Overview

The schema includes 7 main tables with comprehensive Row Level Security (RLS) policies, optimized indexes, and advanced search functionality for real estate data management.

## Database Tables

### 1. Users Table (`users`)
- **Purpose**: User accounts and authentication
- **Key Fields**: `id`, `email`, `username`, `full_name`, `is_active`
- **RLS**: Users can only access their own profile

### 2. Agents Table (`agents`)
- **Purpose**: AI agents for property analysis
- **Key Fields**: `id`, `name`, `agent_type`, `description`, `config` (JSONB)
- **RLS**: Public read access for active agents, admin-only management

### 3. Properties Table (`properties`)
- **Purpose**: Real estate properties with comprehensive details
- **Key Fields**: Address, location, financial data, features, market data
- **RLS**: Public read for active properties, agent-specific access, admin management
- **Special Features**: Full-text search, geospatial indexing, JSONB for flexible data

### 4. Leads Table (`leads`)
- **Purpose**: Customer leads and prospects
- **Key Fields**: Contact info, status, priority, assigned agent, preferences
- **RLS**: Agent-specific access to assigned leads, admin management

### 5. Market Data Table (`market_data`)
- **Purpose**: Market trends and analytics
- **Key Fields**: Location, property type, data type, value, trend
- **RLS**: Public read access, admin-only management

### 6. AI Insights Table (`ai_insights`)
- **Purpose**: AI-generated property insights
- **Key Fields**: Property reference, insight type, confidence score, AI model
- **RLS**: Public read for active insights, admin management

### 7. User-Agent Assignments Table (`user_agent_assignments`)
- **Purpose**: Manage user-to-agent relationships
- **Key Fields**: `user_id`, `agent_id`, assignment tracking
- **RLS**: Users can view their own assignments, admin management

## Row Level Security (RLS) Policies

### Authentication-Based Access
- **Public Access**: Market data, active properties, active AI insights
- **Authenticated Users**: All properties, all AI insights, agent information
- **User-Specific**: Profile data, assigned leads, agent assignments
- **Admin-Only**: Full CRUD operations on all tables

### Policy Examples

```sql
-- Users can only access their own profile
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

-- Public can view active properties
CREATE POLICY "Anyone can view active properties" ON properties
    FOR SELECT USING (is_active = true AND status != 'off_market');

-- Agents can access their assigned properties
CREATE POLICY "Assigned agents can view their properties" ON properties
    FOR SELECT USING (
        assigned_agent_id::text = (
            SELECT id::text FROM agents 
            WHERE id IN (
                SELECT agent_id FROM user_agent_assignments 
                WHERE user_id = auth.uid()
            )
        )
    );
```

## Advanced Features

### 1. Full-Text Search
```sql
-- Search properties with similarity scoring
SELECT * FROM search_properties(
    search_term := 'downtown apartment',
    property_type_filter := 'residential',
    city_filter := 'New York',
    min_price := 500000,
    max_price := 2000000,
    limit_count := 25
);
```

### 2. JSONB Indexing
- **Features**: Amenities, upgrades, property characteristics
- **Market Data**: Market trends, comparables, analytics
- **Images**: Property photo URLs and metadata
- **Tags**: Flexible categorization system

### 3. Geospatial Support
- **Latitude/Longitude**: Precise location data
- **Neighborhood**: Area classification
- **School District**: Educational boundaries
- **Location-based queries**: Proximity searches

### 4. Optimized Indexes
- **B-tree**: Standard field indexing (email, status, dates)
- **GIN**: JSONB and full-text search indexing
- **Composite**: Multi-field optimization (price ranges, location)
- **Partial**: Conditional indexing (active records only)

## Setup Instructions

### 1. Create Supabase Project
```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Create new project
supabase projects create janus-prop-ai

# Link local project
supabase link --project-ref YOUR_PROJECT_REF
```

### 2. Apply Schema
```bash
# Apply the schema
supabase db reset

# Or apply manually in Supabase dashboard SQL editor
# Copy and paste the contents of supabase_schema.sql
```

### 3. Configure Authentication
```sql
-- Enable email authentication
-- Configure JWT settings
-- Set up admin role
```

### 4. Test RLS Policies
```sql
-- Test as anonymous user
SELECT * FROM properties WHERE is_active = true;

-- Test as authenticated user
-- Test as admin user
```

## Usage Examples

### Property Search
```typescript
// Frontend TypeScript example
const searchProperties = async (filters: PropertyFilters) => {
  const { data, error } = await supabase
    .rpc('search_properties', {
      search_term: filters.searchTerm,
      property_type_filter: filters.propertyType,
      city_filter: filters.city,
      min_price: filters.minPrice,
      max_price: filters.maxPrice,
      min_bedrooms: filters.minBedrooms,
      max_bedrooms: filters.maxBedrooms,
      limit_count: 50
    });
  
  return { data, error };
};
```

### Lead Management
```typescript
// Get leads assigned to current user's agents
const getAssignedLeads = async () => {
  const { data, error } = await supabase
    .from('leads')
    .select(`
      *,
      agents!leads_assigned_agent_id_fkey (
        name,
        agent_type
      )
    `)
    .eq('assigned_agent_id', userAgentId);
  
  return { data, error };
};
```

### AI Insights
```typescript
// Get insights for a specific property
const getPropertyInsights = async (propertyId: string) => {
  const { data, error } = await supabase
    .from('ai_insights')
    .select('*')
    .eq('property_id', propertyId)
    .eq('is_active', true)
    .order('confidence_score', { ascending: false });
  
  return { data, error };
};
```

## Performance Optimization

### 1. Index Strategy
- **Primary Keys**: UUID with default generation
- **Foreign Keys**: Referenced table lookups
- **Search Fields**: Full-text and similarity search
- **JSONB Fields**: GIN indexes for flexible queries

### 2. Query Optimization
- **Pagination**: Use `limit_count` parameter
- **Filtering**: Apply filters early in query
- **Joins**: Minimize unnecessary table joins
- **Views**: Use summary views for complex aggregations

### 3. Caching Strategy
- **Redis**: Session and temporary data
- **Database**: Materialized views for heavy aggregations
- **Application**: In-memory caching for frequently accessed data

## Security Considerations

### 1. RLS Policies
- **Principle of Least Privilege**: Users only access necessary data
- **Role-Based Access**: Different permissions for different user types
- **Data Isolation**: Users cannot access other users' data

### 2. Authentication
- **JWT Tokens**: Secure session management
- **Role Claims**: Embedded in JWT for policy evaluation
- **Token Expiration**: Configurable security timeouts

### 3. Data Validation
- **Input Sanitization**: Prevent SQL injection
- **Type Checking**: Ensure data integrity
- **Constraint Validation**: Database-level data validation

## Monitoring and Maintenance

### 1. Performance Monitoring
```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Monitor slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### 2. Regular Maintenance
- **Vacuum**: Clean up dead tuples
- **Analyze**: Update table statistics
- **Reindex**: Optimize index performance
- **Backup**: Regular database backups

### 3. Health Checks
```sql
-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check RLS status
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';
```

## Troubleshooting

### Common Issues

1. **RLS Policy Errors**
   - Check user authentication status
   - Verify JWT token validity
   - Review policy conditions

2. **Performance Issues**
   - Analyze query execution plans
   - Check index usage statistics
   - Optimize slow queries

3. **Permission Denied**
   - Verify user roles and permissions
   - Check RLS policy conditions
   - Ensure proper authentication

### Debug Queries
```sql
-- Check current user context
SELECT auth.uid(), auth.role(), auth.jwt();

-- Test RLS policies
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM properties;

-- Verify table structure
\d+ properties
```

## Next Steps

1. **Data Migration**: Import existing data from other sources
2. **API Integration**: Connect backend services to Supabase
3. **Real-time Features**: Enable real-time subscriptions
4. **Advanced Analytics**: Implement complex reporting queries
5. **Performance Tuning**: Monitor and optimize based on usage patterns

## Support

For additional support:
- Check Supabase documentation
- Review RLS policy examples
- Monitor database performance metrics
- Test security policies thoroughly
