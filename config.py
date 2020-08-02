from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api
from flask_mail import Mail
from dotenv import load_dotenv
from flask_whooshee import Whooshee
import os


app = Flask(__name__)

UPLOAD_FOLDER = os.curdir + os.path.sep + 'static/'
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Oluranti08056965@localhost:3306/ecommerce"
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = os.environ['MAIL_DEFAULT_SENDER']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = SQLAlchemy(app)
api = Api(app)
mail = Mail(app)
migrate = Migrate(app, db)
whooshee = Whooshee(app)
whooshee.reindex()

@app.before_first_request
def create_tables():
    db.create_all()
