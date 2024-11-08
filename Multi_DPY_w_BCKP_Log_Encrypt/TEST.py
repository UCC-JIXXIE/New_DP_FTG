import os
import time
import paramiko
import logging
from datetime import datetime
from cryptography.fernet import Fernet

# Set up logging
LOG_FILE = "fortigate_configuration.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# File paths
IP_LIST_FILE = "Segments/fortigate_ips.txt"
CRYPTO_FOLDER = "Crypt"
COMMANDS_FILE = "Commands/fortigate_commands.txt"
BACKUP_MAIN_FOLDER = "FTP_BCKP"

# Paths for encrypted FortiGate and FTP credentials
FORTIGATE_ENCRYPTED_PASSWORD_FILE = os.path.join(CRYPTO_FOLDER, "encrypted_password1.txt")
FORTIGATE_KEY_FILE = os.path.join(CRYPTO_FOLDER, "secret1.key")
FTP_ENCRYPTED_PASSWORD_FILE = os.path.join(CRYPTO_FOLDER, "encrypted_password2.txt")
FTP_KEY_FILE = os.path.join(CRYPTO_FOLDER, "secret2.key")

FTP_SERVER_IP = "10.10.14.50"
FTP_USERNAME = "filezilla_py"
USERNAME = "admin"

def decrypt_password(encrypted_password_file, key_file):
    """Decrypt password using the corresponding key."""
    try:
        with open(key_file, 'rb') as key_in, open(encrypted_password_file, 'rb') as enc_file:
            key = key_in.read()
            encrypted_password = enc_file.read()
        cipher = Fernet(key)
        password = cipher.decrypt(encrypted_password).decode()
        logging.info(f"Successfully decrypted password from {encrypted_password_file}")
        return password
    except Exception as e:
        logging.error(f"Failed to decrypt password: {e}")
        raise

# Load decrypted passwords
FORTIGATE_PASSWORD = decrypt_password(FORTIGATE_ENCRYPTED_PASSWORD_FILE, FORTIGATE_KEY_FILE)
FTP_PASSWORD = decrypt_password(FTP_ENCRYPTED_PASSWORD_FILE, FTP_KEY_FILE)

def execute_commands(client, commands):
    """Execute a list of CLI commands on the FortiGate."""
    try:
        shell = client.invoke_shell()
        for cmd in commands:
            shell.send(cmd + "\n")
            time.sleep(1)  # Add delay to ensure command execution
        output = shell.recv(65535).decode()
        logging.info("Commands executed successfully")
        print(output)
    except Exception as e:
        logging.error(f"Failed to execute commands: {e}")
        raise

def load_commands(file_path):
    """Load configuration commands from a .txt file."""
    try:
        with open(file_path, 'r') as file:
            commands = [line.strip() for line in file if line.strip()]
        logging.info(f"Loaded commands from {file_path}")
        return commands
    except FileNotFoundError:
        logging.error(f"Command file {file_path} not found.")
        raise
    except Exception as e:
        logging.error(f"Failed to load commands: {e}")
        raise

def create_backup(client, label, fortigate_ip):
    """Creates a backup with a given label ('pre' or 'post') and timestamp, organized in IP-based folders."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{label}_backup_{timestamp}.conf"
    
    device_folder_path = os.path.join(BACKUP_MAIN_FOLDER, fortigate_ip)
    os.makedirs(device_folder_path, exist_ok=True)
    
    # Full path for FTP backup command
    commands_backup = [
        f"execute backup config ftp {backup_filename} {FTP_SERVER_IP} {FTP_USERNAME} {FTP_PASSWORD}"
    ]
    try:
        execute_commands(client, commands_backup)
        logging.info(f"{label.capitalize()}-configuration backup saved as {os.path.join(device_folder_path, backup_filename)}")
    except Exception as e:
        logging.error(f"Failed to create {label} backup for {fortigate_ip}: {e}")
        raise

def configure_fortigate(fortigate_ip, commands):
    """Connect to FortiGate, create pre and post backups, and run configuration commands."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to FortiGate {fortigate_ip}")
        client.connect(fortigate_ip, username=USERNAME, password=FORTIGATE_PASSWORD)
        logging.info(f"Connected to FortiGate {fortigate_ip}")

        # Pre-configuration backup
        create_backup(client, "pre", fortigate_ip)

        # Execute configuration commands
        execute_commands(client, commands)

        # Post-configuration backup
        create_backup(client, "post", fortigate_ip)
        logging.info(f"VPN configuration for {fortigate_ip} completed successfully.")
    except paramiko.AuthenticationException:
        logging.error(f"Authentication failed for {fortigate_ip}")
    except Exception as e:
        logging.error(f"Failed to configure FortiGate {fortigate_ip}: {e}")
    finally:
        client.close()
        logging.info(f"Connection to {fortigate_ip} closed.")

if __name__ == "__main__":
    # Load IPs from text file
    try:
        with open(IP_LIST_FILE, 'r') as file:
            fortigate_ips = [line.strip() for line in file if line.strip()]
        logging.info("Loaded FortiGate IPs from file")
    except FileNotFoundError:
        logging.error(f"IP list file {IP_LIST_FILE} not found.")
        raise

    # Load configuration commands from .txt file
    configuration_commands = load_commands(COMMANDS_FILE)

    # Apply configuration to each FortiGate IP from the list
    for fortigate_ip in fortigate_ips:
        configure_fortigate(fortigate_ip, configuration_commands)
