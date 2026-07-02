# 🏥 Doctor Appointment Booking System

A full-stack web application built with **Flask** and **MySQL** that allows patients to book doctor appointments, doctors to manage their schedules, and admins to oversee the entire system.

## 🚀 Live Features

- **Patient** — Register, search doctors by name/specialization, book appointments, cancel bookings
- **Doctor** — View all appointments, confirm/complete/cancel patient bookings
- **Admin** — Full control over users, doctors, patients, and all appointments

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Blueprints |
| Database | MySQL, Flask-MySQLdb |
| Frontend | HTML5, Bootstrap 5, Jinja2 |
| Auth | Session-based, Werkzeug password hashing |
| Tools | Git, VS Code |

## ⚙️ Key Technical Highlights

- **Role-based access control** — 3 separate dashboards (Patient, Doctor, Admin)
- **Slot conflict detection** — prevents double-booking the same doctor at the same time
- **Normalized MySQL schema** — 5 tables with proper foreign key relationships
- **Session-based authentication** — secure login with hashed passwords (Werkzeug)
- **Real appointment lifecycle** — Pending → Confirmed → Completed / Cancelled

## 🗄️ Database Schema
