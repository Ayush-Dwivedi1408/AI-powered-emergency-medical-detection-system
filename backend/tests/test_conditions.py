def test_list_conditions_empty_when_unseeded(client):
    r = client.get("/conditions/")
    assert r.status_code == 200
    assert r.json() == []


def test_get_condition_by_id(client, db_session, seeded_condition):
    r = client.get(f"/conditions/{seeded_condition.id}")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Heart Attack"
    assert body["base_severity"] == "CRITICAL"


def test_get_nonexistent_condition_404(client):
    r = client.get("/conditions/99999")
    assert r.status_code == 404
