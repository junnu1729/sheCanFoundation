from flask import Flask, render_template,request,redirect,url_for,session
import mysql.connector
import matplotlib.pyplot as plt
import os
app = Flask(__name__)
app.secret_key = 'Juned@2006'
UNIVERSAL_PASSCODE = "SHECAN2025"


# ✅ Correct database connection with user = 'junnu'
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='junnu',
        password='junnu@123',
        database='shecan_portal'
    )

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if user:
            session['email'] = user['email']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html',error="Invalid credentials.Please try again")
    
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password!=confirm_password:
            return render_template('register.html',error="password is not matching...")
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            connection.close()
            return render_template('register.html',error="Email already registered.Please login or use a different email.....")
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        connection.commit()
        
        cursor.close()
        connection.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT *, (total_amount - collected_amount) AS remaining FROM people")
    people = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', people=people)


    
@app.route('/verify/<name>', methods=['GET', 'POST'])
def verify(name):
    if request.method == 'POST':
        passcode = request.form['passcode']
        if passcode == UNIVERSAL_PASSCODE:
            return redirect(url_for('personal_profile', name=name))
        else:
            return render_template('verify.html', name=name, error="❌ Incorrect passcode.")
    
    return render_template('verify.html', name=name)

@app.route('/profile')
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Filter: Only fetch Juned's data
    cursor.execute("SELECT name, total_amount, collected_amount FROM people WHERE name = %s", ("Juned",))
    person = cursor.fetchone()

    if person:
        total = person['total_amount']
        collected = person['collected_amount']
        person['remaining'] = total - collected
        person['percent_collected'] = round((collected / total) * 100, 2) if total else 0
        person['percent_remaining'] = 100 - person['percent_collected']
    else:
        person = None

    # 👇 Fetch Juned's donation history
    cursor.execute("SELECT donor_name, amount, date, time FROM donations WHERE receiver_name = %s", ("Juned",))
    donations = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('profile.html', person=person, donations=donations)  # 👈 This line is the key


if __name__ == '__main__':
    app.run(debug=True)
