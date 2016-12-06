from flask import Flask, request, render_template, redirect, flash, session
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import re
app = Flask(__name__)
app.secret_key = "kneesandtoes"
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app, "wallDemo")
passRegex = re.compile(r'^(?=.{8,15}$)(?=.*[A-Z])(?=.*[0-9]).*$')
emailRegex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
nameRegex = re.compile(r'^(?=.{2,})([a-zA-z]*)$')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/createUser', methods=['POST'])
def createUser():
    errors = False
    empties = False
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    confirm = request.form['confirm']
    for key, value in request.form.items():
        if len(value) < 1:
            empties = True
    if empties == True:
        flash("All fields must be filled.", "register")
        return redirect('/')
    if not emailRegex.match(email):
        flash("Invalid email address", "register")
        errors = True
    if not passRegex.match(password):
        flash("Password must contain a number, a capital letter, and be between 8-15 characters", "register")
        errors = True
    if not nameRegex.match(first_name) or not nameRegex.match(last_name):
        flash("Names must contain at least two letters and contain only letters.", "register")
        errors = True
    if password != confirm:
        flash("Password must match its confimation", "register")
        errors = True
    if errors == True:
        return redirect('/')

    # NO ERRORS

    pw_hash = bcrypt.generate_password_hash(password)
    insert_query = "INSERT INTO users (email, first_name, last_name, password, created_at, updated_at) VALUES (:email, :first_name, :last_name, :pw_hash, NOW(), NOW())"
    query_data = {'email': email, 'first_name': first_name, 'last_name': last_name, 'pw_hash': pw_hash}
    userid = mysql.query_db(insert_query, query_data)
    session['username'] = first_name
    session['userid'] = userid
    return redirect('/success')

@app.route('/login', methods = ['POST'])
def login():
    email=request.form['email']
    password = request.form['password']
    user_query = 'SELECT * FROM users where email = :email LIMIT 1'
    query_data = {'email': email}
    user = mysql.query_db(user_query, query_data)
    if user:
        if bcrypt.check_password_hash(user[0]['password'], password):
            session['username'] = user[0]['first_name']
            session['userid'] = user[0]['id']
            return redirect('/success')
    else:
        flash("We're sorry, we could not log you in.", "login")
        return redirect('/')

@app.route('/success')
def success():
    if 'username' not in session:
        return redirect('/')
    query = "SELECT message, messages.id, messages.created_at, first_name FROM messages JOIN users ON messages.user_id = users.id"
    allmessages = mysql.query_db(query)

    commentsquery = "SELECT comment, comments.created_at, first_name, message_id, comments.id from comments JOIN users ON comments.user_id = users.id"
    allcomments = mysql.query_db(commentsquery)
    print "got all the comments", allcomments

    return render_template('wall.html', messages = allmessages, comments = allcomments)

@app.route('/create_message', methods=['POST'])
def create_message():
    message = request.form['message']
    insert_query = "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES (:user_id, :message, NOW(), NOW())"
    data = {"user_id": session['userid'], "message": message}
    messageid = mysql.query_db(insert_query, data)
    print "inserted a message, got messageid back", messageid
    if messageid:
        return redirect('/success')
    else:
        flash("Sorry, we were not able to post your message", "posts")
        return redirect('/success')

@app.route('/create_comment', methods=['POST'])
def create_comment():
    print "made it comments", request.form['messageid']
    insert_query = "INSERT INTO comments (message_id, user_id, comment, created_at, updated_at) VALUES (:message_id, :user_id, :comment, NOW(), NOW())"
    data = {"message_id": request.form['messageid'], "user_id": session['userid'], "comment": request.form['comment']}
    commentid = mysql.query_db(insert_query, data)
    print "got comment inserted", commentid

    return redirect('/success')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
















app.run(debug = True)
