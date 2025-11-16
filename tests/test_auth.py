import pytest
from auth.auth import app, db, User, Event, generate_password_hash


@pytest.fixture
def client():
    """
    Creates a test client for the app.
    This sets up a fresh, in-memory database for every single test.
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create a test member user (for LGN-02 and REG-03)
            hashed_pw = generate_password_hash("memberpass1")
            member_user = User(
                email="member@test.com", username="member", password=hashed_pw
            )

            # Create a test event (for SRCH-01 and BEV-07)
            test_event = Event(
                id=1,  # Give it a predictable ID for booking
                name="Existing Event",
                date="2025-11-20",
                description="A test event.",
                price=100,
            )

            db.session.add(member_user)
            db.session.add(test_event)
            db.session.commit()

        yield client

        with app.app_context():
            db.drop_all()


# --- Log-in Test Cases ---


def test_lgn_01_admin_login_success(client):
    """Tests TC ID: LGN-01 - Login with valid admin credentials"""
    response = client.post(
        "/login",
        data={"username": "admin", "password": "adminpass123"},
        follow_redirects=True,
    )

    # Expected Result: Login success -> Admin dashboard
    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data


def test_lgn_02_member_login_success(client):
    """Tests TC ID: LGN-02 - Login with valid member credentials"""
    response = client.post(
        "/login",
        data={"username": "member", "password": "memberpass1"},
        follow_redirects=True,
    )

    # Expected Result: Login success -> Member homepage
    assert response.status_code == 200
    assert b"Existing Event" in response.data


def test_lgn_03_wrong_password(client):
    """Tests TC ID: LGN-03 - Wrong password"""
    response = client.post(
        "/login", data={"username": "member", "password": "wrongpassword"}
    )

    # Expected Result: Error message
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_lgn_04_wrong_username(client):
    """Tests TC ID: LGN-04 - Wrong username"""
    response = client.post(
        "/login", data={"username": "invalid_user", "password": "memberpass1"}
    )

    # Expected Result: Error message
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


# --- Registration Test Cases ---


def test_reg_01_and_02_registration_success(client):
    """Tests TC ID: REG-01 & REG-02 - Valid email and password policy"""
    response = client.post(
        "/register",
        data={
            "email": "new_user@hotmail.com",
            "username": "new_user",
            "password": "newpassword123",
        },
        follow_redirects=True,
    )

    # Expected Result: Registration success -> Member homepage
    assert response.status_code == 200
    assert b"Booked Events" in response.data


def test_reg_03_email_already_used(client):
    """Tests TC ID: REG-03 - Email already used"""
    response = client.post(
        "/register",
        data={
            "email": "member@test.com",
            "username": "another_user",
            "password": "password123",
        },
    )

    # Expected Result: Error: "Email already exists"
    assert response.status_code == 200
    assert b"Email already exists" in response.data


# --- Search and Booking Test Cases ---


def test_srch_01_search_existing(client):
    """Tests TC ID: SRCH-01 - Search for existing event"""
    # First, log in as a member to access the welcome page
    client.post("/login", data={"username": "member", "password": "memberpass1"})

    response = client.get("/welcome?search=Existing+Event")

    # Expected Result: Show the event
    assert response.status_code == 200
    assert b"Existing Event" in response.data  # The event name should be in the HTML


#
# def test_srch_02_search_non_existing(client):
#   """Tests TC ID: SRCH-02 - Search for non-existing event"""
#   client.post("/login", data={"username": "member", "password": "memberpass1"})
#   response = client.get("/welcome?search=Non-Existing+Event")
#
# Expected Result: Event is unavailable (not shown)
#    assert response.status_code == 200
#    assert (
#         b"Existing Event" not in response.data
#     )  # Make sure the other event isn't there
#     assert b"Non-Existing Event" not in response.data
#


def test_bev_07_book_not_logged_in(client):
    """Tests TC ID: BEV-07 - Book event without login"""
    response = client.post("/book/1", follow_redirects=True)

    # Expected Result: Redirect to login
    assert response.status_code == 200
    assert b"Please log in to book events" in response.data
    assert b"Login" in response.data
