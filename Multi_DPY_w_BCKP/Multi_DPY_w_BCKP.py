import os
import time
import paramiko
from datetime import datetime

# Define FortiGate details as a list of dictionaries
fortigate_devices = [
    {
        "ip": "10.10.14.32",
        "username": "admin",
        "password": "4gu4k4n_17"
    },
    {
        "ip": "10.10.14.30",
        "username": "admin",
        "password": "4gu4k4n_17"
    }
    # Add more FortiGate devices as needed
]

def execute_commands(client, commands):
    """Execute a list of CLI commands on the FortiGate."""
    shell = client.invoke_shell()
    for cmd in commands:
        shell.send(cmd + "\n")
        time.sleep(1)  # Add delay to ensure command execution

    output = shell.recv(65535).decode()
    print(output)
    return "Command fail" not in output  # Return False if any command fails

def download_backup(client, device_ip, backup_stage):
    """Create and download the backup file from FortiGate."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    remote_backup_filename = f"backup_{backup_stage}_{timestamp}.conf"
    
    # Create a backup file on the FortiGate
    stdin, stdout, stderr = client.exec_command(f"execute backup config flash {remote_backup_filename}")
    error = stderr.read().decode().strip()
    
    if error:
        print(f"Failed to save backup on {device_ip}: {error}")
        return  # Exit if backup failed

    print(f"{backup_stage.capitalize()} backup saved as {remote_backup_filename} on {device_ip}")

    # Use SCP to copy the file from FortiGate to the local machine
    local_backup_path = f"{device_ip}_{backup_stage}_backup_{timestamp}.conf"
    scp_command = f"scp {device_ip}:/flash/{remote_backup_filename} {local_backup_path}"
    
    # Execute the SCP command
    os.system(f"sshpass -p {device['password']} {scp_command}")

    # Alternatively, you can use paramiko to handle SCP if you don't want to rely on sshpass
    # with paramiko's SFTP functionality
    # Uncomment below if you prefer using paramiko for SFTP download
    # sftp = client.open_sftp()
    # sftp.get(f"/flash/{remote_backup_filename}", local_backup_path)
    # sftp.close()

    print(f"{backup_stage.capitalize()} backup downloaded successfully for {device_ip} to {local_backup_path}")

def configure_fortigate(device):
    """Connect to FortiGate, perform pre- and post-backups, and run configuration commands."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Step 1: Pre-configuration backup
    download_backup(client, device["ip"], "pre")

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
        "set authpasswd T3lemetria.2025#",
        "set auto-negotiate enable",
        "set autokey-keepalive enable",
        "set keylife 3600",
        "next",
        "end"
    ]
    success_phase1 = execute_commands(client, commands_phase1)

    # Only proceed if phase 1 commands are successful
    if success_phase1:
        commands_phase2 = [
            "config vpn ipsec phase2-interface",
            "edit AGK-OCI-CARCAMO",
            "set phase1name AGK-OCI-CARCAMO",
            "set src-subnet 10.10.14.0/24",
            "set dst-subnet 10.70.0.0/24",
            "set proposal 3des-md5",
            "next",
            "end"
        ]
        success_phase2 = execute_commands(client, commands_phase2)

        # Commands for Static Route (Step 2)
        if success_phase2:
            commands_route = [
                "config router static",
                "edit 1",
                "set dst 10.70.0.0 255.255.255.0",
                "set device AGK-OCI-CARCAMO",
                "next",
                "end"
            ]
            success_route = execute_commands(client, commands_route)

            # Commands for Firewall Policies (Step 3)
            if success_route:
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
                success_policy1 = execute_commands(client, commands_policy1)

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
                success_policy2 = execute_commands(client, commands_policy2)

                # Step 2: Post-configuration backup only if all steps succeed
                if success_policy1 and success_policy2:
                    download_backup(client, device["ip"], "post")
                else:
                    print(f"Configuration failed at firewall policy stage for device {device['ip']}. No post-backup taken.")

            else:
                print(f"Configuration failed at static route stage for device {device['ip']}. No post-backup taken.")
        else:
            print(f"Configuration failed at phase 2 stage for device {device['ip']}. No post-backup taken.")
    else:
        print(f"Configuration failed at phase 1 stage for device {device['ip']}. No post-backup taken.")

    client.close()

if __name__ == "__main__":
    # Loop through each FortiGate device and apply the configuration
    for device in fortigate_devices:
        configure_fortigate(device)