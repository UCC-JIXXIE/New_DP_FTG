##MODIFY THE PARAMETERS OF THE CODE ACCORDINGLY TO EACH DEVICE, SOME MAY USE WAN INSTEAD OF WWAN##

Overview This Python script automates the configuration of an IPsec VPN and associated firewall policies on FortiGate devices. Using Paramiko for SSH connectivity, the script performs the following tasks in order:

Configures an IPsec VPN tunnel using custom Phase 1 and Phase 2 parameters. Adds a static route for the VPN network. Creates two firewall policies to manage traffic in and out of the VPN. This script is ideal for network administrators looking to quickly set up consistent VPN configurations across multiple FortiGate devices.

Prerequisites FortiGate Device Requirements FortiGate device(s) accessible via SSH. Appropriate credentials with administrative access. Software Requirements Python 3.x installed. paramiko library for SSH connectivity. SSH access to each FortiGate device. Installation Install Python if not already installed on your system.

Install paramiko with the following command:

bash Copy code pip install paramiko Clone or download this repository.

Configuration Before running the script, ensure the following parameters in the script are set according to your environment:

VPN Name: "AGK-OCI-CARCAMO" Phase 1 Parameters: Remote IP Address: Replace with the target IP address. Outgoing Interface: Usually wan or wwan. Preshared Key: Replace with the actual key. Encryption and Authentication: 3DES and MD5. XAUTH Type: Client. Credentials: Replace with your VPN username and password. Phase 2 Parameters: Local and Remote Addresses: Set local address per FortiGate, remote remains static. Encryption and Authentication: 3DES and MD5. Auto-negotiation: Enable. Key Lifetime: 3600 seconds. Script Execution To run the script, use the following command:

bash Copy code python Deploy_VPN_Fortigate.py The script will connect to the specified FortiGate device(s) and perform the configuration in the following order:

Step 1: Configure the IPsec VPN tunnel. Step 2: Add a static route. Step 3: Add firewall policies for traffic management. Example Commands VPN Configuration Commands (Step 1):

Configures IPsec Phase 1 and Phase 2 with custom settings. Static Route Commands (Step 2):

Adds a static route to the VPN with destination 10.70.0.0/255.255.255.0. Firewall Policy Commands (Step 3):

Adds two policies: Policy 1: AGK-OCI-CARCAMOS for outbound traffic. Policy 2: LAN-AGK-OCI-CARCAMOS for inbound traffic.

Troubleshooting Common Errors Return code -119: The schedule field is required for firewall policies. Ensure each policy includes set schedule always. Return code -160: A required field, such as action or schedule, may be missing. Return code -651: Incorrect value for set keepalive. Ensure it is set in Phase 1 with set keepalive enable. ModuleNotFoundError: No module named 'paramiko': Install Paramiko by running pip install paramiko. Tips Ensure SSH is enabled on each FortiGate device. Verify all parameters, especially IP addresses and interface names, to avoid command failures. Check the FortiGate firmware version as some commands may differ slightly between versions. 
License This project is licensed under the MIT License.
