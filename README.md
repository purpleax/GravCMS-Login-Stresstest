# Login Stress Testing Script

This script simulates multiple user login attempts to a target website, allowing for load testing and debugging. It uses concurrent threads to send login requests and reports whether the login was successful or failed based on the response.

## Features

-   Extracts a dynamically generated nonce from the login page.
-   Allows specifying the login and login page URLs via command-line arguments.
-   Provides a `--debug` flag to print the HTML content of the login page.
-   Reports success or failure based on the response from the server.
-   Stops execution on rate-limiting or being blocked.

## Prerequisites

-   Python 3.x
-   Required Python packages: `requests`

Install the required package using `pip`:

    pip install requests

## Usage

### Basic Command

Run the script with the required login URL and login page URL:

    python3 script_name.py --login-url https://example.com/login --login-page-url https://example.com/login

### Debug Mode

To enable debug mode (prints the login page's HTML content):

    python3 script_name.py --login-url https://example.com/login --login-page-url https://example.com/login --debug

### Credentials File Format

The credentials file (`credentials.txt`) should be in the format `username:password`, with one credential pair per line:

    user1@example.com:password123
    user2@example.com:password456

### Command-line Options

-   `--login-url`: The URL where the POST request is sent for login (required).
-   `--login-page-url`: The URL where the nonce is extracted from (required).
-   `--debug`: Enable debug mode to print the login page HTML content (optional).

### Example

Run the script as follows:

    python3 script_name.py --login-url https://stresstest.example.com/login --login-page-url https://stresstest.fastlylab.com/login

For debug mode:

    python3 script_name.py --login-url https://stresstest.example.com/login --login-page-url https://stresstest.fastlylab.com/login --debug

## How It Works

1.  **Nonce Extraction**: The script first sends a GET request to the login page to extract a nonce value (if present) using a regular expression.
2.  **Login Attempts**: After extracting the nonce, the script sends POST requests to the login URL with the specified credentials and nonce.
3.  **Success/Failure Reporting**: The script checks the response text for success or failure keywords and reports accordingly:
    -   **Success**: The response contains the keyword `successfully logged in`.
    -   **Failure**: The response contains the keyword `Login failed`.
4.  **Concurrency**: The script uses `ThreadPoolExecutor` to simulate multiple concurrent login attempts.