import sys
import os
sys.path.append(os.path.abspath("."))

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

def test_successful_login(client):
    response = client.post("/login", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/protected")

def test_already_logged_in_redirect(client):
     with client:
          client.post("/login", data={"username": "testuser", "password": "testpass"})
          response = client.get("/login")
          assert response.status_code == 302


def test_login_with_empty_credentials(client):
     response = client.post("/login", data={"username": "", "password": ""})
     assert b"Invalid credentials" in response.data
