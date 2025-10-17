const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Deploying SessionManager contract...");
  console.log("Network:", hre.network.name);

  // Check if private key is configured
  let deployer;
  try {
    const signers = await hre.ethers.getSigners();
    if (signers.length === 0) {
      throw new Error("No signers available");
    }
    deployer = signers[0];
    console.log("Deploying with account:", deployer.address);
  } catch (error) {
    console.error("\n❌ ERROR: Cannot get deployer account");
    console.error("\nPossible causes:");
    console.error("1. Missing .env file in contracts/ directory");
    console.error("2. PRIVATE_KEY not set in .env file");
    console.error("3. PRIVATE_KEY format is incorrect");
    console.error("\nHow to fix:");
    console.error("1. Create contracts/.env file");
    console.error("2. Add: PRIVATE_KEY=your_private_key_without_0x_prefix");
    console.error("3. Make sure private key is 64 hex characters");
    console.error("\nExample .env file:");
    console.error("PRIVATE_KEY=ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80");
    console.error("POLYGON_AMOY_RPC=https://rpc-amoy.polygon.technology");
    throw error;
  }

  // Check balance
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  const balanceInMatic = hre.ethers.formatEther(balance);
  console.log("Account balance:", balanceInMatic, "MATIC");

  if (parseFloat(balanceInMatic) < 0.01) {
    console.warn("\n⚠️  WARNING: Low balance!");
    console.warn("Your wallet has less than 0.01 MATIC");
    console.warn("Deployment may fail due to insufficient gas");
    console.warn("\nFor testnet: Get free MATIC from https://faucet.polygon.technology/");
    console.warn("For mainnet: Buy MATIC and send to your wallet");
  }

  // Deploy contract
  console.log("\nCompiling and deploying contract...");
  const SessionManager = await hre.ethers.getContractFactory("SessionManager");
  
  console.log("Sending deployment transaction...");
  const sessionManager = await SessionManager.deploy();

  console.log("Waiting for deployment confirmation...");
  await sessionManager.waitForDeployment();

  const address = await sessionManager.getAddress();
  console.log("\n✅ SessionManager deployed to:", address);

  // Save deployment info
  const network = await hre.ethers.provider.getNetwork();
  const deploymentInfo = {
    network: hre.network.name,
    contractAddress: address,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    chainId: network.chainId.toString(),
    blockNumber: await hre.ethers.provider.getBlockNumber()
  };

  const deploymentPath = path.join(__dirname, "..", "..", "deployment.json");
  fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
  console.log("Deployment info saved to:", deploymentPath);

  // Save ABI
  const artifactPath = path.join(__dirname, "..", "artifacts", "SessionManager.sol", "SessionManager.json");
  const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));
  const abiPath = path.join(__dirname, "..", "..", "shared", "SessionManager.abi.json");
  fs.writeFileSync(abiPath, JSON.stringify(artifact.abi, null, 2));
  console.log("ABI saved to:", abiPath);

  // Display summary
  console.log("\n" + "=".repeat(70));
  console.log("DEPLOYMENT SUCCESSFUL!");
  console.log("=".repeat(70));
  console.log("Contract Address:", address);
  console.log("Network:", hre.network.name);
  console.log("Chain ID:", network.chainId.toString());
  console.log("Deployer:", deployer.address);
  console.log("Block Number:", deploymentInfo.blockNumber);
  console.log("=".repeat(70));
  
  console.log("\n📋 Next Steps:");
  console.log("1. Copy the contract address above");
  console.log("2. Update administrator/admin_config.json with:");
  console.log("   - contract_address:", address);
  console.log("   - rpc_url: (your RPC endpoint)");
  console.log("3. Update agent/agent_config.json with the same info");
  console.log("4. Run the administrator GUI: python3.11 administrator/admin_gui.py");
  console.log("\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("\n❌ DEPLOYMENT FAILED");
    console.error("Error:", error.message);
    if (error.code) {
      console.error("Error code:", error.code);
    }
    process.exit(1);
  });

