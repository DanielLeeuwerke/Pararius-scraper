import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import os
import time
import re

# Function to fetch webpage content
def get_webpage_content(url):
    response = requests.get(url)
    return response.text if response.ok else None

# Function to check for updates and send email if prices change
def check_for_price_changes(url, email_address, email_password, smtp_server, smtp_port):
    # Load the previous prices from a file or initialize it if not available
    try:
        with open("previous_prices.txt", "r") as file:
            previous_prices = file.read()
    except FileNotFoundError:
        previous_prices = None

    # Fetch the current webpage content
    current_content = get_webpage_content(url)

    if current_content is None:
        print(f"Error fetching content from {url}. Skipping.")
        return  # Skip further processing for this URL

    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(current_content, 'html.parser')
    
    # Extract all text from the page
    page_text = soup.get_text()

    # Define a regular expression pattern to match prices (e.g., $99.99, €49.95, 99.99 USD, etc.)
    price_pattern = r'(\$|€|\b(?:dollar|euro)\b)?\s*([\d,.]+)\s*(?:USD|EUR)?'

    # Find all matches of the price pattern in the page text
    current_prices = re.findall(price_pattern, page_text)

    current_prices_str = ' '.join([''.join(price) for price in current_prices])

    print(f"URL: {url}")
    print(f"Current Prices: {current_prices_str}")
    print(f"Previous Prices: {previous_prices}")

    # Compare the previous and current prices
    if current_prices_str != previous_prices:
        # Prices have changed, send an email
        msg = EmailMessage()
        msg.set_content(f"Prices on the webpage at {url} have changed. New prices: {current_prices_str}")

        msg['Subject'] = f"Price Change Alert: {url}"
        msg['From'] = 'studiozoeker@gmail.com'
        msg['To'] = 'danieltl2610@gmail.com'

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_address, email_password)
            server.send_message(msg)

        # Save the current prices to the file for future comparison
        with open("previous_prices.txt", "w") as file:
            file.write(current_prices_str)

if __name__ == "__main__":
    # Replace these values with your email credentials and the URL you want to monitor
    url_to_monitor = "https://www.google.com/finance/quote/BTC-EUR?sa=X&ved=2ahUKEwjypOyP16-BAxXaiP0HHZNLBz0Q-fUHegQIFBAf"
    email_address = "studiozoeker@gmail.com"
    email_password = "xxxx"
    smtp_server = "smtp.gmail.com"
    smtp_port = 465  # Update with your SMTP port

    while True:
        check_for_price_changes(url_to_monitor, email_address, email_password, smtp_server, smtp_port)
        
        # Sleep for 60 seconds before checking again
        time.sleep(60)
