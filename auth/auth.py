from flask import Flask, redirect, render_template, render_template_string, url_for, session, request
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

# Create the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# admin credentials

USERNAME = "admin"
PASSWORD = "ntsa3d"

@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check admin credentials
        if username == USERNAME and password == PASSWORD:
            return redirect(url_for("admin_dashboard"))
        # Check database credentials
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return redirect(url_for("welcome"))
        else:
            return render_template("login.html", error="invalid username or password")
    return render_template("login.html")

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

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

@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")


events = []

@app.route('/admin/events')
def event_index():
    return render_template_string("""
        <h1>Event List</h1>
        <ul>
        {% for event in events %}
            <li>
                {{ event['name'] }} - {{ event['date'] }}
                [<a href="{{ url_for('edit_event', event_id=loop.index0) }}">Edit</a>]
                [<a href="{{ url_for('delete_event', event_id=loop.index0) }}" onclick="return confirm('Are you sure?');">Delete</a>]
            </li>
        {% endfor %}
        </ul>
        <a href="{{ url_for('create_event') }}">Create New Event</a>
        <br><a href="{{ url_for('admin_dashboard') }}">Back to Dashboard</a>
    """, events=events)

@app.route('/admin/events/create', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        events.append({'name': name, 'date': date})
        return redirect(url_for('event_index'))
    return render_template_string("""
        <h1>Create Event</h1>
        <form method="post">
            Name: <input name="name"><br>
            Date: <input name="date" type="date"><br>
            <input type="submit" value="Create">
        </form>
        <a href="{{ url_for('event_index') }}">Back</a>
    """)

@app.route('/admin/events/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if event_id < 0 or event_id >= len(events):
        return "Event not found", 404
    if request.method == 'POST':
        events[event_id]['name'] = request.form['name']
        events[event_id]['date'] = request.form['date']
        return redirect(url_for('event_index'))
    event = events[event_id]
    return render_template_string("""
        <h1>Edit Event</h1>
        <form method="post">
            Name: <input name="name" value="{{ event['name'] }}"><br>
            Date: <input name="date" type="date" value="{{ event['date'] }}"><br>
            <input type="submit" value="Save">
        </form>
        <a href="{{ url_for('event_index') }}">Back</a>
    """, event=event)

@app.route('/admin/events/delete/<int:event_id>')
def delete_event(event_id):
    if event_id < 0 or event_id >= len(events):
        return "Event not found", 404
    events.pop(event_id)
    return redirect(url_for('event_index'))
if __name__ == '__main__':
    app.run(debug=True)