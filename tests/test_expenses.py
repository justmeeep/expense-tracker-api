def create(client, headers, **overrides):
    payload = {"description": "Lunch", "amount": 150.50, "category": "food"}
    payload.update(overrides)
    return client.post("/expenses", json=payload, headers=headers)


def test_expenses_require_login(client):
    assert client.get("/expenses").status_code == 401
    assert client.post("/expenses", json={}).status_code == 401


def test_create_and_list(client, make_user):
    headers = make_user()
    response = create(client, headers)
    assert response.status_code == 201
    assert float(response.json()["amount"]) == 150.50

    listing = client.get("/expenses", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_invalid_amount(client, make_user):
    headers = make_user()
    response = create(client, headers, amount="abc")
    assert response.status_code == 422


def test_filter_by_category(client, make_user):
    headers = make_user()
    create(client, headers, category="food")
    create(client, headers, category="transport")
    create(client, headers, category="food")

    response = client.get("/expenses?category=food", headers=headers)
    assert len(response.json()) == 2


def test_get_missing_expense(client, make_user):
    headers = make_user()
    assert client.get("/expenses/999", headers=headers).status_code == 404


def test_update_only_changes_sent_fields(client, make_user):
    headers = make_user()
    expense_id = create(client, headers).json()["id"]

    response = client.patch(
        f"/expenses/{expense_id}", json={"amount": 200}, headers=headers
    )
    assert response.status_code == 200
    body = response.json()
    assert float(body["amount"]) == 200
    assert body["description"] == "Lunch"


def test_delete(client, make_user):
    headers = make_user()
    expense_id = create(client, headers).json()["id"]

    assert client.delete(f"/expenses/{expense_id}", headers=headers).status_code == 204
    assert client.get(f"/expenses/{expense_id}", headers=headers).status_code == 404


def test_users_cannot_see_each_others_expenses(client, make_user):
    alice = make_user("alice@example.com")
    bob = make_user("bob@example.com")
    expense_id = create(client, alice).json()["id"]

    assert client.get("/expenses", headers=bob).json() == []
    assert client.get(f"/expenses/{expense_id}", headers=bob).status_code == 404
    assert (
        client.patch(
            f"/expenses/{expense_id}", json={"amount": 1}, headers=bob
        ).status_code
        == 404
    )
    assert client.delete(f"/expenses/{expense_id}", headers=bob).status_code == 404

    # Alice's expense is untouched
    assert client.get(f"/expenses/{expense_id}", headers=alice).status_code == 200
