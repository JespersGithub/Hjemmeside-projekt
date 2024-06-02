from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from functools import wraps
import logging


app = Flask(__name__)
app.secret_key = 'supersecretkey'


logging.basicConfig(filename='error.log', level=logging.DEBUG)


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Password1234",
            database="aagejensen"
        )
        return conn
    except mysql.connector.Error as err:
        app.logger.error("Database connection error: %s", err)
        return None

@app.errorhandler(500)
def internal_error(error):
    app.logger.error('Server Error: %s', error)
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', (e))
    return render_template('500.html'), 500

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
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql = "INSERT INTO contact_form (email, phone, name, message) VALUES (%s, %s, %s, %s)"
                val = (email, phone, name, message)
                cursor.execute(sql, val)
                conn.commit()
                return redirect(url_for('thank_you'))
            except mysql.connector.Error as err:
                app.logger.error("Error inserting data: %s", err)
                flash('Der opstod en fejl ved indsættelse af data.')
            finally:
                cursor.close()
                conn.close()
        else:
            flash('Databaseforbindelse mislykkedes.')

    return render_template('kontakt.html')

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/fjernvarme')
def fjernvarme():
    return render_template('fjernvarme.html')

@app.route('/nyt-badevaerelse')
def nyt-badevaerelse():
    return render_template('nyt_badevaerelse.html')

@app.route('/blikkenslager')
def blikkenslager():
    return render_template('blikkenslager.html')

@app.route('/varmepumpe')
def varmepumpe():
    return render_template('varmepumpe.html')

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
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM contact_form")
            data = cursor.fetchall()
            return render_template('admin.html', data=data)
        except mysql.connector.Error as err:
            app.logger.error("Error fetching data: %s", err)
            flash('Der opstod en fejl ved hentning af data.')
        finally:
            cursor.close()
            conn.close()
    else:
        flash('Databaseforbindelse mislykkedes.')
    return render_template('admin.html')

@app.route('/wipe_database', methods=['POST'])
@login_required
def wipe_database():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM contact_form")
            conn.commit()
            flash('Databasen er blevet ryddet.')
        except mysql.connector.Error as err:
            app.logger.error("Error wiping database: %s", err)
            flash('Der opstod en fejl ved sletning af databasen.')
        finally:
            cursor.close()
            conn.close()
    else:
        flash('Databaseforbindelse mislykkedes.')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
