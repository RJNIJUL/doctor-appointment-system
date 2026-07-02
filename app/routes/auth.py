from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app import mysql
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)
@auth.route('/')
def home():
    if 'user_id' in session:
        if session['user_role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif session['user_role'] == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        else:
            return redirect(url_for('patient.dashboard'))
    return render_template('home.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                       (name, email, hashed_password, role))
            mysql.connection.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except:
            flash('Email already exists. Try another.', 'danger')
        finally:
            cur.close()
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_role'] = user[4]
            if user[4] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user[4] == 'doctor':
                return redirect(url_for('doctor.dashboard'))
            else:
                return redirect(url_for('patient.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/create-admin')
def create_admin():
    from werkzeug.security import generate_password_hash
    cur = mysql.connection.cursor()
    hashed = generate_password_hash('admin123')
    cur.execute("UPDATE users SET password = %s WHERE email = 'admin@docbook.com'", (hashed,))
    mysql.connection.commit()
    cur.close()
    return 'Admin password hashed! You can delete this route now.'

