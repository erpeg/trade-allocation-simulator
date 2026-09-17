import asyncio
import math
from collections import deque

import requests


class Controller:
    def __init__(self) -> None:
        self.queue = deque([])
        self.accounts_split = {
            "account1": 100
        }
        self.accounts_split_norm = {
            "account1": 1
        }
        self.current_positions = {}
        self.position_url = "http://localhost:8002/position_send"

    def add_work(self, item: dict):
        """Adding new fill task to process via worker

        Args:
            item (dict): fill task in dictionary format
        """
        self.queue.append(item)

    def normalize_dict(self, input_dictionary: dict[str, int]) -> dict[str, float]:
        """Normalizing input dictionary

        Args:
            input_dictionary (Dict[str, int]): dictionary to normalize

        Returns:
            (Dict[str, float]): Normalized dictionary
        """
        magnitude = math.sqrt(sum(value ** 2 for value in input_dictionary.values()))
        if magnitude == 0:
            return {key: 0.0 for key in input_dictionary}
        return {key: value / magnitude for key, value in input_dictionary.items()}

    def select_account(self, new_stock_positions_normalized):
        """Selecting account that should be given new stock. AUM account normalized splits are compared with Current Positions
        that are normalized, account with the highest difference from the perfect state is selected

        Args:
            new_stock_positions_normalized (dict): Temp Stock Positions dict

        Returns:
            str: Account that should be assigned new stock
        """
        eligible_accounts = [
            account
            for account, weight in self.accounts_split.items()
            if weight > 0
        ]
        return max(
            eligible_accounts,
            key=lambda account: (
                self.accounts_split_norm[account]
                - new_stock_positions_normalized.get(account, 0),
                self.accounts_split_norm[account],
                account,
            ),
        )

    def do_work(self):
        """Function taking the first on the queue fill request and processing it
        """
        to_process = self.queue.popleft()
        stock = to_process["stock_ticker"]
        quantity = to_process["quantity"]

        stock_positions = self.current_positions.setdefault(stock, {})
        for account in self.accounts_split:
            stock_positions.setdefault(account, 0)

        for _ in range(quantity):
            stock_positions_norm = self.normalize_dict(stock_positions)
            chosen_account = self.select_account(stock_positions_norm)
            stock_positions[chosen_account] += 1

    async def run_works(self):
        """Function used to trigger worker.
        """
        await asyncio.sleep(5.)
        while True:
            await asyncio.sleep(0.1)
            try:
                self.do_work()
            except (IndexError, KeyError, TypeError, ValueError):
                pass

    async def send_data(self):
        """Function used to send data to Postion Server
        """
        while True:
            try:
                await asyncio.to_thread(
                    requests.post,
                    self.position_url,
                    json=self.current_positions,
                    timeout=5,
                )
            except requests.RequestException:
                pass
            await asyncio.sleep(7.95)
