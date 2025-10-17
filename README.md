# Blockchain RAT - Remote Administration Tool

A decentralized remote administration tool that uses Polygon blockchain for command and control communication instead of traditional TCP/HTTP connections. **Built entirely in Python** for maximum compatibility and ease of deployment.

## 🚀 Features

- **Blockchain-based C2**: Commands and responses transmitted via Polygon blockchain transactions
- **Smart Contract Sessions**: Session management through Ethereum-compatible smart contracts
- **GUI Administrator Console**: PyQt5-based desktop application for managing agents
- **Python Agent**: Cross-platform agent supporting Windows, Linux, and macOS
- **End-to-End Encryption**: All communications encrypted with hybrid RSA+AES-256-GCM encryption
- **Low Cost**: Utilizes Polygon network for minimal transaction fees (~$0.001 per command)
- **Stealth Operation**: Traffic appears as normal blockchain activity
- **No Direct Connections**: No TCP/IP connections between admin and agent

## 🏗️ Architecture

The system consists of four main components:

1. **Smart Contract (Solidity)**: SessionManager contract deployed on Polygon
2. **Administrator Console (Python + PyQt5)**: GUI for sending commands and viewing responses
3. **Agent (Python)**: Runs on target machines, executes commands
4. **Shared Libraries (Python)**: Encryption and blockchain communication modules

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical documentation.

## 📁 Project Structure

```
blockchain_rat/
├── contracts/              # Smart contracts (Solidity)
│   ├── SessionManager.sol  # Main session management contract
│   ├── hardhat.config.js   # Hardhat configuration
│   └── scripts/            # Deployment scripts
├── administrator/          # Administrator GUI (Python + PyQt5)
│   └── admin_gui.py        # Main GUI application
├── agent/                  # Agent software (Python)
│   └── agent.py            # Agent main file
├── shared/                 # Shared libraries (Python)
│   ├── encryption.py       # Encryption utilities
│   ├── blockchain_client.py # Blockchain interaction
│   └── SessionManager.abi.json # Contract ABI
├── tests/                  # Test suites
│   └── test_system.py      # System tests
├── docs/                   # Documentation
├── ARCHITECTURE.md         # Technical architecture document
├── SETUP_GUIDE.md          # Detailed setup instructions
├── requirements.txt        # Python dependencies
└── quickstart.sh           # Quick setup script
```

## 🔧 Prerequisites

- **Python 3.11+** (recommended for all features)
- **Node.js 18+** and npm (for smart contract deployment)
- **Polygon wallet** with MATIC for gas fees
- **Polygon RPC endpoint** (Alchemy, Infura, or public RPC)

## ⚡ Quick Start

### 1. Clone and Setup

```bash
git clone <repository_url>
cd blockchain_rat
./quickstart.sh
```

### 2. Deploy Smart Contract

```bash
cd contracts
cp .env.example .env
# Edit .env with your private key
npx hardhat run scripts/deploy.js --network polygon-mumbai
```

**Save the contract address** from the output!

### 3. Start Administrator Console

```bash
cd administrator
python3.11 admin_gui.py
```

In the GUI:
- Enter RPC URL, contract address, and private key
- Click "Connect"

### 4. Setup Agent

```bash
cd agent
# Create config file
cat > agent_config.json << EOF
{
  "rpc_url": "https://rpc-mumbai.maticvigil.com",
  "contract_address": "YOUR_CONTRACT_ADDRESS",
  "private_key": "AGENT_WALLET_PRIVATE_KEY",
  "poll_interval": 10
}
EOF

# Register agent
python3.11 agent.py --register --config agent_config.json
```

### 5. Create Session and Connect

In the Administrator GUI:
1. Click "New Session"
2. Enter the agent's wallet address
3. Copy the session ID

On the agent machine:
```bash
python3.11 agent.py --session <SESSION_ID> --config agent_config.json
```

### 6. Send Commands

Use the GUI to send commands:
- **Quick Commands**: System Info, Screenshot, Ping
- **Custom Commands**: Execute shell commands, list directories, read files

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Comprehensive setup and usage guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture and design
- **[Smart Contract](contracts/SessionManager.sol)** - Session management contract
- **Inline Documentation** - See code comments for API details

## 🧪 Testing

### Run All Tests

```bash
# Encryption tests
python3.11 shared/encryption.py

# System tests
python3.11 tests/test_system.py

# Smart contract tests
cd contracts
npx hardhat test
```

### Test Results

```
✅ Encryption: PASS
✅ Blockchain Connection: PASS (requires config)
✅ Smart Contract Compilation: PASS
```

## 💰 Cost Estimates

Using Polygon Mumbai Testnet (similar costs on mainnet):

| Operation | Gas Cost | USD Equivalent |
|-----------|----------|----------------|
| Agent Registration | ~0.001 MATIC | ~$0.0001 |
| Session Creation | ~0.002 MATIC | ~$0.0002 |
| Send Message | ~0.001-0.003 MATIC | ~$0.0001-0.0003 |
| **100 Commands** | ~0.1-0.3 MATIC | ~$0.01-0.03 |

## 🛡️ Security Features

- **Hybrid Encryption**: RSA-2048 + AES-256-GCM
- **Data Compression**: Automatic gzip compression before encryption
- **Sequence Numbers**: Prevents replay attacks
- **Session Management**: Isolated sessions with unique IDs
- **Public Key Infrastructure**: Secure key exchange via blockchain

## 🎯 Use Cases

### Legitimate Applications

- Remote IT administration in restrictive networks
- Security research and penetration testing
- Disaster recovery and emergency access
- IoT device management
- Educational purposes and training

## ⚠️ Legal Disclaimer

**This tool is for authorized security research and system administration only.**

Unauthorized access to computer systems is **illegal** in most jurisdictions. Users must:

- ✅ Obtain explicit authorization before deployment
- ✅ Comply with all applicable laws and regulations
- ✅ Use the system only for lawful purposes
- ✅ Respect privacy and data protection requirements

The authors and contributors assume **no liability** for misuse of this software.

## 🔑 Key Technologies

- **Blockchain**: Polygon (Ethereum-compatible)
- **Smart Contracts**: Solidity 0.8.20
- **Backend**: Python 3.11
- **GUI**: PyQt5
- **Encryption**: cryptography, pycryptodome
- **Blockchain Client**: web3.py
- **Development**: Hardhat, ethers.js

## 📊 System Requirements

### Administrator Console

- Python 3.11+
- PyQt5
- 2GB RAM minimum
- Internet connection

### Agent

- Python 3.11+
- 512MB RAM minimum
- Internet connection (for blockchain RPC)

### Smart Contract

- Polygon network (Mumbai testnet or mainnet)
- Wallet with MATIC for gas fees

## 🚀 Advanced Features

### Multi-Agent Management

- Manage multiple agents simultaneously
- Switch between sessions in GUI
- Independent encryption keys per session

### Command Types

- **System Info**: OS, hostname, user details
- **Execute**: Run shell commands
- **Screenshot**: Capture screen
- **File Operations**: List directories, read files
- **Custom**: Extensible command framework

### Persistence Options

- Windows: Registry, Scheduled Tasks
- Linux: systemd, cron
- macOS: LaunchAgents

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

## 🆘 Support

For issues, questions, or contributions:

- Open an issue on GitHub
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for troubleshooting
- Check inline code documentation

## 🎉 Acknowledgments

Built with Python for maximum compatibility and ease of use. Powered by Polygon for low-cost, fast blockchain transactions.

---

**Version 1.0.0** | Built with ❤️ for security researchers and system administrators

