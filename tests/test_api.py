from fastapi.testclient import TestClient

from controller.main import app, controller

client = TestClient(app)


def test_invalid_fill_is_rejected_without_poisoning_queue():
    controller.queue.clear()
    controller.current_positions.clear()

    invalid_response = client.post("/fill", json={"quantity": 1})
    valid_response = client.post(
        "/fill",
        json={"stock_ticker": "XYZ", "price": 12, "quantity": 2},
    )
    controller.do_work()

    assert invalid_response.status_code == 422
    assert valid_response.status_code == 200
    assert controller.current_positions == {"XYZ": {"account1": 2}}


def test_invalid_allocation_targets_are_rejected():
    assert client.post("/aum", json={}).status_code == 422
    assert client.post("/aum", json={"account1": 0}).status_code == 422
    assert client.post("/aum", json={"account1": -1}).status_code == 422


def test_non_finite_numbers_are_rejected_without_changing_targets():
    controller.accounts_split = {"account1": 100}
    controller.accounts_split_norm = {"account1": 1}

    aum_response = client.post(
        "/aum",
        content='{"funded":NaN,"zero":0}',
        headers={"content-type": "application/json"},
    )
    fill_response = client.post(
        "/fill",
        content='{"stock_ticker":"XYZ","price":NaN,"quantity":1}',
        headers={"content-type": "application/json"},
    )

    assert aum_response.status_code == 422
    assert fill_response.status_code == 422
    assert controller.accounts_split == {"account1": 100}
    assert controller.accounts_split_norm == {"account1": 1}
