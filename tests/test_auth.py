import pytest
from auth.auth import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200

def test_logout(client):
     with client:
          client.post("/login", data={"username": "testuser", "password": "testpass"})
          response = client.get("/logout")
          assert response.status_code == 302  
          response = client.get("/protected")
          assert response.status_code == 302

def test_invalid_login(client):
     response = client.post("/login", data={"username": "wronguser", "password": "wrongpass"})
     assert b"Invalid credentials" in response.data


def test_already_logged_in_redirect(client):
     with client:
          client.post("/login", data={"username": "testuser", "password": "testpass"})
          response = client.get("/login")
          assert response.status_code == 302

def test_access_login_page_when_not_logged_in(client):
     response = client.get("/login")
     assert response.status_code == 200

def test_session_persistence(client):
     with client:
          client.post("/login", data={"username": "testuser", "password": "testpass"})
          response = client.get("/protected")
          assert response.status_code == 200
          response = client.get("/protected")
          assert response.status_code == 200

def test_logout_redirects_to_login(client):
     with client:
          client.post("/login", data={"username": "testuser", "password": "testpass"})
          response = client.get("/logout")
          assert response.status_code == 302
          assert response.headers["Location"].endswith("/login")

def test_login_with_empty_credentials(client):
     response = client.post("/login", data={"username": "", "password": ""})
     assert b"Invalid credentials" in response.data
