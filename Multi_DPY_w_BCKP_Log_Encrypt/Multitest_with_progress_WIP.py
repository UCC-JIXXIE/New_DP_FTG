

import os
import time
import paramiko
import logging
from datetime import datetime
from cryptography.fernet import Fernet
import sys

# Set up logging
LOG_FILE = f"fortigate_configuration_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Redirect stdout and stderr to the logging system
class StreamToLogger:
    def __init__(self, log_level):
        self.log_level = log_level

    def write(self, message):
        if message.strip():
            self.log_level(message.strip())

    def flush(self):
        pass

sys.stdout = StreamToLogger(logging.info)
sys.stderr = StreamToLogger(logging.error)

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

FTP_SERVER_IP = "10.10.20.50"
FTP_USERNAME = "filezilla_py"
USERNAME = "admin"

def decrypt_password(encrypted_password_file, key_file):
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

FORTIGATE_PASSWORD = decrypt_password(FORTIGATE_ENCRYPTED_PASSWORD_FILE, FORTIGATE_KEY_FILE)
FTP_PASSWORD = decrypt_password(FTP_ENCRYPTED_PASSWORD_FILE, FTP_KEY_FILE)

def execute_commands(client, commands):
    try:
        shell = client.invoke_shell()
        for cmd in commands:
            logging.info(f"Executing command: {cmd}")
            shell.send(cmd + "\n")
            print(f"Executed: {cmd}")
        output = shell.recv(65535).decode()
        logging.info("Commands executed successfully")
        print("Command execution complete.")
    except Exception as e:
        logging.error(f"Failed to execute commands: {e}")
        raise

def load_commands(file_path):
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{label}_backup_{timestamp}.conf"
    device_folder_path = os.path.join(BACKUP_MAIN_FOLDER, fortigate_ip)
    os.makedirs(device_folder_path, exist_ok=True)
    
    commands_backup = [
        f"execute backup config ftp {backup_filename} {FTP_SERVER_IP} {FTP_USERNAME} {FTP_PASSWORD}"
    ]
    try:
        logging.info(f"Creating {label} backup for {fortigate_ip}.")
        print(f"Creating {label} backup for {fortigate_ip}.")
        execute_commands(client, commands_backup)
        logging.info(f"{label.capitalize()}-backup saved as {os.path.join(device_folder_path, backup_filename)}")
        print(f"{label.capitalize()}-backup completed.")
    except Exception as e:
        logging.error(f"Failed to create {label} backup for {fortigate_ip}: {e}")
        raise

def configure_fortigate(fortigate_ip, commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to FortiGate {fortigate_ip}")
        print(f"Connecting to FortiGate {fortigate_ip}...")
        client.connect(fortigate_ip, username=USERNAME, password=FORTIGATE_PASSWORD)
        logging.info(f"Connected to FortiGate {fortigate_ip}")
        print("Connected successfully.")

        create_backup(client, "pre", fortigate_ip)

        print("Executing configuration commands...")
        execute_commands(client, commands)

        create_backup(client, "post", fortigate_ip)

        logging.info(f"Configuration for {fortigate_ip} completed successfully.")
        print(f"Configuration for {fortigate_ip} completed.")
    except paramiko.AuthenticationException:
        logging.error(f"Authentication failed for {fortigate_ip}")
        print(f"Authentication failed for {fortigate_ip}.")
    except Exception as e:
        logging.error(f"Failed to configure FortiGate {fortigate_ip}: {e}")
        print(f"Failed to configure FortiGate {fortigate_ip}.")
    finally:
        client.close()
        logging.info(f"Connection to {fortigate_ip} closed.")
        print(f"Connection to {fortigate_ip} closed.")

if __name__ == "__main__":
    try:
        with open(IP_LIST_FILE, 'r') as file:
            fortigate_ips = [line.strip() for line in file if line.strip()]
        logging.info("Loaded FortiGate IPs from file")
        print("FortiGate IPs loaded successfully.")
    except FileNotFoundError:
        logging.error(f"IP list file {IP_LIST_FILE} not found.")
        print(f"IP list file {IP_LIST_FILE} not found.")
        raise

    configuration_commands = load_commands(COMMANDS_FILE)

    for fortigate_ip in fortigate_ips:
        configure_fortigate(fortigate_ip, configuration_commands)
