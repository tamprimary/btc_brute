#!/bin/bash

#wget https://raw.githubusercontent.com/tamprimary/btc_brute/main/full_setup_env.sh -O setup.sh && sudo bash setup.sh

# --- Configuration ---
PROJECT_DIR="btc_brute_force" # The main project folder name
GITHUB_RAW_URL="https://raw.githubusercontent.com/tamprimary/btc_brute/main" # Base URL for raw files

# List of files to download from GitHub
# Adjust these URLs if your files are in a different repository or path
DOWNLOAD_FILES=(
    "script.py"       # Your main script (e.g., the one with send_email_with_attachment)
    "decrypt.py"      # Your decryption script
    "riches.txt"      # The list of addresses to check against
    "wallet.xlsx"     # If needed by your script, otherwise remove or adapt
)

# Files that should exist (might be created by script, or empty initially)
TOUCH_FILES=(
    "foundkey.txt"
    "count.txt"
)

# --- Functions ---

# Function to check if a command exists
command_exists () {
    type "$1" &> /dev/null ;
}

# --- 1. Update package list ---
echo "Updating system package list..."
sudo apt update || { echo "Failed to update package list. Exiting."; exit 1; }
echo "System package list updated."
echo " "

# --- 2. Install openssl ---
echo "Checking and installing openssl..."
if ! command_exists openssl
then
    echo "openssl not found. Installing openssl..."
    sudo apt install -y openssl || { echo "Failed to install openssl. Exiting."; exit 1; }
    echo "openssl installed successfully."
	echo " "
else
    echo "openssl is already installed."
	echo " "
fi

# --- 3. Install python3-venv (for creating virtual environments) ---
echo "Checking and installing python3-venv..."
if ! dpkg -s python3-venv &> /dev/null
then
    echo "python3-venv not found. Installing python3-venv..."
    sudo apt install -y python3-venv || { echo "Failed to install python3-venv. Exiting."; exit 1; }
    echo "python3-venv installed successfully."
	echo " "
else
    echo "python3-venv is already installed."
	echo " "
fi

# --- 4. Prepare project directory ---
echo "Preparing project directory: $PROJECT_DIR"
if [ -d "$PROJECT_DIR" ]; then
    echo "Directory $PROJECT_DIR already exists. Skipping creation."
else
    mkdir "$PROJECT_DIR" || { echo "Failed to create directory $PROJECT_DIR. Exiting."; exit 1; }
    echo "Directory $PROJECT_DIR created."
fi
cd "$PROJECT_DIR" || { echo "Failed to change directory to $PROJECT_DIR. Exiting."; exit 1; }
echo "Changed to directory: $(pwd)"
echo " "

# --- 5. Download files from GitHub ---
echo "Downloading necessary files from GitHub..."
for file in "${DOWNLOAD_FILES[@]}"; do
    FILE_URL="$GITHUB_RAW_URL/$file"
    echo "Downloading $file from $FILE_URL..."
    wget -q "$FILE_URL" -O "$file" || { echo "Failed to download $file. Please check URL and internet connection. Exiting."; exit 1; }
    echo "$file downloaded."
done
echo " "

# --- 6. Create empty placeholder files if they don't exist ---
echo "Creating placeholder files if they don't exist..."
for file in "${TOUCH_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        touch "$file"
        echo "Created empty file: $file"
		sudo chmod o+w "$file"
    else
        echo "File $file already exists."
    fi
done
echo " "

# --- 7. Create and activate Python virtual environment ---
echo "Creating Python virtual environment 'venv'..."
python3 -m venv venv || { echo "Failed to create virtual environment. Exiting."; exit 1; }
echo "Virtual environment 'venv' created."

echo "Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated. You should see (venv) in your prompt."
echo " "

# --- 8. Install Python libraries ---
echo "Installing Python libraries: bit and pycryptodome..."
pip install bit || { echo "Failed to install 'bit'. Exiting."; deactivate; exit 1; }
pip install pycryptodome || { echo "Failed to install 'pycryptodome'. Exiting."; deactivate; exit 1; }
echo "Python libraries installed successfully."
echo " "

# --- Deactivate venv after installation if not needed for the rest of setup ---
deactivate
echo "Virtual environment deactivated."
echo " "

# --- 9. Setup Cron Job for Log Cleanup (Modified to handle /root/ path) ---
echo "Setting up cron job to clear script.log daily..."
CRON_JOB_COMMAND="0 0 * * * rm ${CURRENT_PROJECT_PATH}/script.log"
# Get the current crontab for root
(sudo crontab -l 2>/dev/null | grep -v -F "${CRON_JOB_COMMAND}" ; echo "${CRON_JOB_COMMAND}") | sudo crontab -
echo "Cron job added: ${CRON_JOB_COMMAND}"
echo " "

echo "---------------------------------------------------------"
echo "System setup complete. Your environment is ready!"
echo "Project directory: $(pwd)"
echo "A cron job has been set up to clear ${CURRENT_PROJECT_PATH}/script.log daily at midnight."
echo "To run your main Python script (e.g., script.py),"
echo "make sure you are in the '$PROJECT_DIR' directory"
echo "and the virtual environment is activated (you should see (venv) in your prompt)."
echo "If not, run: source venv/bin/activate"
echo "Then run your script:"
echo "nohup python script.py --smtp_user 'your_gmail_address@gmail.com' --smtp_password 'your_gmail_app_password' --recipient_email 'your_recipient_email@example.com' --encryption_password 'YourStrongEncryptionPassword123' > script.log 2>&1 &"
echo "To check log: tail -f script.log"
echo "To stop script: pkill -f 'python script.py'"
echo "---------------------------------------------------------"
echo " "

echo "RUN:"
echo "cd btc_brute_force"
echo "sudo chmod o+w foundkey.txt count.txt or sudo chown username:username foundkey.txt count.txt"
echo "source venv/bin/activate"
echo "python script.py --smtp_user 'your_gmail_address@gmail.com' --smtp_password 'your_gmail_app_password' --recipient_email 'your_recipient_email@example.com' --encryption_password 'YourStrongEncryptionPassword123' > script.log 2>&1 &"
echo "---------------------------------------------------------"
echo " "