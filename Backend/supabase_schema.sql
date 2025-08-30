-- =====================================================
-- Janus Prop AI - Supabase Database Schema
-- =====================================================
-- This schema creates all necessary tables, indexes, and RLS policies
-- for the Janus Prop AI real estate platform

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- =====================================================
-- AGENTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    agent_type VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agents indexes
CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_agents_active ON agents(is_active);
CREATE INDEX IF NOT EXISTS idx_agents_config ON agents USING GIN(config);

-- =====================================================
-- PROPERTIES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Basic property information
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(20),
    county VARCHAR(100),
    country VARCHAR(50) DEFAULT 'USA',
    
    -- Property details
    property_type VARCHAR(100) NOT NULL,
    property_subtype VARCHAR(100),
    bedrooms INTEGER,
    bathrooms DECIMAL(4,2),
    square_feet INTEGER,
    lot_size INTEGER,
    year_built INTEGER,
    
    -- Financial information
    list_price DECIMAL(15,2),
    estimated_value DECIMAL(15,2),
    last_sold_price DECIMAL(15,2),
    last_sold_date TIMESTAMP WITH TIME ZONE,
    tax_assessment DECIMAL(15,2),
    property_tax DECIMAL(15,2),
    
    -- Property status
    status VARCHAR(50) DEFAULT 'active',
    listing_date TIMESTAMP WITH TIME ZONE,
    days_on_market INTEGER DEFAULT 0,
    
    -- Property features
    features JSONB,
    description TEXT,
    images JSONB,
    
    -- Location data
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    neighborhood VARCHAR(100),
    school_district VARCHAR(100),
    
    -- Market data
    market_data JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- External IDs
    mls_id VARCHAR(100),
    zillow_id VARCHAR(100),
    redfin_id VARCHAR(100),
    attom_id VARCHAR(100),
    
    -- Agent assignment
    assigned_agent_id UUID REFERENCES agents(id) ON DELETE SET NULL
);

-- Properties indexes
CREATE INDEX IF NOT EXISTS idx_properties_address ON properties(address);
CREATE INDEX IF NOT EXISTS idx_properties_city ON properties(city);
CREATE INDEX IF NOT EXISTS idx_properties_state ON properties(state);
CREATE INDEX IF NOT EXISTS idx_properties_zip ON properties(zip_code);
CREATE INDEX IF NOT EXISTS idx_properties_type ON properties(property_type);
CREATE INDEX IF NOT EXISTS idx_properties_subtype ON properties(property_subtype);
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_agent ON properties(assigned_agent_id);
CREATE INDEX IF NOT EXISTS idx_properties_mls ON properties(mls_id);
CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(list_price, estimated_value);
CREATE INDEX IF NOT EXISTS idx_properties_features ON properties USING GIN(features);
CREATE INDEX IF NOT EXISTS idx_properties_market_data ON properties USING GIN(market_data);
CREATE INDEX IF NOT EXISTS idx_properties_images ON properties USING GIN(images);

-- Full-text search index for properties
CREATE INDEX IF NOT EXISTS idx_properties_search ON properties USING GIN(
    to_tsvector('english', 
        COALESCE(address, '') || ' ' || 
        COALESCE(city, '') || ' ' || 
        COALESCE(state, '') || ' ' || 
        COALESCE(description, '') || ' ' ||
        COALESCE(neighborhood, '')
    )
);

-- =====================================================
-- LEADS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    source VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'new',
    priority VARCHAR(50) DEFAULT 'medium',
    assigned_agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    notes JSONB,
    tags JSONB,
    budget_range VARCHAR(100),
    property_preferences JSONB,
    lead_score VARCHAR(10) DEFAULT '0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Leads indexes
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_priority ON leads(priority);
CREATE INDEX IF NOT EXISTS idx_leads_agent ON leads(assigned_agent_id);
CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_leads_notes ON leads USING GIN(notes);
CREATE INDEX IF NOT EXISTS idx_leads_tags ON leads USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_leads_preferences ON leads USING GIN(property_preferences);

-- =====================================================
-- MARKET_DATA TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location VARCHAR(255) NOT NULL,
    property_type VARCHAR(100) NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    value DECIMAL(15,2),
    trend VARCHAR(50),
    period VARCHAR(50),
    data_source VARCHAR(100) NOT NULL,
    data_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market data indexes
CREATE INDEX IF NOT EXISTS idx_market_data_location ON market_data(location);
CREATE INDEX IF NOT EXISTS idx_market_data_type ON market_data(property_type);
CREATE INDEX IF NOT EXISTS idx_market_data_data_type ON market_data(data_type);
CREATE INDEX IF NOT EXISTS idx_market_data_source ON market_data(data_source);
CREATE INDEX IF NOT EXISTS idx_market_data_created ON market_data(created_at);
CREATE INDEX IF NOT EXISTS idx_market_data_metadata ON market_data USING GIN(data_metadata);

-- =====================================================
-- AI_INSIGHTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS ai_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    insight_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    confidence_score DECIMAL(3,2),
    ai_model VARCHAR(100) NOT NULL,
    tags JSONB,
    insight_metadata JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI insights indexes
CREATE INDEX IF NOT EXISTS idx_ai_insights_property ON ai_insights(property_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_type ON ai_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_ai_insights_model ON ai_insights(ai_model);
CREATE INDEX IF NOT EXISTS idx_ai_insights_active ON ai_insights(is_active);
CREATE INDEX IF NOT EXISTS idx_ai_insights_confidence ON ai_insights(confidence_score);
CREATE INDEX IF NOT EXISTS idx_ai_insights_created ON ai_insights(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_insights_tags ON ai_insights USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_ai_insights_metadata ON ai_insights USING GIN(insight_metadata);

-- =====================================================
-- ADDITIONAL TABLES FOR RELATIONSHIPS
-- =====================================================

-- User-Agent assignments table
CREATE TABLE IF NOT EXISTS user_agent_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, agent_id)
);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) ENABLING
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_agent_assignments ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES
-- =====================================================

-- Users table policies
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Users can insert their own profile" ON users
    FOR INSERT WITH CHECK (auth.uid()::text = id::text);

-- Agents table policies
CREATE POLICY "Anyone can view active agents" ON agents
    FOR SELECT USING (is_active = true);

CREATE POLICY "Only authenticated users can view all agents" ON agents
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Only authenticated users can manage agents" ON agents
    FOR ALL USING (auth.role() = 'authenticated');

-- Properties table policies
CREATE POLICY "Anyone can view active properties" ON properties
    FOR SELECT USING (is_active = true AND status != 'off_market');

CREATE POLICY "Authenticated users can view all properties" ON properties
    FOR SELECT USING (auth.role() = 'authenticated');

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

CREATE POLICY "Only authenticated users can manage properties" ON properties
    FOR ALL USING (auth.role() = 'authenticated');

-- Leads table policies
CREATE POLICY "Assigned agents can view their leads" ON leads
    FOR SELECT USING (
        assigned_agent_id::text = (
            SELECT id::text FROM agents 
            WHERE id IN (
                SELECT agent_id FROM user_agent_assignments 
                WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Only authenticated users can manage leads" ON leads
    FOR ALL USING (auth.role() = 'authenticated');

-- Market data table policies
CREATE POLICY "Anyone can view market data" ON market_data
    FOR SELECT USING (true);

CREATE POLICY "Only authenticated users can manage market data" ON market_data
    FOR ALL USING (auth.role() = 'authenticated');

-- AI insights table policies
CREATE POLICY "Anyone can view active AI insights" ON ai_insights
    FOR SELECT USING (is_active = true);

CREATE POLICY "Authenticated users can view all AI insights" ON ai_insights
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Only authenticated users can manage AI insights" ON ai_insights
    FOR ALL USING (auth.role() = 'authenticated');

-- User-Agent assignments policies
CREATE POLICY "Users can view their own agent assignments" ON user_agent_assignments
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Only authenticated users can manage user-agent assignments" ON user_agent_assignments
    FOR ALL USING (auth.role() = 'authenticated');

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_market_data_updated_at BEFORE UPDATE ON market_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_insights_updated_at BEFORE UPDATE ON ai_insights
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SEARCH FUNCTIONS
-- =====================================================

-- Function for property search
CREATE OR REPLACE FUNCTION search_properties(
    search_term TEXT DEFAULT '',
    property_type_filter VARCHAR(100) DEFAULT NULL,
    city_filter VARCHAR(100) DEFAULT NULL,
    state_filter VARCHAR(50) DEFAULT NULL,
    min_price DECIMAL(15,2) DEFAULT NULL,
    max_price DECIMAL(15,2) DEFAULT NULL,
    min_bedrooms INTEGER DEFAULT NULL,
    max_bedrooms INTEGER DEFAULT NULL,
    limit_count INTEGER DEFAULT 50
)
RETURNS TABLE(
    id UUID,
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    property_type VARCHAR(100),
    list_price DECIMAL(15,2),
    bedrooms INTEGER,
    bathrooms DECIMAL(4,2),
    square_feet INTEGER,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    similarity_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.address,
        p.city,
        p.state,
        p.property_type,
        p.list_price,
        p.bedrooms,
        p.bathrooms,
        p.square_feet,
        p.latitude,
        p.longitude,
        CASE 
            WHEN search_term != '' THEN 
                GREATEST(
                    similarity(p.address, search_term),
                    similarity(p.city, search_term),
                    similarity(p.state, search_term)
                )
            ELSE 0
        END as similarity_score
    FROM properties p
    WHERE p.is_active = true
        AND (property_type_filter IS NULL OR p.property_type = property_type_filter)
        AND (city_filter IS NULL OR p.city ILIKE '%' || city_filter || '%')
        AND (state_filter IS NULL OR p.state = state_filter)
        AND (min_price IS NULL OR p.list_price >= min_price)
        AND (max_price IS NULL OR p.list_price <= max_price)
        AND (min_bedrooms IS NULL OR p.bedrooms >= min_bedrooms)
        AND (max_bedrooms IS NULL OR p.bedrooms <= max_bedrooms)
        AND (search_term = '' OR 
            p.address ILIKE '%' || search_term || '%' OR
            p.city ILIKE '%' || search_term || '%' OR
            p.state ILIKE '%' || search_term || '%'
        )
    ORDER BY similarity_score DESC, p.created_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Property summary view
CREATE OR REPLACE VIEW property_summary AS
SELECT 
    p.id,
    p.address,
    p.city,
    p.state,
    p.zip_code,
    p.property_type,
    p.property_subtype,
    p.bedrooms,
    p.bathrooms,
    p.square_feet,
    p.list_price,
    p.estimated_value,
    p.status,
    p.listing_date,
    p.days_on_market,
    p.latitude,
    p.longitude,
    a.name as agent_name,
    COUNT(ai.id) as insight_count,
    AVG(ai.confidence_score) as avg_confidence
FROM properties p
LEFT JOIN agents a ON p.assigned_agent_id = a.id
LEFT JOIN ai_insights ai ON p.id = ai.property_id AND ai.is_active = true
WHERE p.is_active = true
GROUP BY p.id, a.name;

-- Market trends view
CREATE OR REPLACE VIEW market_trends AS
SELECT 
    md.location,
    md.property_type,
    md.data_type,
    md.trend,
    md.period,
    md.data_source,
    AVG(md.value) as avg_value,
    COUNT(*) as data_points,
    MAX(md.created_at) as last_updated
FROM market_data md
GROUP BY md.location, md.property_type, md.data_type, md.trend, md.period, md.data_source;

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Grant necessary permissions to authenticated users
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Grant INSERT, UPDATE, DELETE permissions to authenticated users for management
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE users IS 'User accounts and authentication information';
COMMENT ON TABLE agents IS 'AI agents for property analysis and insights';
COMMENT ON TABLE properties IS 'Real estate properties with comprehensive details';
COMMENT ON TABLE leads IS 'Customer leads and prospects';
COMMENT ON TABLE market_data IS 'Market trends and analytics data';
COMMENT ON TABLE ai_insights IS 'AI-generated insights about properties';
COMMENT ON TABLE user_agent_assignments IS 'User to agent assignment relationships';

COMMENT ON FUNCTION search_properties IS 'Search properties with filters and similarity scoring';
COMMENT ON VIEW property_summary IS 'Summary view of properties with agent and insight information';
COMMENT ON VIEW market_trends IS 'Aggregated market trends and analytics';

-- =====================================================
-- SCHEMA COMPLETE
-- =====================================================
