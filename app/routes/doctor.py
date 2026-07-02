from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app import mysql

doctor = Blueprint('doctor', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@doctor.route('/doctor/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()

    # Get all appointments for this doctor
    cur.execute("""
        SELECT a.id, u.name, a.appointment_date, 
               a.appointment_time, a.status, a.notes
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        WHERE a.doctor_id = %s
        ORDER BY a.appointment_date ASC
    """, (session['user_id'],))
    appointments = cur.fetchall()

    # Stats
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
        FROM appointments WHERE doctor_id = %s
    """, (session['user_id'],))
    stats = cur.fetchone()
    cur.close()

    return render_template('doctor/dashboard.html',
                         appointments=appointments,
                         stats=stats,
                         name=session['user_name'])

@doctor.route('/doctor/update/<int:appointment_id>/<status>')
@login_required
def update_status(appointment_id, status):
    if status not in ['confirmed', 'completed', 'cancelled']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('doctor.dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE appointments SET status = %s
        WHERE id = %s AND doctor_id = %s
    """, (status, appointment_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash(f'Appointment marked as {status}.', 'success')
    return redirect(url_for('doctor.dashboard'))