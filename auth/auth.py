from flask import Flask, redirect, render_template, url_for, request, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Admin credentials
USERNAME = "admin"
PASSWORD = "ntsa3d"

# File upload config
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    category = db.Column(db.String(50), nullable=True)  # <-- Add this line

# Booking model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

# Review model
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

# Login route
@app.route('/', methods=["GET", "POST"])
@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username, password=password).first()
        if user or (username == USERNAME and password == PASSWORD):
            session['username'] = username
            print("Login successful, redirecting to welcome")  # Debug
            return redirect(url_for("welcome"))
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error)

# Register route
# Register route
@app.route('/register', methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(username=username).first():
            error = "Username already exists"
        else:
            newUser = User(username=username, password=password)
            db.session.add(newUser)
            db.session.commit()
            session['username'] = username  # Log the user in
            return redirect(url_for("welcome"))  # Redirect to welcome page
    return render_template("register.html", error=error)

# Welcome page (user homepage)
@app.route('/welcome')
def welcome():
    # Get filter parameters
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    budget = request.args.get('budget', '').strip()
    date = request.args.get('date', '').strip()
    reset = request.args.get('reset')

    # Start with all events
    query = Event.query

    # Apply filters if not reset
    if not reset:
        if search:
            query = query.filter(
                (Event.name.ilike(f'%{search}%')) |
                (Event.description.ilike(f'%{search}%'))
            )
        # Example: If you add a category field to Event, filter here
        # if category:
        #     query = query.filter(Event.category == category)
        if budget:
            if budget == 'budget':
                query = query.filter(Event.price < 500)
            elif budget == 'midrange':
                query = query.filter(Event.price >= 500, Event.price < 1500)
            elif budget == 'luxury':
                query = query.filter(Event.price >= 1500)
        if date:
            query = query.filter(Event.date == date)

    events = query.order_by(Event.date).all()

    # Booked events logic (unchanged)
    booked_events = []
    username = session.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            bookings = Booking.query.filter_by(user_id=user.id).all()
            event_ids = [b.event_id for b in bookings]
            booked_events = Event.query.filter(Event.id.in_(event_ids)).order_by(Event.date).all()
    return render_template('welcome.html', events=events, booked_events=booked_events)

# Show only the logged-in user's booked events
@app.route('/events')
def show_events():
    username = session.get('username')
    if not username:
        flash("Please log in to view your events.")
        return redirect(url_for('login'))
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found.")
        return redirect(url_for('login'))
    bookings = Booking.query.filter_by(user_id=user.id).all()
    event_ids = [b.event_id for b in bookings]
    events = Event.query.filter(Event.id.in_(event_ids)).order_by(Event.date).all()
    return render_template('events.html', events=events)

# Book an event
@app.route('/book/<int:event_id>', methods=['POST'])
def book_event(event_id):
    username = session.get('username')
    if not username:
        flash("Please log in to book events.")
        return redirect(url_for('login'))
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found.")
        return redirect(url_for('login'))
    if Booking.query.filter_by(user_id=user.id, event_id=event_id).first():
        flash("Already booked this event.")
        return redirect(url_for('welcome'))
    booking = Booking(user_id=user.id, event_id=event_id)
    db.session.add(booking)
    db.session.commit()
    flash("Event booked!")
    return redirect(url_for('show_events'))

# Admin dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('username') != USERNAME:
        flash("Admin access only.")
        return redirect(url_for('login'))
    return render_template("admin_dashboard.html")

# Organizer portal (event management)
@app.route('/admin/organizer-portal', methods=['GET', 'POST'])
def event_portal():
    if session.get('username') != USERNAME:
        flash("Admin access only.")
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        description = request.form['description']
        price = request.form.get('price', 0)
        category = request.form.get('category', '')
        image_url = ''
        image_file = request.files.get('image_file')
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(filepath)
            image_url = url_for('uploaded_file', filename=filename)
        new_event = Event(
            name=name,
            date=date,
            description=description,
            price=price,
            image_url=image_url,
            category=category  # <-- Save category
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('event_portal'))
    events = Event.query.order_by(Event.date).all()
    return render_template('org_portal.html', events=events)

# Admin: Show all events (admin view)
@app.route('/admin/show-events')
def admin_show_events():
    if session.get('username') != USERNAME:
        flash("Admin access only.")
        return redirect(url_for('login'))
    events = Event.query.order_by(Event.date).all()
    return render_template('admin_show_events.html', events=events)

# Admin: Show all events (user view)
@app.route('/admin/all-events')
def admin_all_events():
    if session.get('username') != USERNAME:
        flash("Admin access only.")
        return redirect(url_for('login'))
    events = Event.query.order_by(Event.date).all()
    return render_template('events.html', events=events)

# Delete event (from organizer portal)
@app.route('/admin/events/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if session.get('username') != USERNAME:
        flash("Admin access only.")
        return redirect(url_for('login'))
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('event_portal'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/event/<int:event_id>/reviews', methods=['GET', 'POST'])
def event_reviews(event_id):
    event = Event.query.get_or_404(event_id)
    reviews = Review.query.filter_by(event_id=event_id).all()
    if request.method == 'POST':
        username = session.get('username')
        if not username:
            flash("Please log in to leave a review.")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=username).first()
        if not user and username == 'admin':
            # Allow admin to leave a review even if not in User table
            user_id = 0
            display_name = 'admin'
        elif user:
            user_id = user.id
            display_name = user.username
        else:
            flash("User not found. Please log in again.")
            return redirect(url_for('login'))
        content = request.form.get('content', '').strip()
        rating = int(request.form.get('rating', 5))
        if not content:
            flash("Review cannot be empty.")
        else:
            review = Review(
                event_id=event_id,
                user_id=user_id,
                username=display_name,
                content=content,
                rating=rating
            )
            db.session.add(review)
            db.session.commit()
            flash("Review submitted!")
            return redirect(url_for('event_reviews', event_id=event_id))
    return render_template('reviews.html', event=event, reviews=reviews)

if __name__ == '__main__':
    app.run(debug=True)

