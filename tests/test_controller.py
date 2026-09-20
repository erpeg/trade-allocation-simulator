import math

from controller.utils import Controller


def test_normalize_dict():
    controller = Controller()

    assert controller.normalize_dict({"account1": 3, "account2": 4}) == {
        "account1": 0.6,
        "account2": 0.8,
    }


def test_normalize_zero_values():
    controller = Controller()

    assert controller.normalize_dict({"account1": 0, "account2": 0}) == {
        "account1": 0.0,
        "account2": 0.0,
    }


def test_allocate_fill_toward_target_split():
    controller = Controller()
    controller.accounts_split = {"account1": 75, "account2": 25}
    controller.accounts_split_norm = controller.normalize_dict(controller.accounts_split)
    controller.add_work({"stock_ticker": "ABC", "price": 10, "quantity": 4})

    controller.do_work()

    assert controller.current_positions == {
        "ABC": {"account1": 3, "account2": 1}
    }
    assert math.isclose(sum(controller.current_positions["ABC"].values()), 4)


def test_zero_weight_account_receives_no_fill():
    controller = Controller()
    controller.accounts_split = {"zero": 0, "funded": 100}
    controller.accounts_split_norm = controller.normalize_dict(controller.accounts_split)
    controller.add_work({"stock_ticker": "ABC", "price": 10, "quantity": 10})

    controller.do_work()

    assert controller.current_positions == {
        "ABC": {"zero": 0, "funded": 10}
    }
