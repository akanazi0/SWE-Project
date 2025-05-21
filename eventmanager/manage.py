from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# In-memory event storage
events = []

@app.route('/')
def index():
    return render_template_string("""
        <h1>Event List</h1>
        <ul>
        {% for event in events %}
            <li>
                {{ event['name'] }} - {{ event['date'] }}
                [<a href="{{ url_for('edit_event', event_id=loop.index0) }}">Edit</a>]
            </li>
        {% endfor %}
        </ul>
        <a href="{{ url_for('create_event') }}">Create New Event</a>
    """, events=events)

@app.route('/create', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        events.append({'name': name, 'date': date})
        return redirect(url_for('index'))
    return render_template_string("""
        <h1>Create Event</h1>
        <form method="post">
            Name: <input name="name"><br>
            Date: <input name="date" type="date"><br>
            <input type="submit" value="Create">
        </form>
        <a href="{{ url_for('index') }}">Back</a>
    """)

@app.route('/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if event_id < 0 or event_id >= len(events):
        return "Event not found", 404
    if request.method == 'POST':
        events[event_id]['name'] = request.form['name']
        events[event_id]['date'] = request.form['date']
        return redirect(url_for('index'))
    event = events[event_id]
    return render_template_string("""
        <h1>Edit Event</h1>
        <form method="post">
            Name: <input name="name" value="{{ event['name'] }}"><br>
            Date: <input name="date" type="date" value="{{ event['date'] }}"><br>
            <input type="submit" value="Save">
        </form>
        <a href="{{ url_for('index') }}">Back</a>
    """, event=event)

if __name__ == '__main__':
    app.run(debug=True)