#!/usr/bin/env python
import os
import threading
import smtplib
import time
from bit import Key
import subprocess
import base64
import argparse # Import the argparse module

# Add necessary modules for email with attachments
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Email configuration defaults (will be passed as arguments to functions)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

#SMTP_USER = 'your_email@gmail.com'          # REPLACE WITH YOUR GMAIL ADDRESS
#SMTP_PASSWORD = 'your_app_password'     # REPLACE WITH YOUR GMAIL APP PASSWORD
#RECIPIENT_EMAIL = 'your_recipient_email@example.com' # REPLACE WITH RECIPIENT EMAIL
#ENCRYPTION_PASSWORD = "YOUR_STRONG_ENCRYPTION_PASSWORD" # REPLACE THIS WITH YOUR ACTUAL PASSWORD, DO NOT SHARE!

# SMTP_USER, SMTP_PASSWORD, RECIPIENT_EMAIL, ENCRYPTION_PASSWORD
# will be passed as function arguments after being parsed from command line.

# File path
RICHES_FILE = "riches.txt"
FOUND_KEYS_FILE = "foundkey.txt"
ENCRYPTED_DATA_FILE = "/tmp/encrypted_key.enc" # Temporary file name for encrypted data
COUNT_FILE = "count.txt"

# global variable for testmail (controls a specific test key generation)
testmail = True

# --- HELPER FUNCTION TO RUN OPENSSL COMMANDS ---
def _run_openssl_command_simple(command_args, input_data):
    """
    Runs an openssl command and handles its output/errors.
    command_args: A list of arguments for the openssl command (e.g., ['enc', ...])
    input_data: Data (bytes) to be passed to openssl's stdin
    """
    full_command = ['openssl'] + command_args
    try:
        process = subprocess.run(
            full_command,
            input=input_data,
            capture_output=True,
            check=True # Raise CalledProcessError if the exit code is non-zero
        )
        return process.stdout.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print(f"Error calling openssl: Exit code {e.returncode}")
        print(f"Command executed: {' '.join(full_command)}")
        print(f"Stdout: {e.stdout.decode('utf-8').strip()}")
        print(f"Stderr: {e.stderr.decode('utf-8').strip()}")
        raise
    except FileNotFoundError:
        print("Error: 'openssl' command not found. Please ensure openssl is installed and in your PATH.")
        raise
    except Exception as e:
        print(f"System error running openssl: {e}")
        raise

# --- ENCRYPTION FUNCTION USING OPENSSL ---
def encrypt_message_openssl_simple(plaintext, password): # Password is now a parameter
    """
    Encrypts plaintext using AES-256-CBC via openssl CLI with simple default options.
    """
    command_args = ['enc', '-aes-256-cbc', '-a', '-k', password]
    return _run_openssl_command_simple(command_args, plaintext.encode('utf-8'))

# --- DECRYPTION FUNCTION (for the separate decrypt.py script, not used in this main script) ---
def decrypt_message_openssl_simple(ciphertext_b64, password):
    """
    Decrypts base64 encoded ciphertext using AES-256-CBC via openssl CLI with simple default options.
    """
    command_args = ['enc', '-d', '-aes-256-cbc', '-a', '-k', password]
    return _run_openssl_command_simple(command_args, ciphertext_b64.encode('utf-8'))
# --- END OF OPENSSL FUNCTIONS ---

def load_addresses(filepath):
    """Loads Bitcoin addresses from a file."""
    try:
        with open(filepath, 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        print(f"Error: Could not find file {filepath}")
        return set()

# This function now explicitly takes email configuration as arguments
def send_email_with_attachment(subject, body, filepath_to_attach, filename_in_email, smtp_user, smtp_password, recipient_email):
    """Sends an email with an attachment."""
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with open(filepath_to_attach, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {filename_in_email}")
        msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [recipient_email], msg.as_string())
            print(f"Email sent successfully via Gmail with attachment: {filename_in_email}.")
    except Exception as e:
        print(f"Error sending email with attachment via Gmail: {e}")

# check_address now receives all necessary email and encryption config as arguments
def check_address(addresses, lock, counter, smtp_user, smtp_password, recipient_email, encryption_password):
    """Verifies random Bitcoin addresses against a loaded list."""
    global testmail # testmail remains global as it's a shared state flag
    
    while True:
        key = Key() # Generate a new random Bitcoin key
        
        # Logic for using a specific test key (for debugging/testing purposes)
        if testmail:
            specific_test_wif = "Ky8rrHJDTkuiox8mfdKdKuXYV7VWFERX7zT25YZ4v8Asotx6XnMH" # A known WIF (test key)
            key = Key(specific_test_wif)
            print(f"DEBUG: Using test key: {specific_test_wif}")
            testmail = False # Reset flag so it only runs once per program execution
        
        address = key.address # Get the Bitcoin address for the generated key

        # Check if the generated address is in our list of riches addresses
        if address in addresses:
            with lock: # Use a lock to ensure thread-safe file writing and email sending
                # Append the found public address and private key to foundkey.txt
                with open(FOUND_KEYS_FILE, 'a') as f:
                    f.write(f"Public Address: {address}\n")
                    f.write(f"Private Key: {key.to_wif()}\n")
                
                # Prepare the sensitive content (Public Address and Private Key) for encryption
                content_to_encrypt = f"Public Address: {address}\nPrivate Key: {key.to_wif()}"
                
                # Encrypt the content using openssl, passing the encryption_password
                encrypted_data_b64 = encrypt_message_openssl_simple(content_to_encrypt, encryption_password)
                
                # Save the encrypted content to a temporary file for attachment
                try:
                    with open(ENCRYPTED_DATA_FILE, 'w') as f:
                        f.write(encrypted_data_b64)
                    print(f"Encrypted data saved to {ENCRYPTED_DATA_FILE}")
                except Exception as e:
                    print(f"Error saving encrypted data to file: {e}")
                    # Fallback: if file cannot be saved, print the encrypted data directly to console
                    print(f"Encrypted Data (Base64): {encrypted_data_b64}")

                # Send an email with the temporary encrypted file as an attachment
                email_subject = "Wow!! Matching Private Key Address Found! (Encrypted Attachment)"
                email_body = "The sensitive information is attached in an encrypted file. Use the shared password to decrypt it."
                # Call send_email_with_attachment, passing all required email parameters
                send_email_with_attachment(email_subject, email_body, ENCRYPTED_DATA_FILE, "found_key.enc", smtp_user, smtp_password, recipient_email)
                
                print(f"Matching address found: {address}")
                
                # Remove the temporary encrypted file to clean up sensitive data from disk
                try:
                    os.remove(ENCRYPTED_DATA_FILE)
                    print(f"Removed temporary encrypted file: {ENCRYPTED_DATA_FILE}")
                except OSError as e:
                    print(f"Error removing temporary file {ENCRYPTED_DATA_FILE}: {e}")

                #os._exit(0) # This exits all threads/processes immediately. Use with caution.
        
        # Update and print progress (thread-safe)
        with counter['lock']:
            counter['value'] += 1
            if counter['value'] % 100000 == 0:
                print(f"Thread {threading.current_thread().name}: Checked {counter['value']} addresses")
                # Append the current count to a file (optional, for persistent tracking)
                with open(COUNT_FILE, 'a') as f:
                    f.write(f"{counter['value']}\n")

if __name__ == "__main__":
    # --- Command-line argument parsing ---
    parser = argparse.ArgumentParser(description="Bitcoin Brute-Force Key Checker with Encrypted Email Notification.")
    parser.add_argument('--smtp_user', type=str, required=True,
                        help="Gmail address to send emails from (e.g., your_email@gmail.com).")
    parser.add_argument('--smtp_password', type=str, required=True,
                        help="Gmail App Password for the sending email account.")
    parser.add_argument('--recipient_email', type=str, required=True,
                        help="Email address to send alert notifications to.")
    parser.add_argument('--encryption_password', type=str, required=True,
                        help="Password used for encrypting sensitive key data in the attachment.")
    # Removed --num_threads as a command line arg to keep original behavior for it.
    
    args = parser.parse_args()

    # Assign parsed arguments to local variables in main
    smtp_user_arg = args.smtp_user
    smtp_password_arg = args.smtp_password
    recipient_email_arg = args.recipient_email
    encryption_password_arg = args.encryption_password

    addresses = load_addresses(RICHES_FILE)
    if not addresses:
        print(f"No addresses loaded from {RICHES_FILE}. Exiting.")
        exit(1)

    lock = threading.Lock()
    counter = {'value': 0, 'lock': threading.Lock()}
    threads = []
    # Original logic for num_threads
    num_threads = os.cpu_count()-0 or 4 # Use the number of CPU cores, or 4 if not determinable

    print(f"Starting check with {num_threads} threads...")

    for i in range(num_threads):
        thread = threading.Thread(
            target=check_address,
            # Pass all the necessary arguments to the check_address function
            args=(addresses, lock, counter, smtp_user_arg, smtp_password_arg, recipient_email_arg, encryption_password_arg),
            name=f"Thread-{i+1}"
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
