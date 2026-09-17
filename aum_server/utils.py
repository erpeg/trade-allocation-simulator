import random
import time
from datetime import datetime

import requests


def generate_accounts(accounts_threshold: int = 10):
    """Function generating splits of share for multiple accounts.

    Args:
        accounts_threshold (int, optional): Maximum number of accounts in the split. Defaults to 10.

    Returns:
        dict: Randomly generated account splits
    """
    sum_of_values = 100
    account_splits = {}
    number_of_accounts = random.randint(1, accounts_threshold)
    for account_index in range(1, number_of_accounts+1):  # adding start of range and +1 to have numbering of accounts starting at 1
        account_value = random.randint(0, sum_of_values)
        account_splits[f"account{account_index}"] = account_value

        # condition used to make sure sum of % is equal 100
        if account_index == number_of_accounts:
            account_splits[f"account{account_index}"] = sum_of_values
        sum_of_values -= account_value

    return account_splits
    
def send_request(aum_endpoint, max_number_of_accounts):
    """Sending request with randomly generated trade fills

    Args:
        aum_endpoint (str): URL to AUM endpoint
        max_number_of_accounts (int): Maximum number of accounts to split
    """
    while True:
        starttime = time.time()
        data_to_send = generate_accounts(max_number_of_accounts)  # generating data
        requests.post(aum_endpoint, json=data_to_send, timeout=5).raise_for_status()
        print(f"Sent {data_to_send} on {datetime.now()}.")
        time.sleep(30 - starttime % 30)


