from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api
from flask_mail import Mail
import os


app = Flask(__name__)

UPLOAD_FOLDER = os.curdir + os.path.sep + 'static/'

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Oluranti08056965@localhost:3306/ecommerce"
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'lk2k2kll3k4kl'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ceuticpharm@gmail.com'
app.config['MAIL_PASSWORD'] = 'pharm12345'
app.config['MAIL_DEFAULT_SENDER'] = 'ceuticpharm@gmail.com'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
api = Api(app)
mail = Mail(app)
migrate = Migrate(app, db)


@app.before_first_request
def create_tables():
    db.create_all()