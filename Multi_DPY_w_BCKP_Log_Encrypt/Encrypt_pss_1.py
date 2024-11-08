import os
from cryptography.fernet import Fernet

# Define the folder for storing encryption files
CRYPT_FOLDER = "../Crypt"

# Ensure the crypt folder exists
os.makedirs(CRYPT_FOLDER, exist_ok=True)

# Generate and save a key for encryption
def generate_key():
    key = Fernet.generate_key()
    key_path = os.path.join(CRYPT_FOLDER, "secret1.key")
    with open(key_path, "wb") as key_file:
        key_file.write(key)
    print(f"Encryption key saved at {key_path}")

# Encrypt and save a password
def encrypt_password(password):
    key_path = os.path.join(CRYPT_FOLDER, "secret1.key")
    with open(key_path, "rb") as key_file:
        key = key_file.read()
    fernet = Fernet(key)
    
    encrypted_password = fernet.encrypt(password.encode())
    enc_password_path = os.path.join(CRYPT_FOLDER, "encrypted_password1.txt")
    with open(enc_password_path, "wb") as enc_file:
        enc_file.write(encrypted_password)
    print(f"Encrypted password saved at {enc_password_path}")

# Run this function to generate the key and encrypt the password
generate_key()  # Run only once to create the key
encrypt_password("4gu4k4n_17")  # Replace with the actual password
