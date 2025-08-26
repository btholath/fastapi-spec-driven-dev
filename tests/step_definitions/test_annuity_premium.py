from pytest_bdd import given, when, then, scenario
from fastapi.testclient import TestClient
from app.main import app

@scenario("../features/annuity_premium.feature", "Calculate premium for a fixed annuity")
def test_annuity_premium():
    pass

@given("a logged-in user")
def logged_in_user():
    return {"id": 123, "role": "user"}

@when('they submit an annuity request with principal $10000, term 5 years, and rate 3%')
def submit_anuity_request():
    client = TestClient(app)
    client.headers["Authorization"] = "Bearer fake-token"
    response = client.post(
        "/annuities/premium",
        json={"principal": 10000, "term_years": 5, "annual_rate": 3}
    )
    return response

@then("the API returns a premium of $2124.60")
def check_premium(response):
    assert response.status_code == 200
    assert response.json()["premium"] == 2124.60