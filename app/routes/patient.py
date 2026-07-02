from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app import mysql

patient = Blueprint('patient', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@patient.route('/patient/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    
    # Get upcoming appointments
    cur.execute("""
        SELECT a.id, u.name, d.specialization, a.appointment_date, 
               a.appointment_time, a.status
        FROM appointments a
        JOIN users u ON a.doctor_id = u.id
        JOIN doctors d ON a.doctor_id = d.user_id
        WHERE a.patient_id = %s AND a.status != 'cancelled'
        ORDER BY a.appointment_date ASC
    """, (session['user_id'],))
    appointments = cur.fetchall()
    cur.close()
    
    return render_template('patient/dashboard.html', 
                         appointments=appointments,
                         name=session['user_name'])

@patient.route('/patient/search', methods=['GET', 'POST'])
@login_required
def search_doctors():
    doctors = []
    specializations = []
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT specialization FROM doctors")
    specializations = [row[0] for row in cur.fetchall()]
    
    search = request.args.get('search', '')
    specialization = request.args.get('specialization', '')
    
    query = """
        SELECT u.id, u.name, d.specialization, d.fee, d.experience_years, d.bio
        FROM users u
        JOIN doctors d ON u.id = d.user_id
        WHERE u.role = 'doctor'
    """
    params = []
    
    if search:
        query += " AND u.name LIKE %s"
        params.append(f'%{search}%')
    if specialization:
        query += " AND d.specialization = %s"
        params.append(specialization)
    
    cur.execute(query, params)
    doctors = cur.fetchall()
    cur.close()
    
    return render_template('patient/search.html',
                         doctors=doctors,
                         specializations=specializations,
                         search=search,
                         specialization=specialization)
    
    
@patient.route('/patient/book/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book_appointment(doctor_id):
    cur = mysql.connection.cursor()
    
    # Get doctor details
    cur.execute("""
        SELECT u.name, d.specialization, d.fee, d.experience_years
        FROM users u
        JOIN doctors d ON u.id = d.user_id
        WHERE u.id = %s
    """, (doctor_id,))
    doctor = cur.fetchone()
    
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        notes = request.form.get('notes', '')
        
        # Conflict detection — check if slot already booked
        cur.execute("""
            SELECT id FROM appointments 
            WHERE doctor_id = %s 
            AND appointment_date = %s 
            AND appointment_time = %s
            AND status != 'cancelled'
        """, (doctor_id, date, time))
        
        existing = cur.fetchone()
        
        if existing:
            flash('This slot is already booked. Please choose a different time.', 'danger')
        else:
            cur.execute("""
                INSERT INTO appointments 
                (patient_id, doctor_id, appointment_date, appointment_time, notes, status)
                VALUES (%s, %s, %s, %s, %s, 'pending')
            """, (session['user_id'], doctor_id, date, time, notes))
            mysql.connection.commit()
            flash('Appointment booked successfully!', 'success')
            cur.close()
            return redirect(url_for('patient.dashboard'))
    
    cur.close()
    return render_template('patient/book.html', doctor=doctor, doctor_id=doctor_id)

@patient.route('/patient/cancel/<int:appointment_id>')
@login_required
def cancel_appointment(appointment_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE appointments SET status = 'cancelled'
        WHERE id = %s AND patient_id = %s
    """, (appointment_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash('Appointment cancelled.', 'info')
    return redirect(url_for('patient.dashboard'))