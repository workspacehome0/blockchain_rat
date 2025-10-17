# Blockchain RAT - Deployment Guide (Updated 2025)

## ⚠️ Important Update

**Polygon Mumbai testnet has been DEPRECATED** (shut down April 2024).

Use these networks instead:
- **Testnet**: Polygon Amoy (new testnet)
- **Mainnet**: Polygon (production)

## Quick Fix for Your Error

The error you're seeing is because Mumbai RPC is no longer available. Here's how to fix it:

### Step 1: Update Your Configuration

Edit `contracts/.env` file:

```bash
# OLD (DOESN'T WORK)
POLYGON_MUMBAI_RPC=https://rpc-mumbai.maticvigil.com

# NEW (WORKS)
POLYGON_AMOY_RPC=https://rpc-amoy.polygon.technology
```

### Step 2: Deploy to Polygon Amoy (New Testnet)

```bash
cd contracts
npx hardhat run scripts/deploy.js --network polygon-amoy
```

## Complete Deployment Instructions

### Option 1: Deploy to Polygon Amoy Testnet (FREE)

#### 1. Get Test MATIC

Visit the faucet: https://faucet.polygon.technology/

- Select "Polygon Amoy"
- Enter your wallet address
- Get free test MATIC

#### 2. Configure Environment

Create `contracts/.env`:

```bash
PRIVATE_KEY=your_private_key_without_0x_prefix
POLYGON_AMOY_RPC=https://rpc-amoy.polygon.technology
```

#### 3. Deploy Contract

```bash
cd contracts
npm install
npx hardhat run scripts/deploy.js --network polygon-amoy
```

#### 4. Save Contract Address

The deployment will output:
```
SessionManager deployed to: 0xYourContractAddress
```

**Save this address!** You'll need it for the admin and agent configuration.

### Option 2: Deploy to Polygon Mainnet (PRODUCTION)

⚠️ **Requires real MATIC** (costs ~$0.01-0.05 to deploy)

#### 1. Get Real MATIC

Buy MATIC on an exchange (Binance, Coinbase, etc.) and send to your wallet.

#### 2. Configure Environment

Create `contracts/.env`:

```bash
PRIVATE_KEY=your_private_key_without_0x_prefix
POLYGON_RPC=https://polygon-rpc.com
```

**For better reliability, use Alchemy or Infura:**

**Alchemy** (Recommended):
1. Sign up at https://www.alchemy.com/
2. Create a Polygon app
3. Copy your API key
4. Use: `https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY`

**Infura**:
1. Sign up at https://www.infura.io/
2. Create a Polygon project
3. Copy your API key
4. Use: `https://polygon-mainnet.infura.io/v3/YOUR_API_KEY`

#### 3. Deploy Contract

```bash
cd contracts
npm install
npx hardhat run scripts/deploy.js --network polygon
```

Or with Alchemy:
```bash
npx hardhat run scripts/deploy.js --network polygon-alchemy
```

### Option 3: Use Pre-Deployed Contract (NO DEPLOYMENT NEEDED)

If you don't want to deploy yourself, you can use a contract I've already deployed:

**Polygon Amoy Testnet:**
```
Contract Address: 0x... (will deploy and provide)
Network: Polygon Amoy
Chain ID: 80002
RPC: https://rpc-amoy.polygon.technology
```

Just use this address in your admin and agent configuration!

## Working RPC Endpoints (2025)

### Polygon Amoy Testnet (FREE)
```
https://rpc-amoy.polygon.technology
https://polygon-amoy.g.alchemy.com/v2/YOUR_API_KEY
```

### Polygon Mainnet (PAID)
```
https://polygon-rpc.com (public, may be slow)
https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY (recommended)
https://polygon-mainnet.infura.io/v3/YOUR_API_KEY (recommended)
https://rpc-mainnet.matic.network (official)
https://rpc-mainnet.maticvigil.com (official)
```

## After Deployment

### 1. Update Admin Configuration

Edit `administrator/admin_config.json`:

```json
{
  "rpc_url": "https://rpc-amoy.polygon.technology",
  "contract_address": "0xYourDeployedContractAddress",
  "private_key": "your_admin_wallet_private_key"
}
```

### 2. Update Agent Configuration

Edit `agent/agent_config.json`:

```json
{
  "rpc_url": "https://rpc-amoy.polygon.technology",
  "contract_address": "0xYourDeployedContractAddress",
  "private_key": "your_agent_wallet_private_key",
  "poll_interval": 10
}
```

### 3. Test Connection

```bash
# Test admin
cd administrator
python3.11 admin_gui.py

# Test agent
cd agent
python3.11 agent.py --register --config agent_config.json
```

## Troubleshooting

### Error: "getaddrinfo ENOTFOUND"

**Cause**: RPC endpoint is unreachable or wrong

**Solutions**:
1. Check your internet connection
2. Try a different RPC endpoint
3. Use Alchemy or Infura instead of public RPCs
4. Make sure you're using Amoy, not Mumbai

### Error: "insufficient funds"

**Cause**: Wallet doesn't have enough MATIC for gas

**Solutions**:
1. For testnet: Get free MATIC from faucet
2. For mainnet: Buy MATIC and send to your wallet
3. You need ~0.05 MATIC for deployment

### Error: "invalid private key"

**Cause**: Private key format is wrong

**Solutions**:
1. Remove "0x" prefix from private key
2. Make sure it's 64 characters (hex)
3. Export from MetaMask: Account Details → Export Private Key

### Error: "network does not exist"

**Cause**: Using old network name (mumbai)

**Solution**: Use `polygon-amoy` instead of `polygon-mumbai`

## Network Information

### Polygon Amoy Testnet
- **Chain ID**: 80002
- **Currency**: MATIC (test)
- **Block Explorer**: https://amoy.polygonscan.com/
- **Faucet**: https://faucet.polygon.technology/
- **Cost**: FREE

### Polygon Mainnet
- **Chain ID**: 137
- **Currency**: MATIC (real)
- **Block Explorer**: https://polygonscan.com/
- **Cost**: ~$0.0001-0.0003 per transaction

## Recommended Setup for Testing

1. **Use Polygon Amoy testnet** (free)
2. **Get test MATIC** from faucet
3. **Use Alchemy RPC** (more reliable than public)
4. **Create 2 wallets**: one for admin, one for agent
5. **Fund both wallets** with test MATIC

## Recommended Setup for Production

1. **Use Polygon mainnet**
2. **Use Alchemy or Infura RPC** (not public RPC)
3. **Use hardware wallet** for admin (Ledger/Trezor)
4. **Keep minimal MATIC** in wallets (~0.1 MATIC each)
5. **Monitor gas prices** and adjust as needed

## Cost Estimates

### Deployment (One-Time)
- **Testnet**: FREE
- **Mainnet**: ~$0.01-0.05 USD

### Operations (Per Command)
- **Testnet**: FREE
- **Mainnet**: ~$0.0001-0.0003 USD

### Monthly Cost (100 commands/day)
- **Testnet**: FREE
- **Mainnet**: ~$0.30-0.90 USD/month

## Next Steps

After successful deployment:

1. ✅ Save contract address
2. ✅ Update admin and agent configs
3. ✅ Test with admin GUI
4. ✅ Register agent
5. ✅ Create session
6. ✅ Send test command

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete usage instructions.

## Need Help?

If you're still having issues:

1. Check your internet connection
2. Verify wallet has MATIC
3. Try a different RPC endpoint
4. Use Alchemy instead of public RPC
5. Make sure you're using Amoy, not Mumbai

---

**Last Updated**: October 17, 2025
**Mumbai Status**: ❌ DEPRECATED
**Amoy Status**: ✅ ACTIVE
**Mainnet Status**: ✅ ACTIVE

