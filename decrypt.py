import subprocess
import os

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

# --- DECRYPTION FUNCTION USING OPENSSL ---
def decrypt_message_openssl_simple(ciphertext_b64, password):
    """
    Decrypts base64 encoded ciphertext using AES-256-CBC via openssl CLI.
    """
    # -d: decrypt.
    # -aes-256-cbc: AES 256-bit CBC mode.
    # -a: base64 decode input.
    # -k: password (openssl will use this to derive key/IV, using the salt embedded in ciphertext).
    command_args = ['enc', '-d', '-aes-256-cbc', '-a', '-k', password]
    
    # Input data should be the base64 encoded string itself, as openssl will decode it.
    return _run_openssl_command_simple(command_args, ciphertext_b64.encode('utf-8'))

# --- MAIN SCRIPT FOR FILE DECRYPTION ---
if __name__ == "__main__":
    print("Starting decryption of encrypted file content using openssl...")

    # Get the file path from user input
    ENCRYPTED_FILE_PATH = input("Enter the path to the encrypted file (e.g., /path/to/found_key.enc): ")

    # Check if the file exists
    if not os.path.exists(ENCRYPTED_FILE_PATH):
        print(f"Error: File not found at '{ENCRYPTED_FILE_PATH}'. Please check the path and try again.")
        exit()

    # Read the Base64 encoded ciphertext from the file
    try:
        with open(ENCRYPTED_FILE_PATH, 'r') as f:
            ciphertext_from_file = f.read().strip() # .strip() to remove any leading/trailing whitespace or newlines
        print(f"Successfully read encrypted data from '{ENCRYPTED_FILE_PATH}'.")
    except Exception as e:
        print(f"Error reading file '{ENCRYPTED_FILE_PATH}': {e}")
        exit()

    # Get the decryption password from user input
    DECRYPTION_PASSWORD = input("Enter the decryption password: ")

    try:
        decrypted_content = decrypt_message_openssl_simple(ciphertext_from_file, DECRYPTION_PASSWORD)
        print("\n--- DECRYPTED CONTENT SUCCESSFULLY ---")
        print(decrypted_content)
        print("---------------------------------------")
    except ValueError as e:
        print(f"\nDECRYPTION ERROR: {e}")
        print("The password might be incorrect, or the data might be corrupted.")
        print("Please double-check the password and the content of the encrypted file.")
    except Exception as e:
        print(f"\nAn unexpected error occurred during decryption: {e}")