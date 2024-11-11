This project automates the configuration of FortiGate VPNs, creates backups, and maintains logs for each run. The primary script securely connects to specified FortiGate devices, configures VPN settings, and stores backups on an FTP server. This README provides an overview of the folder structure, required tools, and usage instructions.

Folder Structure

Multi_DPY_w_BCKP_Log_Encrypt: Main project folder containing the primary script.

Commands: Contains a text file with the commands to configure VPN settings on the FortiGate devices.

Crypt: Stores encrypted passwords for FortiGate and FTP access, along with scripts to generate these encrypted files.

FTP_Backup: Directory where backups are uploaded via FTP using FileZilla.

script_testing: Contains test versions of the main script for additional functionality or testing.

Segments: Holds a text file with the IP addresses of the FortiGate devices to be configured.

Logs: Directory where log files for each script run are saved.

Required Software

FileZilla: Used as an FTP server for backing up configuration files.

Visual Studio Code: For coding and executing the Python scripts.

GitHub: Used to manage versions and pull requests.

FortiGate 30E-3G4G-GBL: Tested on this FortiGate device model.

Requirements

Python 3.x

paramiko: For SSH connections.

cryptography: For encryption and decryption of credentials.

Install required packages using:

bash

Copy code

pip install paramiko cryptography

Configuration

FortiGate IP List: In the Segments folder, add a file named fortigate_ips.txt with the IPs of each FortiGate device to be configured, one per line.

Commands: Place the commands for VPN configuration in a text file inside the Commands folder. Ensure each command is on a new line.

Encrypted Passwords: Encrypt FortiGate and FTP passwords and save them in the Crypt folder. The encryption keys and generated encrypted files should match the file paths defined in the script.

Usage

Run the main script in the Multi_DPY_w_BCKP_Log_Encrypt folder.

Upon execution, the script:

Reads FortiGate IPs from the Segments folder.

Decrypts stored passwords from the Crypt folder.

Connects to each FortiGate device via SSH and applies the VPN configuration commands from the Commands folder.

Backs up the pre- and post-configuration states to the FTP_Backup folder.

Logs details of each run to the Logs folder.

Logging

Logs for each script execution are saved in the Logs folder, providing information on:


Successful or failed connections.

Command execution results.

Backup status.

Additional Information

Testing: The script has been tested on a FortiGate 30E-3G4G-GBL.

Code Versioning: Managed with GitHub, using pull requests for updates.

Troubleshooting

Connection Issues: Ensure correct IPs and encrypted credentials are provided.

File Permissions: Verify read/write permissions for backup and log folders.

FTP Configuration: Check that FileZilla FTP server details match those specified in the script.

