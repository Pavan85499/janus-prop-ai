# Database Management Scripts

This directory contains comprehensive database management scripts for the Janus Prop AI Backend.

## Available Scripts

### 1. `setup_database.py` - Database Setup and Configuration

**Purpose**: Complete database setup and configuration management.

**Usage**:
```bash
# Run complete database setup
python scripts/setup_database.py --setup

# Show database status
python scripts/setup_database.py --status

# Run health checks
python scripts/setup_database.py --health

# Force setup (overwrite existing configuration)
python scripts/setup_database.py --setup --force
```

**Features**:
- Automatic detection of Supabase vs PostgreSQL setup
- Dependency checking
- Connection testing
- Schema application
- Health monitoring

### 2. `apply_supabase_schema.py` - Schema Application

**Purpose**: Apply the Supabase database schema to the configured database.

**Usage**:
```bash
# Apply schema to Supabase database
python scripts/apply_supabase_schema.py
```

**Features**:
- Reads and executes `supabase_schema.sql`
- Handles SQL statement parsing
- Error handling and logging
- Supabase configuration validation

### 3. `migrate_database.py` - Database Migrations

**Purpose**: Manage database migrations and schema updates.

**Usage**:
```bash
# Create a new migration
python scripts/migrate_database.py --create add_new_field --description "Add new field to users table"

# Apply pending migrations
python scripts/migrate_database.py --up

# Apply migrations up to specific target
python scripts/migrate_database.py --up --target 20240101_120000_add_new_field.sql

# Rollback migrations
python scripts/migrate_database.py --down 20240101_120000_add_new_field.sql

# Show migration status
python scripts/migrate_database.py --status

# List all migrations
python scripts/migrate_database.py --list

# Dry run (show what would be done)
python scripts/migrate_database.py --up --dry-run
```

**Features**:
- Migration file creation with templates
- Up and down migration support
- Migration tracking in database
- Dry run capability
- Rollback functionality

### 4. `backup_database.py` - Database Backup and Restore

**Purpose**: Comprehensive database backup and restore functionality.

**Usage**:
```bash
# Create full database backup
python scripts/backup_database.py --backup full

# Create data-only backup (JSON format)
python scripts/backup_database.py --backup data

# Create backup with custom filename
python scripts/backup_database.py --backup full --filename my_backup.sql

# List available backups
python scripts/backup_database.py --list

# Restore from backup
python scripts/backup_database.py --restore backup_20240101_120000.sql

# Restore with data replacement
python scripts/backup_database.py --restore backup_20240101_120000.sql --drop-existing

# Clean up old backups (older than 30 days)
python scripts/backup_database.py --cleanup 30
```

**Features**:
- Full SQL dumps using pg_dump
- Data-only JSON backups
- Automatic backup file naming
- Restore functionality
- Backup cleanup
- Support for both Supabase and PostgreSQL

### 5. `validate_database.py` - Database Validation

**Purpose**: Comprehensive database validation and health checking.

**Usage**:
```bash
# Run full validation
python scripts/validate_database.py --full

# Validate specific components
python scripts/validate_database.py --config
python scripts/validate_database.py --connections
python scripts/validate_database.py --schema
python scripts/validate_database.py --data
python scripts/validate_database.py --performance
```

**Features**:
- Configuration validation
- Connection testing
- Schema validation
- Data integrity checks
- Performance testing
- Comprehensive reporting

## Quick Start Guide

### 1. Initial Setup

```bash
# 1. Copy environment template
cp env.example .env

# 2. Edit .env with your database credentials
# For Supabase:
SUPABASE_PROJECT_ID=your_project_id
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key

# For local PostgreSQL:
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/janus_prop_ai

# 3. Run database setup
python scripts/setup_database.py --setup

# 4. Verify setup
python scripts/setup_database.py --status
```

### 2. Schema Management

```bash
# Apply initial schema (for Supabase)
python scripts/apply_supabase_schema.py

# Create a migration for schema changes
python scripts/migrate_database.py --create update_properties_table --description "Add new fields to properties table"

# Apply migrations
python scripts/migrate_database.py --up
```

### 3. Backup and Restore

```bash
# Create regular backup
python scripts/backup_database.py --backup full

# Schedule backups (add to crontab)
# Daily backup at 2 AM
0 2 * * * cd /path/to/backend && python scripts/backup_database.py --backup full

# Clean up old backups weekly
0 3 * * 0 cd /path/to/backend && python scripts/backup_database.py --cleanup 30
```

### 4. Monitoring and Validation

```bash
# Run health checks
python scripts/validate_database.py --full

# Check specific components
python scripts/validate_database.py --connections
python scripts/validate_database.py --performance
```

## Environment Configuration

All scripts use the same environment configuration as the main application. Key variables:

### Supabase Configuration
```bash
SUPABASE_PROJECT_ID=your_project_id
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
```

### PostgreSQL Configuration
```bash
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/janus_prop_ai
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### Redis Configuration
```bash
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   ```bash
   # Check configuration
   python scripts/setup_database.py --status
   
   # Validate connections
   python scripts/validate_database.py --connections
   ```

2. **Schema Issues**
   ```bash
   # Check schema
   python scripts/validate_database.py --schema
   
   # Reapply schema
   python scripts/apply_supabase_schema.py
   ```

3. **Migration Problems**
   ```bash
   # Check migration status
   python scripts/migrate_database.py --status
   
   # Rollback problematic migration
   python scripts/migrate_database.py --down problematic_migration.sql
   ```

4. **Backup/Restore Issues**
   ```bash
   # List available backups
   python scripts/backup_database.py --list
   
   # Test restore with dry run
   python scripts/backup_database.py --restore backup.sql --dry-run
   ```

### Debug Mode

Enable debug mode for detailed logging:
```bash
DEBUG=true LOG_LEVEL=DEBUG python scripts/setup_database.py --setup
```

## Best Practices

1. **Regular Backups**: Set up automated daily backups
2. **Migration Testing**: Always test migrations in development first
3. **Health Monitoring**: Run validation checks regularly
4. **Environment Separation**: Use different databases for dev/staging/prod
5. **Documentation**: Document all custom migrations and changes

## Security Considerations

1. **Credentials**: Never commit `.env` files with real credentials
2. **Backups**: Secure backup files with appropriate permissions
3. **Access Control**: Limit database access to necessary users only
4. **Audit Logs**: Monitor database access and changes

## Integration with CI/CD

Example GitHub Actions workflow:
```yaml
name: Database Validation
on: [push, pull_request]

jobs:
  validate-db:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Validate Database
        run: python scripts/validate_database.py --full
        env:
          DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
```

## Support

For issues or questions:
1. Check the main project documentation
2. Review script logs for error details
3. Run validation scripts to identify problems
4. Create an issue in the project repository
