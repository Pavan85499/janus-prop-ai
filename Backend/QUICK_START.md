# 🚀 Quick Start Guide - Janus Prop AI Backend

## ⚡ Quick Setup

### 1. Check Your Environment
```bash
cd Backend
python check_env.py
```

This will show you what's configured and what's missing.

### 2. Install Dependencies
```bash
# Make sure you're in your virtual environment
pip install -r requirements.txt
```

### 3. Configure Environment Variables

#### Option A: Use Supabase (Recommended)
Create a `.env` file with:
```bash
SUPABASE_PROJECT_ID=your_project_id
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_URL=https://your_project_id.supabase.co
SUPABASE_ANON_KEY=your_anon_key
```

#### Option B: Use Local Database
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/janus_prop_ai
```

### 4. Test Configuration
```bash
# If using Supabase
python test_supabase.py

# Check environment
python check_env.py
```

### 5. Start the Backend
```bash
python start.py
```

## 🔧 Troubleshooting

### Common Issues

#### 1. "asyncpg driver not available"
```bash
pip install asyncpg
```

#### 2. "Supabase not configured"
- Check your `.env` file exists
- Verify all Supabase variables are set
- Restart your terminal after setting variables

#### 3. "Database connection failed"
- Verify your database is running
- Check connection strings
- Ensure firewall/network access

### Quick Fixes

#### Reset Virtual Environment
```bash
# Windows
deactivate
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Mac/Linux
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Check Dependencies
```bash
pip list | grep -E "(sqlalchemy|asyncpg|supabase)"
```

## 📚 Next Steps

1. **Read the full guide**: `SUPABASE_INTEGRATION.md`
2. **Apply database schema**: Use the provided scripts
3. **Test endpoints**: Check `/api/v1/health/` when running
4. **Explore API docs**: Visit `/docs` when the server is running

## 🆘 Need Help?

- Check the logs when starting the server
- Run `python check_env.py` to verify configuration
- Review `SUPABASE_INTEGRATION.md` for detailed setup
- Ensure all environment variables are properly set
