# BTC Brute Force Key Checker

This tool continuously generates random Bitcoin addresses and checks them against a target list. If a match is found, it encrypts the corresponding private key and sends it via email.

## Tool's Core Functionality

  * **Random Bitcoin Key Generation:** Continuously generates random Bitcoin key pairs (private key and public address).
  * **Address Checking:** Compares the newly generated Bitcoin address against a pre-provided list of target Bitcoin addresses (in the `riches.txt` file).
  * **Secure Notification:** If a matching address is found, the private key will be encrypted using a password you provide and sent to your recipient email address as an attachment.
  * **Multi-threading:** Utilizes multiple processing threads to accelerate the checking process.
  * **Decryption Tool:** Includes a separate script (`decrypt.py`) to decrypt the encrypted key files you receive via email.
  * **Automated Setup:** The `full_setup_env.sh` script helps to automatically set up the necessary environment on a Linux system.

## ⚠️ Important Note

**This tool is intended for educational and experimental purposes only.** Brute-forcing Bitcoin private keys is an extremely difficult and practically impossible task due to the immense size of the Bitcoin address space. Using this tool to find keys for existing addresses is highly unlikely to succeed.

## Prerequisites

### For System (when using `full_setup_env.sh`):

  * Debian/Ubuntu-based Linux operating system (e.g., Ubuntu, Debian, Kali Linux).
  * `sudo` privileges to install system packages.
  * Internet connection.

### For Manual Installation:

  * Python 3.x
  * `pip` (Python package installer)
  * `openssl` (command-line utility)

## Setup Guide (`full_setup_env.sh`)

The easiest way to get started is by using the `full_setup_env.sh` script.

1.  **Download and Run the Setup Script:**

    ```bash
    wget https://raw.githubusercontent.com/tamprimary/btc_brute/main/full_setup_env.sh -O setup.sh && sudo bash setup.sh
    ```

      * `wget ... -O setup.sh`: Downloads the script from GitHub and saves it as `setup.sh`.
      * `&&`: Ensures the second command runs only if the download is successful.
      * `sudo bash setup.sh`: Executes the script with superuser privileges.

    This script will automatically:

      * Update the system.
      * Install necessary tools (`openssl`, `python3-venv`).
      * Create the `btc_brute_force` project directory.
      * Download essential files (`script.py`, `decrypt.py`, `riches.txt`, etc.).
      * Set up a Python virtual environment (`venv`) and install Python libraries (`bit`, `pycryptodome`).
      * Install a cron job to automatically clear your log file (`script.log`) daily.

    Please follow the on-screen prompts during the script's execution.

## Usage

Once the setup is complete, you can run the main tool.

1.  **Navigate to the Project Directory:**

    ```bash
    cd btc_brute_force
    ```

2.  **Activate the Virtual Environment:**
    This ensures you are using the correct installed libraries.

    ```bash
    source venv/bin/activate
    ```

    You should see `(venv)` appear at the beginning of your command prompt.

3.  **Prepare the `riches.txt` file:**
    This file contains the list of Bitcoin addresses you want to check against. Each address should be on a separate line.
    Example `riches.txt`:

    ```
    1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
    1Mz715NAWmm1NDJ39QYg9ESgiMmddyXdnX
    ```

4.  **Run the Key Checking Script (`script.py`):**
    You need to provide your email information and encryption password via arguments.
    **Important:** For `smtp_password`, use a **Gmail App Password**, not your regular Gmail password. Learn how to generate an App Password at [Google Support](https://support.google.com/accounts/answer/185833?hl=vi).

    ```bash
    nohup python script.py \
        --smtp_user 'your_sending_email@gmail.com' \
        --smtp_password 'your_gmail_app_password' \
        --recipient_email 'your_recipient_email@example.com' \
        --encryption_password 'YourStrongEncryptionPassword123' \
        > script.log 2>&1 &
    ```

      * `nohup ... &`: This command allows the script to run in the background even if you close the terminal.
      * `> script.log 2>&1`: All script output will be redirected to the `script.log` file.

5.  **Check Status and Logs:**

      * To see if the script is running: `ps aux | grep script.py`
      * To view script messages (logs): `tail -f script.log` (press `Ctrl+C` to exit `tail`).

6.  **Decrypt Found Keys (`decrypt.py`):**
    If you receive an email with an attachment (`found_key.enc`), download that file to your project directory. Then run:

    ```bash
    python decrypt.py --input_file found_key.enc --encryption_password 'YourStrongEncryptionPassword123'
    ```

    Replace `'YourStrongEncryptionPassword123'` with the password you used for encryption. The decrypted content will be displayed on your terminal.

## Project Structure

```
btc_brute_force/
├── venv/                   # Python virtual environment
├── script.py               # Main Bitcoin key checking script
├── decrypt.py              # Script to decrypt found key files
├── riches.txt              # List of target Bitcoin addresses (one address per line)
├── foundkey.txt            # (Automatically created) Stores found public addresses and private keys
├── count.txt               # (Automatically created) Stores the latest count of checked addresses
├── wallet.xlsx             # (Optional) If your script uses it, otherwise ignore
└── full_setup_env.sh       # Automated setup script for Linux
```

## Contributing

You can contribute by opening issues or submitting pull requests for improvements or bug fixes.

## License

[MIT License](https://www.google.com/search?q=LICENSE) (You should add a https://www.google.com/search?q=LICENSE file to your repo)
