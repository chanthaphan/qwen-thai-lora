#!/bin/bash
# OpenAI API Key Setup Script

echo "🔑 OpenAI API Key Setup for Thai Model Project"
echo "=============================================="
echo ""

# Check if API key is already set
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OpenAI API key is already set!"
    echo "Current key: ${OPENAI_API_KEY:0:20}..."
    echo ""
    echo "If you want to change it, run: unset OPENAI_API_KEY"
    echo "Then run this script again."
    exit 0
fi

echo "❌ OpenAI API key is not set."
echo ""
echo "📋 Steps to get your OpenAI API key:"
echo "1. Visit: https://platform.openai.com/api-keys"
echo "2. Sign in to your OpenAI account"
echo "3. Click 'Create new secret key'"
echo "4. Copy the generated key"
echo ""

# Prompt for API key
echo "🔐 Please enter your OpenAI API key:"
echo "(It will be hidden for security)"
echo -n "API Key: "
read -s api_key
echo ""

# Validate key format (basic check)
if [ ${#api_key} -lt 20 ]; then
    echo "❌ API key seems too short. Please check and try again."
    exit 1
fi

if [[ ! $api_key == sk-* ]]; then
    echo "⚠️  Warning: OpenAI API keys usually start with 'sk-'"
    echo "Are you sure this is correct? (y/N)"
    read -n 1 confirmation
    echo ""
    if [[ ! $confirmation =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled."
        exit 1
    fi
fi

# Set the API key for current session
export OPENAI_API_KEY="$api_key"

# Ask if user wants to make it permanent
echo ""
echo "✅ API key set for current session!"
echo ""
echo "🔄 Would you like to make this permanent? (y/N)"
echo "This will add the key to your ~/.bashrc file."
read -n 1 make_permanent
echo ""

if [[ $make_permanent =~ ^[Yy]$ ]]; then
    # Check if already in bashrc
    if grep -q "OPENAI_API_KEY" ~/.bashrc; then
        echo "⚠️  Found existing OPENAI_API_KEY in ~/.bashrc"
        echo "Would you like to replace it? (y/N)"
        read -n 1 replace_existing
        echo ""
        if [[ $replace_existing =~ ^[Yy]$ ]]; then
            # Remove existing line
            sed -i '/OPENAI_API_KEY/d' ~/.bashrc
        else
            echo "❌ Setup cancelled to avoid duplicates."
            exit 1
        fi
    fi
    
    # Add to bashrc
    echo "" >> ~/.bashrc
    echo "# OpenAI API Key for Thai Model Project" >> ~/.bashrc
    echo "export OPENAI_API_KEY=\"$api_key\"" >> ~/.bashrc
    
    echo "✅ API key added to ~/.bashrc"
    echo "💡 It will be available in new terminal sessions."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🚀 You can now start the web interface with OpenAI support:"
echo "   ./manage.sh chat-web"
echo ""
echo "🌟 Available OpenAI models include:"
echo "   - GPT-4o (recommended)"
echo "   - GPT-4o-mini (faster, cheaper)"
echo "   - GPT-5 (latest model)"
echo "   - GPT-5-mini (latest mini model)"
echo ""
echo "💡 In the web interface, select 'OpenAI' from the Backend dropdown!"