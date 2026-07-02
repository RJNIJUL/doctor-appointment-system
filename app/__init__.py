from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    mysql.init_app(app)
    
    from app.routes.auth import auth
    from app.routes.patient import patient
    from app.routes.doctor import doctor
    from app.routes.admin import admin
    
    app.register_blueprint(auth)
    app.register_blueprint(patient)
    app.register_blueprint(doctor)
    app.register_blueprint(admin)
    
    return app