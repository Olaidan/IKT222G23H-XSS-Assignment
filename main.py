from flask import Flask, render_template, request, redirect, url_for, g, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = 'reviews.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT rating, review FROM reviews')
    reviews = cursor.fetchall()

    user_id = session.get('user_id')

    return render_template('index.html', reviews=reviews, user_id=user_id)


@app.route('/submit', methods=['POST'])
def submit_review():
    if request.method == 'POST':
        rating = request.form['rating']
        review_text = request.form['review_text']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO reviews (rating, review) VALUES (?, ?)", (rating, review_text))
        db.commit()

    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username and password:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                return "Username already exists. Please choose a different username."
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username and password:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                user_id = user[0]
                session['user_id'] = user_id
                return redirect(url_for('index'))
            else:
                return "Invalid login credentials. Please try again."

    return render_template('login.html')


@app.route('/fake_login', methods=['GET', 'POST'])
def fake_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
    return render_template('fake_login.html')


if __name__ == '__main__':
    app.run(debug=True)