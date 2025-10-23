#!/bin/bash
# PostgreSQL Setup Script for Thai Model Chat History

echo "🐘 Setting up PostgreSQL for Thai Model Chat History"
echo "=================================================="

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed"
    echo ""
    echo "📦 Installing PostgreSQL..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        sudo apt update
        sudo apt install -y postgresql postgresql-contrib
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install postgresql
        else
            echo "❌ Please install Homebrew first: https://brew.sh"
            exit 1
        fi
    else
        echo "❌ Unsupported OS. Please install PostgreSQL manually."
        exit 1
    fi
fi

# Start PostgreSQL service
echo "🚀 Starting PostgreSQL service..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew services start postgresql
fi

echo "✅ PostgreSQL service started"

# Create database and user
echo ""
echo "🔧 Setting up database and user..."
echo ""

# Generate secure password
DB_PASSWORD=$(openssl rand -base64 12)

echo "📋 Database Configuration:"
echo "   Database: thai_chat"
echo "   Username: thai_user"
echo "   Password: $DB_PASSWORD"
echo ""

# Create database setup SQL
cat > /tmp/setup_thai_db.sql << EOF
-- Create database
CREATE DATABASE thai_chat;

-- Create user
CREATE USER thai_user WITH ENCRYPTED PASSWORD '$DB_PASSWORD';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE thai_chat TO thai_user;

-- Connect to the new database
\c thai_chat

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO thai_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO thai_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO thai_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO thai_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO thai_user;

EOF

# Execute SQL as postgres user
sudo -u postgres psql < /tmp/setup_thai_db.sql

# Clean up
rm /tmp/setup_thai_db.sql

echo "✅ Database setup completed!"
echo ""

# Create environment file
ENV_FILE="../.env"
echo "💾 Creating environment configuration..."

cat > $ENV_FILE << EOF
# PostgreSQL Configuration for Thai Model Chat History
DATABASE_URL=postgresql://thai_user:$DB_PASSWORD@localhost:5432/thai_chat

# Alternative individual settings (if needed)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=thai_chat
DB_USER=thai_user
DB_PASSWORD=$DB_PASSWORD
EOF

echo "✅ Environment file created: $ENV_FILE"
echo ""

# Test connection
echo "🧪 Testing database connection..."
export DATABASE_URL="postgresql://thai_user:$DB_PASSWORD@localhost:5432/thai_chat"

if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection failed"
    echo "💡 You may need to configure PostgreSQL authentication"
    echo "   Edit /etc/postgresql/*/main/pg_hba.conf if needed"
fi

echo ""
echo "🎉 PostgreSQL setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Install Python dependencies:"
echo "   pip install psycopg2-binary sqlalchemy"
echo ""
echo "2. Load environment variables:"
echo "   source .env"
echo ""
echo "3. Test the chat database:"
echo "   python3 -c \"from thai_model.core.chat_database import ChatDatabaseManager; ChatDatabaseManager().test_connection()\""
echo ""
echo "4. Start using database-backed chat history in your web interface!"
echo ""
echo "🔐 Database credentials saved in .env file"
echo "⚠️  Keep the .env file secure and don't commit it to version control!"