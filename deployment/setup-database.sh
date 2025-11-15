#!/bin/bash

# Database setup script for ibhoom PostgreSQL database
# Run this script as root or with sudo

set -e

echo "🚀 Setting up PostgreSQL database for ibhoom..."

# Database configuration
DB_NAME="ibhoom_db"
DB_USER="ibhoom_user"
DB_PASSWORD=""

# Generate a random password if not provided
if [ -z "$DB_PASSWORD" ]; then
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    echo "Generated password: $DB_PASSWORD"
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib
fi

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Switch to postgres user and create database
sudo -u postgres psql << EOF
-- Create database
CREATE DATABASE $DB_NAME;

-- Create user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Grant schema privileges (for PostgreSQL 15+)
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;

-- Exit
\q
EOF

# Configure PostgreSQL for production (3GB RAM server)
echo "📝 Configuring PostgreSQL for production..."

PG_VERSION=$(psql --version | grep -oP '\d+' | head -1)
PG_CONF="/etc/postgresql/${PG_VERSION}/main/postgresql.conf"
PG_HBA="/etc/postgresql/${PG_VERSION}/main/pg_hba.conf"

# Backup original config
sudo cp "$PG_CONF" "${PG_CONF}.backup"

# Update PostgreSQL configuration for 3GB RAM
sudo sed -i "s/#shared_buffers = 128MB/shared_buffers = 256MB/" "$PG_CONF"
sudo sed -i "s/#effective_cache_size = 4GB/effective_cache_size = 1GB/" "$PG_CONF"
sudo sed -i "s/#maintenance_work_mem = 64MB/maintenance_work_mem = 64MB/" "$PG_CONF"
sudo sed -i "s/#work_mem = 4MB/work_mem = 4MB/" "$PG_CONF"
sudo sed -i "s/#max_connections = 100/max_connections = 100/" "$PG_CONF"

# Enable logging
sudo sed -i "s/#logging_collector = off/logging_collector = on/" "$PG_CONF"
sudo sed -i "s/#log_directory = 'log'/log_directory = 'log'/" "$PG_CONF"
sudo sed -i "s/#log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'/log_filename = 'postgresql-%Y-%m-%d.log'/" "$PG_CONF"

# Restart PostgreSQL
sudo systemctl restart postgresql

echo "✅ Database setup complete!"
echo ""
echo "📋 Database Connection Details:"
echo "   Database Name: $DB_NAME"
echo "   Database User: $DB_USER"
echo "   Database Password: $DB_PASSWORD"
echo "   Connection String: postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "⚠️  IMPORTANT: Save this password! You'll need it for your .env file."
echo ""
echo "💡 To test the connection:"
echo "   psql -U $DB_USER -d $DB_NAME -h localhost"

