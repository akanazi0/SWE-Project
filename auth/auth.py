#test flask login
from flask import Flask, redirect, render_template, url_for, session, request
from flask_sqlalchemy import SQLAlchemy 
app = Flask(__name__)

#create the SQlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)

#user model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable = False)
    password = db.Column(db.String(120), nullable = False)

# Create database tables
with app.app_context():
    db.create_all()

#dummy username and password
USERNAME = "admin"
PASSWORD = "password"
#Use get and post methods
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
    #get form data
        username = request.form.get("username")
        password = request.form.get("password")

        #check credentials
        if username == USERNAME and password == PASSWORD:
            return redirect(url_for("welcome"))
        else:
            return render_template("login.html",
                                error="invalid username or password")
    return render_template("login.html")

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #get data from form
        username = request.form.get("username")
        password = request.form.get("password")
        #Check if username exsits
        if User.query.filter_by(username = username).first():
            #if username exists, return error
            return render_template('register.html', error ="username already exists")
        #Else Add the new user to the user Database
        newUser = User(username = username, password= password)
        db.session.add(newUser)
        db.session.commit()
        return redirect(url_for("login")) #redirect to login Url
    return render_template("register.html") #redirects to another template of URL


if __name__ == '__main__':
    app.run(debug=True)