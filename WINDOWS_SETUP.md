# Windows Setup Guide - Step by Step

## Your Error and How to Fix It

**Error**: `Cannot read properties of undefined (reading 'address')`

**Cause**: The `.env` file is missing or `PRIVATE_KEY` is not configured.

## Step-by-Step Fix (Windows)

### Step 1: Create .env File

Open Command Prompt or PowerShell in the `contracts` folder:

```cmd
cd C:\Users\Administrator\Downloads\blockchain_rat-main\blockchain_rat-main\contracts
```

Create the `.env` file:

```cmd
copy .env.example .env
```

### Step 2: Get Your Private Key

**From MetaMask:**
1. Open MetaMask
2. Click on the three dots (⋮) next to your account
3. Click "Account Details"
4. Click "Export Private Key"
5. Enter your password
6. Copy the private key (64 characters, like: `ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`)

⚠️ **IMPORTANT**: Remove the `0x` prefix if it has one!

### Step 3: Edit .env File

Open `.env` with Notepad:

```cmd
notepad .env
```

Add your configuration:

```
PRIVATE_KEY=your_64_character_private_key_here_without_0x
POLYGON_AMOY_RPC=https://rpc-amoy.polygon.technology
```

**Example** (don't use this key, it's just an example):
```
PRIVATE_KEY=ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
POLYGON_AMOY_RPC=https://rpc-amoy.polygon.technology
```

Save and close Notepad.

### Step 4: Get Test MATIC

Your wallet needs MATIC for gas fees.

**For Testnet (FREE):**
1. Go to: https://faucet.polygon.technology/
2. Select "Polygon Amoy"
3. Paste your wallet address
4. Click "Submit"
5. Wait 1-2 minutes for MATIC to arrive

**Check your balance:**
- Open MetaMask
- Switch network to "Polygon Amoy" (you may need to add it manually)
- You should see ~0.5 MATIC

### Step 5: Add Polygon Amoy to MetaMask (if not added)

1. Open MetaMask
2. Click network dropdown
3. Click "Add Network"
4. Click "Add a network manually"
5. Enter:
   - **Network Name**: Polygon Amoy Testnet
   - **RPC URL**: https://rpc-amoy.polygon.technology
   - **Chain ID**: 80002
   - **Currency Symbol**: MATIC
   - **Block Explorer**: https://amoy.polygonscan.com/
6. Click "Save"

### Step 6: Deploy Contract

Now run the deployment:

```cmd
npx hardhat run scripts/deploy.js --network polygon-amoy
```

You should see:

```
Deploying SessionManager contract...
Network: polygon-amoy
Deploying with account: 0xYourAddress
Account balance: 0.5 MATIC

Compiling and deploying contract...
Sending deployment transaction...
Waiting for deployment confirmation...

✅ SessionManager deployed to: 0xYourContractAddress
```

### Step 7: Save Contract Address

Copy the contract address from the output. You'll need it!

## Common Errors and Fixes

### Error: "Cannot read properties of undefined"

**Fix**: Your `.env` file is missing or `PRIVATE_KEY` is not set.

**Check**:
```cmd
type .env
```

You should see your private key. If not, go back to Step 3.

### Error: "insufficient funds"

**Fix**: Your wallet doesn't have MATIC.

**Solution**: Get test MATIC from faucet (Step 4)

### Error: "invalid private key"

**Fix**: Private key format is wrong.

**Check**:
- Must be 64 hex characters
- No `0x` prefix
- No spaces or quotes

**Correct**: `ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`
**Wrong**: `0xac0974...` (has 0x)
**Wrong**: `"ac0974..."` (has quotes)
**Wrong**: `ac0974 bec39a...` (has space)

### Error: "network does not exist: polygon-amoy"

**Fix**: You need to update `hardhat.config.js`.

**Solution**: Download the latest version from GitHub or manually add:

```javascript
"polygon-amoy": {
  url: "https://rpc-amoy.polygon.technology",
  accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
  chainId: 80002
}
```

## Quick Checklist

Before running deployment, verify:

- [ ] `.env` file exists in `contracts` folder
- [ ] `PRIVATE_KEY` is set in `.env` (64 hex characters, no 0x)
- [ ] `POLYGON_AMOY_RPC` is set in `.env`
- [ ] Wallet has test MATIC (check MetaMask)
- [ ] MetaMask is on Polygon Amoy network
- [ ] `npm install` was run in contracts folder

## Full Command Sequence (Copy-Paste)

```cmd
cd C:\Users\Administrator\Downloads\blockchain_rat-main\blockchain_rat-main\contracts

rem Create .env file
copy .env.example .env

rem Edit .env with Notepad (add your private key)
notepad .env

rem Install dependencies (if not done)
npm install

rem Deploy to Polygon Amoy testnet
npx hardhat run scripts/deploy.js --network polygon-amoy
```

## After Successful Deployment

### 1. Update Admin Config

Create `administrator/admin_config.json`:

```json
{
  "rpc_url": "https://rpc-amoy.polygon.technology",
  "contract_address": "0xYourContractAddressFromDeployment",
  "private_key": "your_admin_wallet_private_key"
}
```

### 2. Update Agent Config

Create `agent/agent_config.json`:

```json
{
  "rpc_url": "https://rpc-amoy.polygon.technology",
  "contract_address": "0xYourContractAddressFromDeployment",
  "private_key": "your_agent_wallet_private_key",
  "poll_interval": 10
}
```

⚠️ **Use different wallets for admin and agent!**

### 3. Run Admin GUI

```cmd
cd ..\administrator
python admin_gui.py
```

### 4. Register Agent

```cmd
cd ..\agent
python agent.py --register --config agent_config.json
```

## Alternative: Use Polygon Mainnet (Real Money)

If you want to use real Polygon network instead of testnet:

**Step 1**: Buy real MATIC (~$0.10 worth)

**Step 2**: Edit `.env`:
```
PRIVATE_KEY=your_private_key
POLYGON_RPC=https://polygon-rpc.com
```

**Step 3**: Deploy to mainnet:
```cmd
npx hardhat run scripts/deploy.js --network polygon
```

**Cost**: ~$0.01-0.05 for deployment

## Still Having Issues?

### Check .env file exists:
```cmd
dir .env
```

### Check .env file content:
```cmd
type .env
```

### Check npm packages installed:
```cmd
dir node_modules
```

### Reinstall packages:
```cmd
rmdir /s /q node_modules
npm install
```

### Test connection:
```cmd
npx hardhat console --network polygon-amoy
```

## Need Help?

If you're still stuck, provide:
1. The exact error message
2. Output of `type .env` (hide your private key!)
3. Output of `npm --version` and `node --version`
4. Your MetaMask wallet address
5. Your MetaMask network (should be Polygon Amoy)

---

**Last Updated**: October 17, 2025
**Platform**: Windows 10/11
**Tested**: ✅ Working

