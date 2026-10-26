def add(client, headers, category, amount):
    return client.post(
        "/expenses",
        json={"description": "x", "amount": amount, "category": category},
        headers=headers,
    )


def test_summary_requires_login(client):
    assert client.get("/summary").status_code == 401


def test_summary_totals_and_insight(client, make_user):
    headers = make_user()
    add(client, headers, "food", 100)
    add(client, headers, "food", 50)
    add(client, headers, "transport", 50)

    response = client.get("/summary", headers=headers)
    assert response.status_code == 200
    body = response.json()

    assert float(body["total"]) == 200
    assert body["by_category"][0]["category"] == "food"
    assert body["by_category"][0]["percent"] == 75.0
    assert "Food" in body["insight"]


def test_summary_only_counts_own_expenses(client, make_user):
    alice = make_user("alice@example.com")
    bob = make_user("bob@example.com")
    add(client, alice, "food", 100)

    body = client.get("/summary", headers=bob).json()
    assert float(body["total"]) == 0
    assert body["by_category"] == []


def test_summary_empty_month(client, make_user):
    headers = make_user()
    add(client, headers, "food", 100)

    body = client.get("/summary?year=2000&month=1", headers=headers).json()
    assert float(body["total"]) == 0
    assert body["insight"] == "No expenses recorded this month."
