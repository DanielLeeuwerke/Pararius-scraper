import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import os
import time

# Function to fetch webpage content with retry
def get_webpage_content_with_retry(url):
    max_retries = 5
    for retry in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.text
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            print(f"Error fetching content from {url}. Retry {retry+1}/{max_retries}. Error: {e}")
            time.sleep(10)  # Wait for a while before retrying
    return None

# Function to count occurrences of a class in the HTML
def count_class_occurrences(html_content, class_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    return len(soup.find_all(class_=class_name))

# Function to check for updates and send email
def check_for_updates(url, email_address, email_password, smtp_server, smtp_port):
    # Load the previous and most recent counts from files or initialize them if not available
    try:
        with open("previous_count.txt", "r") as file:
            previous_count = int(file.read())
    except FileNotFoundError:
        previous_count = 0

    try:
        with open("most_recent_count.txt", "r") as file:
            most_recent_count = int(file.read())
    except FileNotFoundError:
        most_recent_count = 0

    # Fetch the current webpage content
    current_content = get_webpage_content_with_retry(url)

    if current_content is None:
        print(f"Error fetching content from {url}. Skipping.")
        return  # Skip further processing for this URL

    # Count the occurrences of the specified class in the current content
    current_count = count_class_occurrences(current_content, 'listing-search-item listing-search-item--list listing-search-item--for-rent')

    print(f"URL: {url}")
    print(f"Current Count: {current_count}")
    print(f"Previous Count: {previous_count}")
    print(f"Most Recent Count: {most_recent_count}")

    # Compare the current count with the previous and most recent counts
    if current_count > most_recent_count:
        # The count has increased since the last notification, indicating new listings

        # Send an email with the updated webpage link
        msg = EmailMessage()
        msg.set_content(f"The webpage at {url} has new house listings. Check them out!\n{url}")

        msg['Subject'] = f"New House Listings: {url}"
        msg['From'] = 'studiozoeker@gmail.com'
        msg['To'] = 'danieltl2610@gmail.com'

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_address, email_password)
            server.send_message(msg)

        # Update the most recent count to the current count
        with open("most_recent_count.txt", "w") as file:
            file.write(str(current_count))
    elif current_count < most_recent_count:
        # The count has decreased since the last notification, indicating some listings were removed

        # Send an email with the updated webpage link
        msg = EmailMessage()
        msg.set_content(f"The webpage at {url} has fewer house listings. Check them out!\n{url}")

        msg['Subject'] = f"Removed House Listings: {url}"
        msg['From'] = 'studiozoeker@gmail.com'
        msg['To'] = 'danieltl2610@gmail.com'

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_address, email_password)
            server.send_message(msg)

        # Update the most recent count to the current count
        with open("most_recent_count.txt", "w") as file:
            file.write(str(current_count))

    # Update the previous count to the current count
    with open("previous_count.txt", "w") as file:
        file.write(str(current_count))

if __name__ == "__main__":
    # Replace these values with your email credentials and the URL you want to monitor
    url_to_monitor = "https://www.pararius.nl/huurwoningen/groningen/0-1000"
    email_address = "studiozoeker@gmail.com"
    email_password = "xxxx"
    smtp_server = "smtp.gmail.com"
    smtp_port = 465  # Update with your SMTP port

    while True:
        check_for_updates(url_to_monitor, email_address, email_password, smtp_server, smtp_port)
        
        # Sleep for 30 seconds before checking again
        time.sleep(30)
