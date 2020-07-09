from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api
# from flask_jwt_extended import JWTManager
# from flask_jwt import JWT, jwt_required, current_identity
# from flask_script import Manager

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Oluranti08056965@localhost:3306/ecommerce"
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'lk2k2kll3k4kl'

db = SQLAlchemy(app)
api = Api(app)
# jwt = JWTManager(app)
# jwt = JWT(app, authenticate, identity)

migrate = Migrate(app, db)


@app.before_first_request
def create_tables():
    db.create_all()