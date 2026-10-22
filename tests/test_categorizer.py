from categorizer import suggest_category


def test_known_words():
    assert suggest_category("Jollibee lunch") == "food"
    assert suggest_category("Grab ride to work") == "transport"
    assert suggest_category("Netflix subscription") == "entertainment"


def test_unknown_description_is_other():
    assert suggest_category("something random") == "other"


def test_whole_words_only():
    assert suggest_category("business meeting") == "other"


def test_suggest_endpoint(client, make_user):
    headers = make_user()
    response = client.post(
        "/expenses/suggest-category",
        json={"description": "Jollibee lunch"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {"category": "food"}


def test_suggest_endpoint_requires_login(client):
    response = client.post("/expenses/suggest-category", json={"description": "lunch"})
    assert response.status_code == 401
