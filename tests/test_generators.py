from aum_server.utils import generate_accounts
from fill_server.utils import generate_fill


def test_generate_accounts():
    accounts = generate_accounts(5)

    assert 1 <= len(accounts) <= 5
    assert sum(accounts.values()) == 100


def test_generate_fill():
    fill = generate_fill()

    assert set(fill) == {"stock_ticker", "price", "quantity"}
    assert 1 <= fill["price"] <= 100
    assert 1 <= fill["quantity"] <= 100
