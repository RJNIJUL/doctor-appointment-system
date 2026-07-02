from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app import mysql

admin = Blueprint('admin', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'danger')
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin.route('/admin/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()

    # Overall stats
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'patient'")
    total_patients = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor'")
    total_doctors = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM appointments WHERE status = 'pending'")
    pending_appointments = cur.fetchone()[0]

    # All appointments
    cur.execute("""
        SELECT a.id, p.name, d.name, a.appointment_date, 
               a.appointment_time, a.status
        FROM appointments a
        JOIN users p ON a.patient_id = p.id
        JOIN users d ON a.doctor_id = d.id
        ORDER BY a.appointment_date DESC
    """)
    appointments = cur.fetchall()

    # All doctors
    cur.execute("""
        SELECT u.id, u.name, u.email, d.specialization, d.fee
        FROM users u
        JOIN doctors d ON u.id = d.user_id
        WHERE u.role = 'doctor'
    """)
    doctors = cur.fetchall()

    # All patients
    cur.execute("""
        SELECT id, name, email, created_at 
        FROM users WHERE role = 'patient'
    """)
    patients = cur.fetchall()

    cur.close()

    return render_template('admin/dashboard.html',
                         total_patients=total_patients,
                         total_doctors=total_doctors,
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         appointments=appointments,
                         doctors=doctors,
                         patients=patients,
                         name=session['user_name'])

@admin.route('/admin/delete/user/<int:user_id>')
@login_required
def delete_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM appointments WHERE patient_id = %s OR doctor_id = %s", 
                (user_id, user_id))
    cur.execute("DELETE FROM doctors WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/admin/update/appointment/<int:appointment_id>/<status>')
@login_required
def update_appointment(appointment_id, status):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE appointments SET status = %s WHERE id = %s", 
                (status, appointment_id))
    mysql.connection.commit()
    cur.close()
    flash(f'Appointment updated to {status}.', 'success')
    return redirect(url_for('admin.dashboard'))