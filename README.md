-----

# BTC Brute Force Key Checker

This project provides a Python-based Bitcoin brute-force private key checker designed to find matching Bitcoin addresses from a predefined list. Upon finding a match, it securely encrypts the sensitive key information and sends it via email. A setup script is included to automate the environment configuration on Linux systems.

## ⚠️ Disclaimer

**This tool is for educational and experimental purposes only.** Brute-forcing Bitcoin private keys is computationally infeasible for all practical purposes, given the vastness of the Bitcoin address space. Attempting to find private keys for existing addresses is highly unlikely to succeed and may be considered a waste of resources. Do not use this tool for any illegal or malicious activities. The developers are not responsible for any misuse of this software.

## Features

  * **Multi-threaded:** Leverages multiple CPU cores for faster checking.
  * **Targeted Search:** Checks generated keys against a custom list of Bitcoin addresses (`riches.txt`).
  * **Secure Notification:**
      * Encrypts found private keys using a user-provided password via `openssl`.
      * Sends encrypted key data as an email attachment.
  * **Automated Setup:** Includes a `full_setup.sh` script to streamline the environment setup on Debian/Ubuntu-based systems (installs dependencies, creates virtual environment, downloads project files).
  * **Decryption Utility:** A separate `decrypt.py` script is provided to decrypt the received encrypted key files.

## Prerequisites

### For running the `full_setup.sh` script:

  * A Debian/Ubuntu-based Linux distribution (e.g., Ubuntu, Debian, Kali Linux).
  * `sudo` privileges for package installation.
  * Internet connection.

### For manual setup (if not using `full_setup.sh`):

  * Python 3.x
  * `pip` (Python package installer)
  * `openssl` (command-line tool)

## Setup Guide

The easiest way to get started is by using the `full_setup.sh` script.

### 1\. Download the Setup Script

```bash
wget https://raw.githubusercontent.com/tamprimary/btc_brute/main/full_setup.sh
chmod +x full_setup.sh
```

**Note:** Ensure `https://raw.githubusercontent.com/tamprimary/btc_brute/main/` is the correct base URL for your GitHub repository where `full_setup.sh` resides. If your repo name is different, please adjust the URL.

### 2\. Run the Setup Script

Execute the setup script. This script will:

  * Update system packages.
  * Install `openssl` and `python3-venv` (if not already installed).
  * Create a project directory named `btc_brute_force`.
  * Download `script.py`, `decrypt.py`, `riches.txt`, and `wallet.xlsx` (if specified) into the project directory.
  * Create empty `foundkey.txt` and `count.txt` files.
  * Set up a Python virtual environment (`venv`).
  * Install required Python libraries (`bit`, `pycryptodome`).

<!-- end list -->

```bash
./full_setup.sh
```

Follow the on-screen prompts. The script will output instructions upon completion.

## Usage

### 1\. Navigate to the Project Directory

After running the `full_setup.sh` script, you should be in your home directory or the directory where you ran the script. Navigate into the newly created project folder:

```bash
cd btc_brute_force
```

### 2\. Activate the Virtual Environment

It's crucial to activate the Python virtual environment to ensure all dependencies are correctly used.

```bash
source venv/bin/activate
```

You should see `(venv)` prepended to your terminal prompt, indicating the virtual environment is active.

### 3\. Prepare `riches.txt`

The `riches.txt` file should contain the Bitcoin addresses you want to check against, with one address per line.

Example `riches.txt`:

```
1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
1Mz715NAWmm1NDJ39QYg9ESgiMmddyXdnX
...
```

### 4\. Run the Bitcoin Key Checker (`script.py`)

The `script.py` now requires command-line arguments for your email and encryption configuration. Replace the placeholder values with your actual information.

  * `--smtp_user`: Your Gmail address (e.g., `your_email@gmail.com`). **You must use a Gmail App Password, not your regular Gmail password, for security reasons.** See [Google's instructions on App Passwords](https://support.google.com/accounts/answer/185833?hl=vi).
  * `--smtp_password`: Your Gmail App Password.
  * `--recipient_email`: The email address where you want to receive notifications. This can be the same as `--smtp_user`.
  * `--encryption_password`: A strong password that will be used to encrypt the found private keys. **Do not share this password.** You will need it to decrypt the attachment later.

<!-- end list -->

```bash
python script.py \
    --smtp_user 'your_gmail_address@gmail.com' \
    --smtp_password 'your_gmail_app_password' \
    --recipient_email 'your_recipient_email@example.com' \
    --encryption_password 'YourStrongEncryptionPassword123'
```

The script will start generating and checking addresses. If a match is found, an email will be sent to the `recipient_email` with an encrypted attachment (`found_key.enc`) containing the public address and the corresponding private key.

### 5\. Decrypting Found Keys (`decrypt.py`)

If you receive an encrypted attachment (`found_key.enc`), you can use the `decrypt.py` script to decrypt it.

First, download the `found_key.enc` file from your email to your project directory. Then run:

```bash
python decrypt.py --input_file found_key.enc --encryption_password 'YourStrongEncryptionPassword123'
```

Replace `'YourStrongEncryptionPassword123'` with the exact password you used during encryption. The decrypted content will be printed to your console.

## Project Structure

```
btc_brute_force/
├── venv/                   # Python virtual environment
├── script.py               # Main Bitcoin key checker script
├── decrypt.py              # Script to decrypt found key files
├── riches.txt              # List of Bitcoin addresses to check against (one per line)
├── foundkey.txt            # (Auto-generated) Stores found public addresses and private keys (unencrypted)
├── count.txt               # (Auto-generated) Logs the progress of checked addresses
├── wallet.xlsx             # (Optional) If your script uses it, otherwise remove
└── full_setup.sh           # Automated setup script for Linux
```

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements or bug fixes.

## License

[MIT License](https://www.google.com/search?q=LICENSE) (It's good practice to include a https://www.google.com/search?q=LICENSE file in your repo)

-----
