""" This module is used to periodically check my website's funcionality

1 - Check if all parts of website are functional, returning 200 responses
2 - Email me if an error is detected
3 - Restart linode server

 """

import smtplib

from flasksite.config import Config
import requests
from linode_api4 import LinodeClient, Instance


# Establish login credentials
myConfig = Config()
EMAIL_ADDRESS = myConfig.DEV_EMAIL_ADDRESS
EMAIL_PASSWORD = myConfig.DEV_EMAIL_PASSWORD
LINODE_TOKEN = myConfig.LINODE_TOKEN
LINODE_ID = myConfig.NHL_LINODE_ID


# Define functions to send email and reset server
def notify_user():
    """
     Use my personal development email account to notify that my website failed
     a request test and is therefore down.

     Args:
        None

     Returns:
        None

     Raises:
        None
     """

    # Connect to gmail via smtp
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:

        # Identify ourselves with mail server
        smtp.ehlo()

        # Encrypt transmissions
        smtp.starttls()

        # Re-ientify as encrypted connection
        smtp.ehlo()

        # Login to email server
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        # Create email contents
        subject = 'Your site is down'
        body = 'Make sure the server successfully restarted and is now functional'
        msg = f'Subject: {subject}\n\n{body}'

        smtp.sendmail(EMAIL_ADDRESS, 'jonathanholson@gmail.com', msg)


def reboot_server(server_id=LINODE_ID):
    """
    Using the Linode Python Library, reboot the specified server(s)

    Args:
        servers: list of ints - The integer ID numbers for servers to reboot

    Returns:
        None

    Raises:
        ValueError -- if supplied server IDs cannot be changed to integers
     """

    # Make sure server ID is an integer, or is at least convertible to one
    try:
        server_id = int(server_id)
    except ValueError as e:
        raise e

    # Connect to Linode
    client = LinodeClient(LINODE_TOKEN)

    # Harness my particular server
    my_server = client.load(Instance, server_id)

    # Reboot server
    my_server.reboot()


if __name__ == '__main__':

    # Create a list of URLs to check
    my_urls = [
        'https://jonathanolson.us',
        'https://jonathanolson.us/home',
        'https://jonathanolson.us/login',
        'https://jonathanolson.us/register',
        'https://jonathanolson.us/nhl_stats',
        'https://jonathanolson.us/todays_players',
        'https://jonathanolson.us/stamkostweets',
        'https://jonathanolson.us/account',
        'https://jonathanolson.us/create_recurly_account',
        'https://jonathanolson.us/update_recurly_account',
        'https://jonathanolson.us/cancel_subscription'
        ]

    # Check each URL from the list above
    for url in my_urls:

        try:
            # Make a request to my homepage; timeout after 5 secs
            r = requests.get(url, timeout=5)

            # Make sure this response is successful. If not, notify user and restart
            if r.status_code != 200:
                notify_user()
                reboot_server()

            else:
                print('All pages passed tests!')

        # If cannot connect, notify user and reboot server
        except Exception:
            notify_user()
            reboot_server()
            break
