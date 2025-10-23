#!/bin/bash
# Simplified PostgreSQL Setup Script for Thai Model Chat History

echo "🐘 Setting up PostgreSQL for Thai Model Chat History"
echo "=================================================="

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    echo "❌ Please don't run this script as root"
    echo "💡 Run it as a regular user - it will use sudo when needed"
    exit 1
fi

# Check if PostgreSQL is installed and running
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed"
    echo "📦 Installing PostgreSQL..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
fi

# Ensure PostgreSQL is running
echo "🚀 Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Wait a moment for the service to start
sleep 2

echo "✅ PostgreSQL service is running"

# Generate secure password
DB_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/" | cut -c1-12)

echo ""
echo "📋 Database Configuration:"
echo "   Database: thai_chat"
echo "   Username: thai_user"
echo "   Password: $DB_PASSWORD"
echo ""

# Create database and user using peer authentication (as postgres user)
echo "🔧 Setting up database and user..."

# Create the setup SQL
sudo -u postgres psql << EOF
-- Drop existing database and user if they exist (for clean setup)
DROP DATABASE IF EXISTS thai_chat;
DROP USER IF EXISTS thai_user;

-- Create user
CREATE USER thai_user WITH ENCRYPTED PASSWORD '$DB_PASSWORD';

-- Create database
CREATE DATABASE thai_chat OWNER thai_user;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE thai_chat TO thai_user;

-- Connect to the database and set up schema privileges
\c thai_chat

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO thai_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO thai_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO thai_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO thai_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO thai_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO thai_user;

-- Show success
SELECT 'Database setup completed successfully!' as status;
EOF

if [ $? -eq 0 ]; then
    echo "✅ Database and user created successfully!"
else
    echo "❌ Database setup failed"
    exit 1
fi

# Configure PostgreSQL to allow password authentication for local connections
echo ""
echo "🔧 Configuring PostgreSQL authentication..."

PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version()" | grep -oP "PostgreSQL \K[0-9]+")
PG_HBA_FILE="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"

# Backup original pg_hba.conf
sudo cp "$PG_HBA_FILE" "$PG_HBA_FILE.backup"

# Create new pg_hba.conf with proper authentication
sudo bash -c "cat > $PG_HBA_FILE" << 'EOF'
# PostgreSQL Client Authentication Configuration File
# Thai Model Project Configuration

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             postgres                                peer
local   all             all                                     md5

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5

# IPv6 local connections:
host    all             all             ::1/128                 md5

# Allow replication connections from localhost
local   replication     all                                     peer
host    replication     all             127.0.0.1/32            md5
host    replication     all             ::1/128                 md5
EOF

echo "✅ PostgreSQL authentication configured"

# Reload PostgreSQL configuration
echo "🔄 Reloading PostgreSQL configuration..."
sudo systemctl reload postgresql

# Wait for reload
sleep 2

# Create environment file
ENV_FILE=".env"
echo "💾 Creating environment configuration..."

cat > $ENV_FILE << EOF
# PostgreSQL Configuration for Thai Model Chat History
# Generated on $(date)
DATABASE_URL=postgresql://thai_user:$DB_PASSWORD@localhost:5432/thai_chat

# Alternative individual settings (if needed)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=thai_chat
DB_USER=thai_user
DB_PASSWORD=$DB_PASSWORD
EOF

echo "✅ Environment file created: $ENV_FILE"

# Test the connection
echo ""
echo "🧪 Testing database connection..."

export DATABASE_URL="postgresql://thai_user:$DB_PASSWORD@localhost:5432/thai_chat"

# Test with psql
if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U thai_user -d thai_chat -c "SELECT 'Connection successful!' as status;" > /dev/null 2>&1; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection failed"
    echo "🔍 Troubleshooting information:"
    echo "   - Database: thai_chat"
    echo "   - User: thai_user"  
    echo "   - Host: localhost:5432"
    echo "   - Config: $PG_HBA_FILE"
    exit 1
fi

# Test Python connection
echo "🐍 Testing Python database connection..."
if python3 -c "
import psycopg2
import os
os.environ['DATABASE_URL'] = 'postgresql://thai_user:$DB_PASSWORD@localhost:5432/thai_chat'
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute('SELECT 1')
    print('✅ Python PostgreSQL connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Python connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    echo "✅ Python database connection works!"
else
    echo "⚠️ Python connection test skipped (psycopg2 not installed yet)"
    echo "💡 Install with: pip install psycopg2-binary"
fi

echo ""
echo "🎉 PostgreSQL setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Load environment variables:"
echo "   source .env"
echo ""
echo "2. Install Python dependencies (if not already installed):"
echo "   pip install psycopg2-binary sqlalchemy"
echo ""  
echo "3. Test the chat database:"
echo "   python3 -c \"import os; exec(open('.env').read().replace('export ', 'os.environ[\\\"').replace('=', '\\\"] = \\\"').replace('\\n', '\\\"\\nos.environ[\\\"')); from thai_model.core.chat_database import ChatDatabaseManager; print('✅ Success!' if ChatDatabaseManager().test_connection() else '❌ Failed')\""
echo ""
echo "4. Start using database-backed chat:"
echo "   ./manage.sh chat-web-db"
echo ""
echo "🔐 Database credentials saved in .env file"
echo "⚠️  Keep the .env file secure and don't commit it to version control!"
echo ""
echo "📊 Connection details:"
echo "   Database URL: postgresql://thai_user:***@localhost:5432/thai_chat"
echo "   Config file: $PG_HBA_FILE"
echo "   Log file: /var/log/postgresql/postgresql-$PG_VERSION-main.log"