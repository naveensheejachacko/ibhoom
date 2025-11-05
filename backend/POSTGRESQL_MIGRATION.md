# PostgreSQL Migration Guide

This guide explains how to migrate from SQLite to PostgreSQL (Aiven).

## ✅ Changes Made

1. **Added PostgreSQL Driver**: `psycopg2-binary==2.9.9` to `requirements.txt`
2. **Updated Database Configuration**: Enhanced `database.py` to handle PostgreSQL SSL connections
3. **Connection Pooling**: Added connection pooling for better PostgreSQL performance

## 📋 Setup Instructions

### 1. Install PostgreSQL Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install `psycopg2-binary` which is required for PostgreSQL connections.

### 2. Create `.env` File

Create a `.env` file in the `backend/` directory with your PostgreSQL connection string:

```env
# Database Configuration
DATABASE_URL=postgresql://avnadmin:AVNS_T29-wXlhuJYupmnZfY3@pg-32ed7144-naveensheejachacko-1c5e.c.aivencloud.com:24184/defaultdb?sslmode=require

# JWT Configuration (keep your existing values)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:3000

# App Configuration
DEBUG=True
```

**Important**: The `.env` file is already in `.gitignore` to protect your credentials.

### 3. Test Database Connection

You can test the connection using Python:

```python
from app.core.database import engine
from sqlalchemy import text

# Test connection
with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print("PostgreSQL version:", result.fetchone()[0])
```

### 4. Create Database Tables

The application will automatically create tables when it starts. However, if you want to create them manually:

```python
from app.core.database import create_database
create_database()
```

Or run:
```bash
python -c "from app.core.database import create_database; create_database()"
```

### 5. Migrate Existing Data (Optional)

If you have existing SQLite data you want to migrate:

1. Export data from SQLite:
   ```bash
   sqlite3 marketplace.db .dump > sqlite_dump.sql
   ```

2. Convert SQLite SQL to PostgreSQL format (you may need to adjust the SQL)
3. Import into PostgreSQL using `psql` or a migration tool

**Note**: For production, consider using Alembic migrations instead of `create_all()`.

## 🔧 Configuration Details

### Connection String Format

The connection string format for Aiven PostgreSQL:
```
postgresql://username:password@host:port/database?sslmode=require
```

### SSL Configuration

Aiven requires SSL connections. The system automatically:
- Detects `sslmode=require` in the connection string
- Passes SSL parameters to the PostgreSQL driver
- Uses secure connections for all database operations

### Connection Pooling

PostgreSQL connections are now pooled for better performance:
- **Pool Size**: 5 connections
- **Max Overflow**: 10 additional connections
- **Pool Pre-ping**: Enabled (verifies connections before use)

## 🚀 Running the Application

After setup, run the application as usual:

```bash
cd backend
uvicorn app.main:app --reload
```

The application will automatically use PostgreSQL if `DATABASE_URL` is set in the `.env` file.

## 🔄 Switching Back to SQLite

If you need to switch back to SQLite for local development:

1. Set `DATABASE_URL` in `.env` to:
   ```env
   DATABASE_URL=sqlite:///./marketplace.db
   ```

2. The application will automatically detect and use SQLite

## ⚠️ Important Notes

1. **Backup First**: Always backup your data before migrating
2. **Test Locally**: Test the PostgreSQL connection before deploying to production
3. **Environment Variables**: Never commit `.env` files to version control
4. **Password Security**: The connection string contains sensitive credentials - keep it secure

## 🐛 Troubleshooting

### Connection Errors

If you get connection errors:
1. Verify the connection string is correct
2. Check that the Aiven PostgreSQL instance is running
3. Ensure your IP is whitelisted in Aiven (if required)
4. Verify SSL is properly configured

### SSL Errors

If you get SSL-related errors:
- Ensure `sslmode=require` is in your connection string
- Check that `psycopg2-binary` is installed
- Verify Aiven SSL certificates are accessible

### Import Errors

If `psycopg2` import fails:
```bash
pip install psycopg2-binary
```

## 📚 Additional Resources

- [Aiven PostgreSQL Documentation](https://aiven.io/docs/products/postgresql)
- [SQLAlchemy PostgreSQL Dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

