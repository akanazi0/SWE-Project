from flask import Flask, redirect, render_template, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

# Booking model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# Admin credentials
USERNAME = "admin"
PASSWORD = "ntsa3d"

# User login
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Check admin credentials
        if username == USERNAME and password == PASSWORD:
            session['username'] = username
            return redirect(url_for("admin_dashboard"))
        # Check database credentials
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for("welcome"))
        else:
            return render_template("login.html", error="invalid username or password")
    return render_template("login.html")

# User registration
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="username already exists")
        newUser = User(username=username, password=password)
        db.session.add(newUser)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/admin/all-events')
def admin_all_events():
    # Optional: check if the user is admin
    if session.get('username') != USERNAME:
        flash("Admin access only.")
        return redirect(url_for('login'))
    events = Event.query.order_by(Event.date).all()
    return render_template('events.html', events=events)

# User homepage: shows all events and allows booking
@app.route('/welcome')
def welcome():
    events = Event.query.order_by(Event.date).all()
    return render_template('welcome.html', events=events)

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
    # Prevent duplicate bookings
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
    return render_template("admin_dashboard.html")

# Organizer portal (event management)
@app.route('/admin/organizer-portal', methods=['GET', 'POST'])
def event_portal():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        description = request.form['description']
        new_event = Event(name=name, date=date, description=description)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('event_portal'))
    events = Event.query.order_by(Event.date).all()
    return render_template('organizer_portal.html', events=events)

# Admin: Show all events
@app.route('/admin/show-events')
def admin_show_events():
    events = Event.query.order_by(Event.date).all()
    return render_template('admin_show_events.html', events=events)

# Delete event (from organizer portal)
@app.route('/admin/events/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('event_portal'))

if __name__ == '__main__':
    app.run(debug=True)