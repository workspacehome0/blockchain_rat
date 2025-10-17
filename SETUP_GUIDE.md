# Blockchain RAT - Setup and Usage Guide

## Overview

This guide will walk you through setting up and using the Blockchain-based Remote Administration Tool (RAT) on the Polygon network.

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.11+** installed
2. **Node.js 18+** and npm/pnpm installed
3. **Two Polygon wallets** with some MATIC for gas fees:
   - One for the Administrator
   - One for the Agent
4. **Polygon RPC endpoint** (free options):
   - Alchemy: https://www.alchemy.com/
   - Infura: https://www.infura.io/
   - Public RPC: https://rpc-mumbai.maticvigil.com (testnet)

## Step 1: Install Dependencies

### Python Dependencies

```bash
cd blockchain_rat
pip3 install -r requirements.txt
```

### Smart Contract Dependencies

```bash
cd contracts
npm install
```

## Step 2: Deploy Smart Contract

### Configure Deployment

1. Create `.env` file in the `contracts` directory:

```bash
cd contracts
cp .env.example .env
```

2. Edit `.env` and add your deployment wallet private key:

```
PRIVATE_KEY=your_private_key_here_without_0x_prefix
POLYGON_MUMBAI_RPC=https://rpc-mumbai.maticvigil.com
```

### Compile Contract

```bash
npx hardhat compile
```

### Deploy to Polygon Mumbai Testnet

```bash
npx hardhat run scripts/deploy.js --network polygon-mumbai
```

**Save the contract address** from the output. You'll need it for configuration.

### Deploy to Polygon Mainnet (Production)

```bash
npx hardhat run scripts/deploy.js --network polygon
```

## Step 3: Configure Administrator Console

1. The first time you run the GUI, you'll need to enter:
   - **RPC URL**: Your Polygon RPC endpoint
   - **Contract Address**: The deployed SessionManager contract address
   - **Private Key**: Your administrator wallet private key

2. These settings will be saved in `administrator/admin_config.json`

## Step 4: Configure Agent

1. Create agent configuration file:

```bash
cd agent
cp ../tests/test_config.json agent_config.json
```

2. Edit `agent_config.json`:

```json
{
  "rpc_url": "https://rpc-mumbai.maticvigil.com",
  "contract_address": "0xYourContractAddress",
  "private_key": "agent_wallet_private_key",
  "poll_interval": 10
}
```

## Step 5: Run the System

### Start Administrator Console

```bash
cd administrator
python3.11 admin_gui.py
```

The GUI will open. Follow these steps:

1. **Connect to Blockchain**:
   - Enter your RPC URL, contract address, and private key
   - Click "Connect"
   - Wait for confirmation

2. **Register Agent**:
   - On the agent machine, run:
   ```bash
   cd agent
   python3.11 agent.py --register --config agent_config.json
   ```
   - Copy the agent's wallet address

3. **Create Session**:
   - In the admin GUI, click "New Session"
   - Enter the agent's wallet address
   - Session will be created

4. **Start Agent**:
   - On the agent machine, run:
   ```bash
   python3.11 agent.py --session <session_id> --config agent_config.json
   ```
   - Replace `<session_id>` with the session ID from step 3

5. **Send Commands**:
   - Select the session in the GUI
   - Use quick commands (System Info, Screenshot, Ping) or
   - Create custom commands with JSON data
   - Click "Send Command"
   - Responses will appear in the response area

## Available Commands

### Quick Commands

- **System Info**: Get system information (OS, hostname, user, etc.)
- **Screenshot**: Capture screen (saved as PNG)
- **Ping**: Check if agent is alive

### Custom Commands

#### Execute Shell Command

```json
{
  "type": "execute",
  "command": "whoami"
}
```

#### List Directory

```json
{
  "type": "list_dir",
  "path": "/home"
}
```

#### Read File

```json
{
  "type": "read_file",
  "filepath": "/etc/hostname"
}
```

## Security Best Practices

### For Administrators

1. **Use dedicated wallets** with minimal funds for RAT operations
2. **Rotate session keys** regularly
3. **Use VPN or Tor** when accessing the admin console
4. **Store private keys securely** (hardware wallet recommended)
5. **Monitor gas costs** to avoid unexpected expenses

### For Agents

1. **Implement kill switches** for emergency termination
2. **Use privacy-focused RPC endpoints** or run your own node
3. **Randomize polling intervals** to avoid pattern detection
4. **Secure agent configuration files** with appropriate permissions

## Cost Optimization

### Reducing Transaction Costs

1. **Use Polygon over Ethereum**: Polygon fees are 1000x cheaper
2. **Compress commands**: The system automatically compresses data
3. **Batch operations**: Send multiple commands in sequence
4. **Monitor gas prices**: Send transactions during low-traffic periods

### Estimated Costs (Polygon Mumbai Testnet)

- **Agent Registration**: ~0.001 MATIC
- **Session Creation**: ~0.002 MATIC
- **Send Message**: ~0.001-0.003 MATIC (depends on payload size)
- **Total for 100 commands**: ~0.1-0.3 MATIC (~$0.01-0.03 USD)

## Troubleshooting

### Connection Issues

**Problem**: "Failed to connect to blockchain"

**Solutions**:
- Check RPC endpoint is accessible
- Verify private key format (no 0x prefix in .env)
- Ensure wallet has MATIC for gas fees
- Try alternative RPC endpoint

### Agent Not Responding

**Problem**: Agent doesn't execute commands

**Solutions**:
- Check agent is running and polling
- Verify session ID is correct
- Ensure agent has MATIC for response transactions
- Check agent logs for errors

### Transaction Failures

**Problem**: Transactions fail or revert

**Solutions**:
- Increase gas limit in blockchain_client.py
- Check wallet has sufficient MATIC
- Verify contract address is correct
- Check sequence numbers are in order

### GUI Issues

**Problem**: GUI doesn't display properly

**Solutions**:
- Install PyQt5 dependencies: `pip3 install PyQt5`
- On Linux, install: `sudo apt-get install python3-pyqt5`
- Check Python version is 3.11+

## Testing

### Run Encryption Tests

```bash
python3.11 shared/encryption.py
```

### Run System Tests

```bash
python3.11 tests/test_system.py
```

### Test Smart Contract

```bash
cd contracts
npx hardhat test
```

## Production Deployment

### For Production Use

1. **Deploy to Polygon Mainnet**:
   ```bash
   npx hardhat run scripts/deploy.js --network polygon
   ```

2. **Use Production RPC**:
   - Alchemy: `https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY`
   - Infura: `https://polygon-mainnet.infura.io/v3/YOUR_KEY`

3. **Secure Configuration**:
   - Use environment variables for sensitive data
   - Encrypt configuration files
   - Implement access controls

4. **Monitor Operations**:
   - Track transaction costs
   - Monitor session activity
   - Log all commands and responses

## Advanced Features

### Multi-Agent Management

The system supports managing multiple agents simultaneously:

1. Register multiple agents
2. Create sessions for each agent
3. Switch between sessions in the GUI
4. Send commands to specific agents

### File Transfer

For large file transfers:

1. Use IPFS or Arweave for storage
2. Send file hash via blockchain
3. Agent downloads from decentralized storage
4. Verify integrity with hash

### Persistence

Agent persistence mechanisms:

- **Windows**: Registry Run keys, Scheduled Tasks
- **Linux**: systemd services, cron jobs
- **macOS**: LaunchAgents, LaunchDaemons

## Legal and Ethical Considerations

⚠️ **IMPORTANT WARNING**

This tool is designed for:
- **Authorized system administration**
- **Security research and testing**
- **Educational purposes**

**Unauthorized access to computer systems is illegal.** Users must:

- Obtain explicit authorization before deployment
- Comply with all applicable laws and regulations
- Use the system only for lawful purposes
- Respect privacy and data protection requirements

## Support and Documentation

- **Architecture Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Smart Contract**: See [contracts/SessionManager.sol](contracts/SessionManager.sol)
- **API Reference**: See inline code documentation

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Changelog

### Version 1.0.0 (Current)

- Initial release
- Polygon blockchain support
- PyQt5 GUI administrator console
- Python agent with command execution
- Hybrid encryption (RSA + AES-256-GCM)
- Smart contract session management
- Multi-platform support (Windows, Linux, macOS)

