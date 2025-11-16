from flask import (
    Flask,
    redirect,
    render_template,
    url_for,
    request,
    session,
    flash,
    send_from_directory,
)
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

# Track failed login attempts and block time
login_attempts = {}
BLOCK_TIME = timedelta(minutes=5)
MAX_ATTEMPTS = 5
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Admin credentials
USERNAME = "admin"
PASSWORD = "ntsa3d"

# File upload config
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# User model
# create user database that stores usernames and passwords
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


# Event model
# create event database that stores properties of each event
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    category = db.Column(db.String(50), nullable=True)


# Booking model
class Booking(
    db.Model
):  # create database that stores each user id with each event the user booked
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)


# Review model
# create database that stores user reviews
# for each event with the respective information for each user
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)


# create databse that stores IP adresses for each user
# to ensure a block if a user has failed log in attempts
class IP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), unique=True, nullable=False)
    count = db.Column(db.Integer, default=0)
    blocked_until = db.Column(db.DateTime, nullable=True)


with app.app_context():
    db.create_all()
# possibility of security risk
# (if a user repeats incorrect credentials it bans the user for a short amount out time)


# Login route
# Ip is requested to give an adress block on the specific id


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    ip = request.remote_addr
    now = datetime.now()
    ip_record = IP.query.filter_by(ip=ip).first()

    # Check if IP is blocked
    if ip_record and ip_record.blocked_until:
        if now < ip_record.blocked_until:
            error = f"Too many failed attempts. Try again after {ip_record.blocked_until.strftime('%H:%M:%S')}."
            return render_template("login.html", error=error)
        else:
            # Unblock after time passes
            ip_record.count = 0
            ip_record.blocked_until = None
            db.session.commit()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        #  Find user by username only
        user = User.query.filter_by(username=username).first()
        is_authenticated = False

        if user:
            # Check the submitted plain password with the stored hash
            is_authenticated = check_password_hash(user.password, password)

        #  Use the authentication flag for success check
        if is_authenticated:  # Login successful for either user or admin

            session["username"] = username
            if not ip_record:  # stores user IP at login
                ip_record = IP(ip=ip, count=0)
                db.session.add(ip_record)
            else:  # if log in is successful redirect to welcome
                ip_record.count = 0
                ip_record.blocked_until = None
            db.session.commit()
            return redirect(url_for("welcome"))
        else:
            # if log in is unseccessful add count to number
            # of allowed times for inccorect log in
            if not ip_record:
                ip_record = IP(ip=ip, count=1)
                db.session.add(ip_record)
            else:  # adds 1 to count for each fail
                ip_record.count += 1
            if ip_record.count >= MAX_ATTEMPTS:
                # if count reaches amount of max attempts
                # then blocks the user for 5 minutes
                ip_record.blocked_until = now + BLOCK_TIME
                error = f"Too many failed attempts. Try again after {(now + BLOCK_TIME).strftime('%H:%M:%S')}."
            else:
                # shows how many attempts user has before the block takes place
                error = f"Invalid username or password. Attempt {ip_record.count} of {MAX_ATTEMPTS}."
            db.session.commit()
    return render_template("login.html", error=error)


# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":  # requests data from user database
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        if len(password) < 5:
            error = "password must be at least 5 characters"
            return render_template("register.html", error=error)

        has_digit = False
        for char in password:
            if char.isdigit():
                has_digit = True
                break
        if not has_digit:
            error = "password must have at least one digit"
            return render_template("register.html", error=error)

        if User.query.filter_by(
            username=username
        ).first():  # queries database to see if username already exists
            error = "Username already exists"
        elif User.query.filter_by(email=email).first():
            error = "Email already exists"
        else:
            # if username or email is not in the databse
            # adds the new user to the database
            hashed_password = generate_password_hash(password)
            newUser = User(email=email, username=username, password=hashed_password)
            db.session.add(newUser)
            db.session.commit()
            session["username"] = username  # Log the user in
            return redirect(url_for("welcome"))  # Redirect to welcome page
    return render_template("register.html", error=error)


# Welcome page (user homepage)
@app.route("/welcome")
def welcome():
    # Get filter parameters
    search = request.args.get("search", "").strip()
    budget = request.args.get("budget", "").strip()
    date = request.args.get("date", "").strip()
    reset = request.args.get("reset")

    # Start with all events
    query = Event.query

    # Apply filters if not reset
    if not reset:
        if search:
            query = query.filter(
                (Event.name.ilike(f"%{search}%"))
                | (Event.description.ilike(f"%{search}%"))
            )
        # Example: If you add a category field to Event, filter here
        # if category:
        #     query = query.filter(Event.category == category)
        if budget:
            if budget == "budget":
                query = query.filter(Event.price < 500)
            elif budget == "midrange":
                query = query.filter(Event.price >= 500, Event.price < 1500)
            elif budget == "luxury":
                query = query.filter(Event.price >= 1500)
        if date:
            query = query.filter(Event.date == date)

    events = query.order_by(Event.date).all()

    # Booked events logic
    booked_events = []
    # stores booked events in an array for each user
    username = session.get("username")
    # get username from databse for specific user
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            # displays all booked events for specific user
            bookings = Booking.query.filter_by(user_id=user.id).all()
            event_ids = [b.event_id for b in bookings]
            booked_events = (
                Event.query.filter(Event.id.in_(event_ids)).order_by(Event.date).all()
            )
    return render_template("welcome.html", events=events, booked_events=booked_events)


# Show only the logged-in user's booked events
@app.route("/events")
def show_events():
    username = session.get("username")  # checks if user is logged in
    if not username:
        flash("Please log in to view your events.")
        return redirect(
            url_for("login")
        )  # redirects user to login in order to log in to view events
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found.")  # if user does not exist
        return redirect(
            url_for("register")
        )  # redirects user to register page to create account
    bookings = Booking.query.filter_by(user_id=user.id).all()
    # queries booking databse for respective user to show events the user booked
    # finds event ids for each event
    event_ids = [b.event_id for b in bookings]

    events = (
        Event.query.filter(Event.id.in_(event_ids)).order_by(Event.date).all()
    )  # displays events to user on the events page
    return render_template("events.html", events=events)


# Book an event
@app.route("/book/<int:event_id>", methods=["POST"])
def book_event(event_id):
    username = session.get("username")  # check if user is logged in
    if not username:  # if user is not logged in
        flash("Please log in to book events.")
        return redirect(url_for("login"))  # redirects to login
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found.")  # if user does not exist
        return redirect(url_for("register"))  # redirects user to register
    if Booking.query.filter_by(
        user_id=user.id, event_id=event_id
    ).first():  # checks if user has booked the event previously
        flash(
            "Already booked this event."
        )  # flashes warning if the user already booked the event
        return redirect(url_for("welcome"))
    booking = Booking(user_id=user.id, event_id=event_id)  # user books event
    # adds to the booking database specific to the user
    db.session.add(booking)

    db.session.commit()
    flash("Event booked!")
    return redirect(
        url_for("show_events")
    )  # redirects to show_events where it displays the users booked events


# Admin dashboard
@app.route("/admin-dashboard")
def admin_dashboard():
    if session.get("username") != USERNAME:  # if current session belongs to normal user
        # and not admin it refuses access (USERNAME = admin username)
        flash("Admin access only.")
        return redirect(url_for("login"))
    return render_template(
        "admin_dashboard.html"
    )  # redirects to admin dashboard when logged in as admin


# Organizer portal (event management)
@app.route(
    "/admin/organizer-portal", methods=["GET", "POST"]
)  # uses GET and POST requests to access data
# from server and send data to server
def event_portal():
    if (
        session.get("username") != USERNAME
    ):  # checks if user logged in is an admin or not
        flash("Admin access only.")
        return redirect(url_for("login"))
    if request.method == "POST":  # requests POST methods to upload new data
        # for new events (name, date, description, etc)
        name = request.form["name"]
        date = request.form["date"]
        description = request.form["description"]
        price = request.form.get("price", 0)
        category = request.form.get("category", "")
        image_url = ""
        image_file = request.files.get("image_file")
        if image_file and allowed_file(
            image_file.filename
        ):  # logic for allowing image uploading
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(filepath)
            image_url = url_for("uploaded_file", filename=filename)
        new_event = Event(
            name=name,
            date=date,
            description=description,
            price=price,
            image_url=image_url,
            category=category,
        )  # create the event using data uploaded
        db.session.add(new_event)  # add new event to Event database
        db.session.commit()
        return redirect(url_for("event_portal"))
    events = Event.query.order_by(Event.date).all()
    return render_template(
        "org_portal.html", events=events
    )  # redirects to organizer portal page to add more events if needed


# Admin: Show all events (admin view)
@app.route("/admin/show-events")
def admin_show_events():
    if (
        session.get("username") != USERNAME
    ):  # checks if user logged in is an admin or not
        flash("Admin access only.")
        return redirect(url_for("login"))
    events = Event.query.order_by(Event.date).all()
    return render_template(
        "admin_show_events.html", events=events
    )  # redirects to show all admin specific events page


# Admin: Show all events (user view)
@app.route("/admin/all-events")
def admin_all_events():
    if (
        session.get("username") != USERNAME
    ):  # checks if user logged in is an admin or not
        flash("Admin access only.")
        return redirect(url_for("login"))
    events = Event.query.order_by(Event.date).all()
    return render_template(
        "events.html", events=events
    )  # redirects to show all events page(as if a user was viewing the events)


# Delete event (from organizer portal)
@app.route("/admin/events/delete/<int:event_id>", methods=["POST"])
def delete_event(event_id):
    if (
        session.get("username") != USERNAME
    ):  # checks if user logged in is an admin or not
        flash("Admin access only.")
        return redirect(url_for("login"))
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)  # remove event from Events database
    db.session.commit()
    return redirect(url_for("event_portal"))


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], filename
    )  # access files from upload folder


def allowed_file(filename):
    return (
        "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )  # decide what type of file is allowed


@app.route("/event/<int:event_id>/reviews", methods=["GET", "POST"])
def event_reviews(event_id):
    event = Event.query.get_or_404(event_id)
    reviews = Review.query.filter_by(event_id=event_id).all()
    if request.method == "POST":
        username = session.get("username")
        if not username:
            flash("Please log in to leave a review.")
            return redirect(
                url_for("login")
            )  # redirects to login if user is not logged in
        user = User.query.filter_by(username=username).first()
        if not user and username == "admin":
            # Allow admin to leave a review even if not in User table
            user_id = 0
            display_name = "admin"
        elif user:
            user_id = user.id
            display_name = user.username
        else:
            flash("User not found. Please log in again.")
            return redirect(url_for("login"))  # should redirect to register
        # content of the review box
        content = request.form.get("content", "").strip()
        rating = int(request.form.get("rating", 5))  # rating out of 5 stars
        if not content:
            flash(
                "Review cannot be empty."
            )  # if content box is empty then flash the error
        else:
            review = Review(
                event_id=event_id,
                user_id=user_id,
                username=display_name,
                content=content,
                rating=rating,
            )  # create review with added data
            db.session.add(review)  # add review to the review database
            db.session.commit()
            flash("Review submitted!")
            return redirect(url_for("event_reviews", event_id=event_id))
    return render_template("reviews.html", event=event, reviews=reviews)


if __name__ == "__main__":
    with app.app_context():
        # create all databases
        db.create_all()
        # check if admin credentials exist
        admin = User.query.filter_by(username=USERNAME).first()
        # if admin does not exist
        if not admin:
            # create secure hashed admin password
            admin_hashed_password = generate_password_hash(PASSWORD)
            # create user model for admin
            admin = User(
                username=USERNAME,
                password=admin_hashed_password,
                email="ntsa3d@gmail.com",
            )
            db.session.add(admin)
            db.session.commit()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    app.run(debug=False)
