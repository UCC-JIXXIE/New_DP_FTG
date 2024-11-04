#THIS IS A TEST
import time
import paramiko

# Replace with FortiGate details

FORTIGATE_IP = "10.10.14.32"
USERNAME = "admin"
PASSWORD = "4gu4k4n_17"

def execute_commands(client, commands):
    """Execute a list of CLI commands on the FortiGate."""
    shell = client.invoke_shell()
    for cmd in commands:
        shell.send(cmd + "\n")
        time.sleep(1)  # Add delay to ensure command execution

    output = shell.recv(65535).decode()
    print(output)

def configure_fortigate():
    """Connect to FortiGate and run configuration commands."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(FORTIGATE_IP, username=USERNAME, password=PASSWORD)

    # Commands for IPsec Tunnel (Step 1)
    # Commands in this section might need to be adjusted just in the case the device is alredy running n' configured otherwhise leave default.
    commands_phase1 = [
        "config vpn ipsec phase1-interface",
        "edit AGK-OCI-CARCAMO",
        "set interface wwan",
        "set remote-gw 159.54.146.111",
        "set psksecret 1iAoDhcEAgk2025#", #Static PSKY
        "set proposal 3des-md5",
        "set xauthtype client",
        "set authusr CAC_LAKIN",  #User, depends of each Fortigate
        "set authpasswd T3lemetria.2025#", #Static Password
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
        "set src-subnet 10.10.14.0/24",  # Local subnet (variable)
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

    client.close()
    print("VPN configuration completed successfully.")

if __name__ == "__main__":
    configure_fortigate()
