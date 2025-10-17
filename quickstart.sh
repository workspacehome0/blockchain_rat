#!/bin/bash

# Blockchain RAT Quick Start Script

echo "=================================="
echo "Blockchain RAT - Quick Start"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3.11 --version || {
    echo "❌ Python 3.11 not found. Please install Python 3.11+"
    exit 1
}
echo "✅ Python 3.11 found"
echo ""

# Check Node.js
echo "Checking Node.js..."
node --version || {
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
}
echo "✅ Node.js found"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -q -r requirements.txt
echo "✅ Python dependencies installed"
echo ""

# Install smart contract dependencies
echo "Installing smart contract dependencies..."
cd contracts
npm install --silent
echo "✅ Smart contract dependencies installed"
echo ""

# Compile smart contract
echo "Compiling smart contract..."
npx hardhat compile
echo "✅ Smart contract compiled"
cd ..
echo ""

# Copy ABI
echo "Copying ABI to shared folder..."
cp contracts/artifacts/SessionManager.sol/SessionManager.json shared/SessionManager.abi.json
echo "✅ ABI copied"
echo ""

# Run tests
echo "Running encryption tests..."
python3.11 shared/encryption.py
echo ""

echo "Running system tests..."
python3.11 tests/test_system.py
echo ""

echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Deploy the smart contract:"
echo "   cd contracts"
echo "   cp .env.example .env"
echo "   # Edit .env with your private key"
echo "   npx hardhat run scripts/deploy.js --network polygon-mumbai"
echo ""
echo "2. Start the Administrator GUI:"
echo "   cd administrator"
echo "   python3.11 admin_gui.py"
echo ""
echo "3. Configure and start the Agent:"
echo "   cd agent"
echo "   # Edit agent_config.json with contract address and keys"
echo "   python3.11 agent.py --register --config agent_config.json"
echo "   python3.11 agent.py --session <session_id> --config agent_config.json"
echo ""
echo "See SETUP_GUIDE.md for detailed instructions."
echo ""

