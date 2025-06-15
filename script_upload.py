#!/usr/bin/env python
import os
import threading
import smtplib
import time
from bit import Key

# Required for subprocess calls to openssl
import subprocess
import base64 # Used for base64 encoding/decoding the final output

# Add necessary modules for email with attachments
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Email configuration (keep sensitive information confidential)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'your_email@gmail.com'          # REPLACE WITH YOUR GMAIL ADDRESS
SMTP_PASSWORD = 'your_app_password'     # REPLACE WITH YOUR GMAIL APP PASSWORD
RECIPIENT_EMAIL = 'your_recipient_email@example.com' # REPLACE WITH RECIPIENT EMAIL

ENCRYPTION_PASSWORD = "YOUR_STRONG_ENCRYPTION_PASSWORD" # REPLACE THIS WITH YOUR ACTUAL PASSWORD, DO NOT SHARE!

# File path
RICHES_FILE = "riches.txt"
FOUND_KEYS_FILE = "foundkey.txt"
ENCRYPTED_DATA_FILE = "/tmp/encrypted_key.enc" # Temporary file name for encrypted data
COUNT_FILE = "count.txt"

# global variable testmail
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

# --- SIMPLIFIED ENCRYPTION/DECRYPTION FUNCTIONS USING OPENSSL ---
def encrypt_message_openssl_simple(plaintext, password):
    """
    Encrypts plaintext using AES-256-CBC via openssl CLI with simple default options.
    """
    # -aes-256-cbc: AES 256-bit CBC mode.
    # -a: base64 encode output (makes it email-friendly).
    # -k: password (openssl will automatically use it to derive key and salt).
    # openssl will automatically add salt to the output, which is more secure.
    command_args = ['enc', '-aes-256-cbc', '-a', '-k', password]
    return _run_openssl_command_simple(command_args, plaintext.encode('utf-8'))

def decrypt_message_openssl_simple(ciphertext_b64, password):
    """
    Decrypts base64 encoded ciphertext using AES-256-CBC via openssl CLI with simple default options.
    """
    # -d: decrypt.
    # -aes-256-cbc: AES 256-bit CBC mode.
    # -a: base64 decode input.
    # -k: password.
    command_args = ['enc', '-d', '-aes-256-cbc', '-a', '-k', password]
    return _run_openssl_command_simple(command_args, ciphertext_b64.encode('utf-8'))
# --- END OF SIMPLIFIED ENCRYPTION/DECRYPTION FUNCTIONS ---

def load_addresses(filepath):
    """Import Bitcoin addresses from a file."""
    try:
        with open(filepath, 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        print(f"Error: Could not find file {filepath}")
        return set()

def send_email(subject, message):
    """Send alert email."""
    try:
        # Encrypt the message content before sending
        encrypted_message = encrypt_message_openssl_simple(message, ENCRYPTION_PASSWORD)
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            #msg = f"Subject: {subject}\n\n{message}"
            #server.sendmail(SMTP_USER, RECIPIENT_EMAIL, msg)
            from_header = f"From: {SMTP_USER}"
            to_header = f"To: {RECIPIENT_EMAIL}"
            subject_header = f"Subject: {subject}"
            full_msg = f"{from_header}\n{to_header}\n{subject_header}\n\n{encrypted_message}"
            server.sendmail(SMTP_USER, [RECIPIENT_EMAIL], full_msg)
            print("Email sent.")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_email_with_attachment(subject, body, filepath_to_attach, filename_in_email):
    """Sends an email with an attachment."""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Attach the file
        attachment = open(filepath_to_attach, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {filename_in_email}")
        msg.attach(part)
        attachment.close()

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [RECIPIENT_EMAIL], msg.as_string())
            print(f"Email sent successfully via Gmail with attachment: {filename_in_email}.")
    except Exception as e:
        print(f"Error sending email with attachment via Gmail: {e}")

def check_address(addresses, lock, counter):
    """Verify random addresses with a loaded list."""
    global testmail
    while True:
        key = Key()
        if testmail:
            specific_test_wif = "Ky8rrHJDTkuiox8mfdKdKuXYV7VWFERX7zT25YZ4v8Asotx6XnMH"
            key = Key(specific_test_wif)
            print(f"DEBUG: Using test key: {specific_test_wif}")
            testmail = False
        address = key.address

        if address in addresses:
            with lock:
                with open(FOUND_KEYS_FILE, 'a') as f:
                    f.write(f"Public Address: {address}\n")
                    f.write(f"Private Key: {key.to_wif()}\n")
                
                # Prepare content for encryption
                content_to_encrypt = f"Public Address: {address}\nPrivate Key: {key.to_wif()}"
                
                # Encrypt the content
                encrypted_data_b64 = encrypt_message_openssl_simple(content_to_encrypt, ENCRYPTION_PASSWORD)
                
                # Save the encrypted content to a temporary file
                try:
                    with open(ENCRYPTED_DATA_FILE, 'w') as f:
                        f.write(encrypted_data_b64)
                    print(f"Encrypted data saved to {ENCRYPTED_DATA_FILE}")
                except Exception as e:
                    print(f"Error saving encrypted data to file: {e}")
                    # If file cannot be saved, at least print it for user visibility
                    print(f"Encrypted Data (Base64): {encrypted_data_b64}")

                # Send email with the attached file
                email_subject = "Wow!! Matching Private Key Address Found! (Encrypted Attachment)"
                email_body = "The sensitive information is attached in an encrypted file. Use the shared password to decrypt it."
                send_email_with_attachment(email_subject, email_body, ENCRYPTED_DATA_FILE, "found_key.enc")
                
                print(f"Matching address found: {address}")
                
                # Remove the temporary file after sending the email
                try:
                    os.remove(ENCRYPTED_DATA_FILE)
                    print(f"Removed temporary encrypted file: {ENCRYPTED_DATA_FILE}")
                except OSError as e:
                    print(f"Error removing temporary file {ENCRYPTED_DATA_FILE}: {e}")

                #os._exit(0) # Exit the program after finding and sending email
        """
        if address in addresses:
            with lock:
                with open(FOUND_KEYS_FILE, 'a') as f:
                    f.write(f"Public Adress: {address}\n")
                    f.write(f"Private Key: {key.to_wif()}\n")
                print(f"Matching Bitcoin address found: {address}")
                send_email("Wow!! Matching Private Key address found!", f"Public Adress: {address}\nPrivate Key: {key.to_wif()}")
                # Stop all threads after finding a match
                #os._exit(0)  # Exit immediately
        """
        # Print progress every 100,000 iterations
        with counter['lock']:
            counter['value'] += 1
            if counter['value'] % 100000 == 0:
                print(f"Thread {threading.current_thread().name}: Checked {counter['value']} addresses")
                with open(COUNT_FILE, 'a') as f:
                    f.write(f"{counter['value']}\n")

if __name__ == "__main__":
    addresses = load_addresses(RICHES_FILE)
    if not addresses:
        exit()

    lock = threading.Lock()
    counter = {'value': 0, 'lock': threading.Lock()}
    threads = []
    num_threads = os.cpu_count()-0 or 4  # Use the number of CPU cores, or 4 if not determinable

    print(f"Starting check with {num_threads} threads...")

    for i in range(num_threads):
        thread = threading.Thread(target=check_address, args=(addresses, lock, counter), name=f"Thread-{i+1}")
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()