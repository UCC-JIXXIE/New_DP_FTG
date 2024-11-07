import os
import time
import paramiko
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(filename='fortigate_config.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# FortiGate details
FORTIGATES = [
    {"ip": "10.10.14.32", "username": "admin", "password": "4gu4k4n_17"},
    {"ip": "10.10.14.30", "username": "admin", "password": "4gu4k4n_17"},
]

FTP_SERVER_IP = "10.10.14.50"
FTP_USERNAME = "filezilla_py"
FTP_PASSWORD = "Metro1998.2050"
BACKUP_MAIN_FOLDER = "FTP_BCKP"

def execute_commands(client, commands):
    """Execute a list of CLI commands on the FortiGate."""
    shell = client.invoke_shell()
    for cmd in commands:
        shell.send(cmd + "\n")
        time.sleep(1)  # Add delay to ensure command execution
        logging.info(f"Executed command: {cmd}")

    output = shell.recv(65535).decode()
    logging.info(f"Command output: {output}")
    print(output)

def create_backup(client, label, fortigate_ip):
    """Creates a backup with a given label ('pre' or 'post') and timestamp, organized in IP-based folders."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{label}_backup_{timestamp}.conf"
    
    # Create the backup directory structure
    device_folder_path = os.path.join(BACKUP_MAIN_FOLDER, fortigate_ip)
    os.makedirs(device_folder_path, exist_ok=True)
    
    # Full path for FTP backup command
    backup_path = os.path.join(device_folder_path, backup_filename)
    
    # Execute the FTP backup command
    commands_backup = [
        f"execute backup config ftp {backup_filename} {FTP_SERVER_IP} {FTP_USERNAME} {FTP_PASSWORD}"
    ]
    try:
        execute_commands(client, commands_backup)
        logging.info(f"{label.capitalize()}-configuration backup saved as {backup_path}")
    except Exception as e:
        logging.error(f"Failed to create {label} backup for {fortigate_ip}: {e}")

def configure_fortigate(fortigate):
    """Connect to FortiGate, create pre and post backups, and run configuration commands."""
    logging.info(f"Starting configuration for FortiGate {fortigate['ip']}")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(fortigate["ip"], username=fortigate["username"], password=fortigate["password"])

    # Pre-configuration backup
    create_backup(client, "pre", fortigate["ip"])

    # Commands for IPsec Tunnel (Step 1)
    commands_phase1 = [
        "config vpn ipsec phase1-interface",
        "edit AGK-OCI-CARCAMO",
        "set interface wwan",
        "set remote-gw 159.54.146.111",
        "set psksecret 1iAoDhcEAgk2025#",  # Static PSK
        "set proposal 3des-md5",
        "set xauthtype client",
        "set authusr CAC_LAKIN",
        "set authpasswd T3lemetria.2025#",  # Static Password
        "set auto-negotiate enable",
        "set autokey-keepalive enable",
        "set keylife 3600",
        "next",
        "end"
    ]
    execute_commands(client, commands_phase1)

    commands_phase2 = [
        "config vpn ipsec phase2-interface",
        "edit AGK-OCI-CARCAMO",
        "set phase1name AGK-OCI-CARCAMO",
        "set src-subnet 10.10.14.0/24",  # Local subnet
        "set dst-subnet 10.70.0.0/24",
        "set proposal 3des-md5",
        "next",
        "end"
    ]
    execute_commands(client, commands_phase2)

    # Commands for Static Route (Step 2)
    commands_route = [
        "config router static",
        "edit 1",
        "set dst 10.70.0.0 255.255.255.0",
        "set device AGK-OCI-CARCAMO",
        "next",
        "end"
    ]
    execute_commands(client, commands_route)

    # Commands for Firewall Policies (Step 3)
    commands_policy1 = [
        "config firewall policy",
        "edit 1",
        "set name AGK-OCI-CARCAMOS",
        "set srcintf AGK-OCI-CARCAMO",
        "set dstintf wwan",
        "set srcaddr all",
        "set dstaddr all",
        "set service ALL",
        "set nat disable",
        "set logtraffic all",
        "set schedule always",
        "set action accept",
        "next",
        "end"
    ]
    execute_commands(client, commands_policy1)

    commands_policy2 = [
        "config firewall policy",
        "edit 2",
        "set name LAN-AGK-OCI-CARCAMOS",
        "set srcintf wwan",
        "set dstintf AGK-OCI-CARCAMO",
        "set srcaddr all",
        "set dstaddr all",
        "set service ALL",
        "set nat disable",
        "set logtraffic all",
        "set schedule always",
        "set action accept",
        "next",
        "end"
    ]
    execute_commands(client, commands_policy2)

    # Post-configuration backup
    create_backup(client, "post", fortigate["ip"])

    client.close()
    logging.info(f"VPN configuration for {fortigate['ip']} completed successfully.")

if __name__ == "__main__":
    for fortigate in FORTIGATES:
        configure_fortigate(fortigate)
