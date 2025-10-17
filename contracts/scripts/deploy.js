const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Deploying SessionManager contract...");

  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);

  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(balance), "MATIC");

  const SessionManager = await hre.ethers.getContractFactory("SessionManager");
  const sessionManager = await SessionManager.deploy();

  await sessionManager.waitForDeployment();

  const address = await sessionManager.getAddress();
  console.log("SessionManager deployed to:", address);

  // Save deployment info
  const deploymentInfo = {
    network: hre.network.name,
    contractAddress: address,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString()
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

  console.log("\nDeployment complete!");
  console.log("Contract address:", address);
  console.log("Network:", hre.network.name);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

