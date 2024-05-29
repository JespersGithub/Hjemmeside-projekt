from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Password1234",
    database="aagejensen"
)
cursor = db.cursor()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/kontakt', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']
        name = request.form['name']
        message = request.form['message']

        sql = "INSERT INTO contact_form (email, phone, name, message) VALUES (%s, %s, %s, %s)"
        val = (email, phone, name, message)
        cursor.execute(sql, val)
        db.commit()

        return redirect(url_for('thank_you'))

    return render_template('kontakt.html')

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/fjernvarme')
def fjernvarme():
    return render_template('fjernvarme.html')

@app.route('/nyt-badevaerelse')
def nyt_badevaerelse():
    return render_template('nyt_badevaerelse.html')

@app.route('/blikkenslager')
def blikkenslager():
    return render_template('blikkenslager.html')

@app.route('/varmepumpe')
def varmepumpe():
    return render_template('varmepumpe.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'adminpassword':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Forkerte oplysninger. Prøv igen.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin():
    cursor.execute("SELECT * FROM contact_form")
    data = cursor.fetchall()
    return render_template('admin.html', data=data)

@app.route('/wipe_database', methods=['POST'])
@login_required
def wipe_database():
    cursor.execute("DELETE FROM contact_form")
    db.commit()
    flash('Databasen er blevet ryddet.')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
