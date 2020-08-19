import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///course.db")



# Generates the homepage that the user lands on
@app.route("/")
@login_required
def index():
    if request.method == 'GET':
        # Gets user's courses
        rows = db.execute("SELECT * FROM course_relations WHERE user_id = ?;", session["user_id"])

        return render_template("index.html", rows=rows)


# Gets the login page and processes attempts to log in
@app.route("/login", methods=['GET', 'POST'])
def login():
    # Clears info from any previous users
    session.clear()
    # Gets log in page if requested
    if request.method == 'GET':
        return render_template("login.html")
    # Or else processes log in
    else:
        # Checks username entred
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # Checks password entred
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        # Gets the user with the specified username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Returns apology if no user with such username exists or password doesnt match
        if len(rows) != 1 or rows[0]["password"] != request.form.get("password"):
            return apology("invalid username and/or password", 403)

        # Log in successful
        session["user_id"] = rows[0]["user_id"]
        # Redirects to homepage of user
        return redirect("/")


# Handles registration related requests
@app.route("/register", methods=['GET', 'POST'])
def register():
    # Returns registration page
    if request.method == 'GET':
        return render_template("register.html")
    else:

        username = request.form.get("username")
        password = request.form.get("password")


        # Ensure username was submitted
        if username == None:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif password == None:
            return apology("must provide password", 403)
        # Ensure passwords match
        elif password != request.form.get("confirm_password"):
            return apology("passwords must match")


        # Adds new user to database
        db.execute("INSERT INTO users (username, password) VALUES (?, ?);", username, password)
        # Redirects to login page
        return redirect("/login")


# Handles logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    # Returns course add page
    if request.method == 'GET':
        return render_template("add.html")
    else:
        course_id = int(request.form.get("room") + "" + request.form.get("block"))

        # Checks if the course already exists
        rows = db.execute("SELECT * FROM courses WHERE id = ?", course_id)


        # If course already not in db, adds course to db
        if len(rows) == 0:

            db.execute("INSERT INTO courses (id, title, teacher_id, rating) VALUES (?, ?, ?, ?);", course_id, "holder title", 0, 0)

        # Add to course relations

        db.execute("INSERT INTO course_relations (course_id, user_id, class_title) VALUES (?, ?, ?);", course_id, session["user_id"], request.form.get("title"))

        # Redirects to homepage
        return redirect("/")


# Gets profile page
@app.route("/profile/<int:p_id>", methods=['GET', 'POST'])
@login_required
def display_profile(p_id):

    # Friend cases --> 0 = self, 1 = can send request, 2 = can cancel request, 3 Friends (shows friends and ), 4 accept friend
    user_id = session["user_id"]
    # If the profile is of the current user
    if p_id == user_id:
        friend_case = 0
    else:
        # Gets user's friends
        user_friends = get_as_list(db.execute("SELECT second_friend_id FROM friend_relations WHERE first_friend_id = ?;", user_id), "second_friend_id")
        # If visiting friend's profile
        if p_id in user_friends:
            friend_case = 3
        else:
            p_friend_requests_to = get_as_list(db.execute("SELECT to_id FROM friend_requests WHERE from_id = ?;", p_id), "to_id")
            user_friend_requests_to = get_as_list(db.execute("SELECT to_id FROM friend_requests WHERE from_id = ?;", user_id), "to_id")
            # If user has a friend request from person
            if user_id in p_friend_requests_to:
                friend_case = 4
            # If user has send a friend request to person
            elif p_id in user_friend_requests_to:
                friend_case = 2
            # If none of the above, the user may send a request to this non friend person
            else:
                friend_case = 1

    rows = db.execute("SELECT * FROM course_relations WHERE user_id = ?;", p_id)
    person_row = db.execute("SELECT * FROM users WHERE user_id = ?;", p_id)

    return render_template("profile.html", person_id=p_id, user_id=user_id, friend_case=friend_case, rows=rows, person_row=person_row)


# Gets friends page
@app.route("/friends")
@login_required
def friends():
    # Gets user's friends
    rows = db.execute("SELECT * FROM users WHERE user_id IN (SELECT second_friend_id FROM friend_relations WHERE first_friend_id = ?);", session["user_id"])

    return render_template("friends.html", rows=rows)

# Gets friends request's page
@app.route("/friend_requests")
@login_required
def friend_requests():
    user_id = session["user_id"]
    # Gets user's friends
    rows = db.execute("SELECT * FROM users WHERE user_id IN (SELECT from_id FROM friend_requests WHERE to_id = ?);", user_id)
    return render_template("friend_requests.html", rows=rows, user_id=user_id)


# Gets page to show who the user has courses with
@app.route("/with_whom/<int:course_id>", methods=["POST"])
@login_required
def with_whom(course_id):

    # Gets user's friends who have the same course
    users_with_whom = db.execute("SELECT * FROM users WHERE user_id in (SELECT user_id FROM course_relations WHERE course_id = ?) "
    + "AND user_id in (SELECT second_friend_id FROM friend_relations WHERE first_friend_id = ?);", course_id, session['user_id'])

    course_name = db.execute("SELECT * FROM courses WHERE id = ?", course_id)[0]['title']

    return render_template("with_whom.html", rows=users_with_whom, course_name=course_name)



# Handles searches
@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    if request.form.get("search"):
        search_term = request.form.get("search")
    else:
        search_term = ""
    # Gets users whose names are like the search term
    rows = db.execute('SELECT * FROM users WHERE username LIKE ?;', "%" + search_term + "%")
    return render_template("search.html", rows=rows)


# Process interpersonal requests
@app.route("/process_request/<int:request_id>/<int:from_id>/<int:to_id>", methods=['POST'])
@login_required
def process(request_id, from_id, to_id):
    # Friend cases --> 1 = send request, 2 = cancel request, 3 Remove Friend, 4 accept friend
    # If user trying to send request, send request
    if request_id == 1:
        db.execute("INSERT INTO friend_requests (from_id, to_id) VALUES (?, ?);", from_id, to_id)
    # If user is trying to cancel request, cancel request
    elif request_id == 2:
        db.execute("DELETE FROM friend_requests WHERE from_id = ? AND to_id = ?;", from_id, to_id)
    # If user is trying to remove friend, remove friend
    elif request_id == 3:
        db.execute("DELETE FROM friend_relations WHERE first_friend_id = ? AND second_friend_id = ?;", from_id, to_id)
        db.execute("DELETE FROM friend_relations WHERE first_friend_id = ? AND second_friend_id = ?;", to_id, from_id)
    # If user is trying to accept a friend request, make them friends
    else:
        db.execute("INSERT INTO friend_relations (first_friend_id, second_friend_id) VALUES (?, ?)", from_id, to_id)
        db.execute("INSERT INTO friend_relations (first_friend_id, second_friend_id) VALUES (?, ?)", to_id, from_id)
    # Redirect to profile page
    return redirect("/profile/" + str(to_id))


# Takes a list of dictionaries and returns the specified property of the dictionary in a list
def get_as_list(list_of_dict, prop):
    new_lst = []
    for dic in list_of_dict:
        new_lst.append(dic[prop])
    return new_lst







