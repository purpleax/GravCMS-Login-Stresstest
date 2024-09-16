import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import sys
import argparse

# Function to extract the nonce from the login page
def get_nonce(login_page_url, debug=False):
    print(f"Fetching nonce from: {login_page_url}")  # Debug print to verify URL
    response = requests.get(login_page_url)
    if response.status_code == 200:
        if debug:
            print("Login page HTML content:")
            print(response.text[:500])  # Print the first 500 characters of the page for inspection

        # Use regex to extract the nonce value
        nonce_pattern = r'name="login-form-nonce" value="([a-zA-Z0-9]+)"'
        match = re.search(nonce_pattern, response.text)
        if match:
            return match.group(1)
        else:
            print("Nonce not found in the page.")
    else:
        print(f"Failed to fetch the login page. Status code: {response.status_code}")
    return None

# Function to read credentials from a file and handle multiple colon issues
def read_credentials(file_path):
    credentials = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            if len(parts) == 2:
                credentials.append((parts[0], parts[1]))
            else:
                print(f"Skipping invalid line: {line.strip()}")
    return credentials

# Function to simulate a single user login
def login(username, password, login_url, login_page_url, debug=False):
    print(f"Attempting login for: {username}")  # Debug print for each login attempt
    nonce = get_nonce(login_page_url, debug)  # Pass the debug flag to control printing
    if nonce:
        print(f"Username: {username}, Password: {password}, Nonce: {nonce}")
        payload = {
            'username': username,
            'password': password,
            'task': 'login.login',
            'login-form-nonce': nonce
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0'
        }
        
        # Make the POST request with the specified Content-Type and User-Agent headers
        response = requests.post(login_url, data=payload, headers=headers)

        # Check if the POST request was successful (HTTP 200)
        if response.status_code == 200:
            print("POST request was successful (HTTP 200).")

            # Print the response content only if the debug flag is set
            if debug:
                print(f"Full response text:\n{response.text}")

            # Normalize the response text (lowercase and strip extra whitespace)
            response_text = response.text.lower().strip()

            # Check the response content for login success or failure
            if "successfully logged in" in response_text:
                return 200, "Login successful"
            elif "access denied" in response_text:  # Updated to match the "Access denied" failure message
                return 401, "Access denied"
            else:
                return response.status_code, "Unknown login response"
        else:
            print(f"POST request failed with status code: {response.status_code}")
            return response.status_code, "POST request failed"
    else:
        return None, "Nonce not found"

# Function to simulate multiple users logging in
def simulate_load(credentials, login_url, login_page_url, debug=False):
    print(f"Login URL: {login_url}")  # Debug print to verify login URL
    print(f"Login Page URL: {login_page_url}")  # Debug print to verify login page URL

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(login, username, password, login_url, login_page_url, debug) for username, password in credentials]
        for future in as_completed(futures):
            status_code, response_message = future.result()
            if status_code:
                print(f"Response code: {status_code}, Message: {response_message}")
                if status_code == 200:
                    print("Login was successful.")
                elif status_code == 401:
                    print("Access denied for this user.")  # Update output to reflect the new keyword
                elif status_code == 429:
                    print("You have been rate limited. Stopping execution.")
                    sys.exit(1)  # Stop script execution on rate limiting
                elif status_code == 406:
                    print("You have been blocked. Stopping execution.")
                    sys.exit(1)  # Stop script execution on being blocked
            else:
                print(f'Error: {response_message}')

if __name__ == "__main__":
    # Set up argument parser for command-line options
    parser = argparse.ArgumentParser(description='Simulate login attempts.')
    parser.add_argument('--login-url', required=True, help='Login URL for POST requests')
    parser.add_argument('--login-page-url', required=True, help='URL to fetch the login page and extract the nonce')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode to print HTML content')
    
    args = parser.parse_args()
    
    # Debugging prints to verify arguments
    print(f"Command-line login URL: {args.login_url}")
    print(f"Command-line login page URL: {args.login_page_url}")
    
    # File containing the credentials in username:password format
    credentials_file = 'credentials.txt'
    
    # Read the credentials from the file
    credentials = read_credentials(credentials_file)
    
    # Simulate login for each credential with or without debug mode
    simulate_load(credentials, login_url=args.login_url, login_page_url=args.login_page_url, debug=args.debug)
