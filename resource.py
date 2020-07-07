from flask_restful import Resource, reqparse
from flask import request
from marshmallow import ValidationError
from status import *
from pprint import pprint
from models import *
from dbschema import CustomersSchema
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

# api to handle customer related activities
class CustomerRegistration(Resource):
    def post(self):
        # get incoming data
        data = request.json

        # check if data is valid
        try:
            result = CustomersSchema().load(data)
        except ValidationError as err:
            err.messages['status'] = 'error'
            return err.messages,HTTP_400_BAD_REQUEST

        #check if email already exists
        if Customers.find_by_username(data['email']):
            return {'status':'error',
            'data':'User {} already exists'. format(data['email'])
            }, HTTP_400_BAD_REQUEST
        else:

            c = Customers(
                firstname=data['firstname'],
                lastname = data['lastname'],
                email = data['email'],
                phone_number = data['phone_number'],
                password = Customers.generate_hash(data['password'])
            )
            try:
                c.save_to_db()
                user = Customers.query.filter_by(email=data['email']).first()
                access_token = create_access_token(identity=user.customer_id)
                return {
                    'message': 'User {} was created'.format(data['email']),
                    'access_token': access_token,
                    'firstname': data['firstname'],
                    'lastname': data['lastname'],
                    'customer_id':user.customer_id
                }
            except:
                db.session.rollback()
                return {'message': 'Something went wrong'}, 500
          

class CustomerLogin(Resource):
    def post(self):
        # get incoming data
        data = request.json

        # check if data is valid
        try:
            result = CustomersSchema(only=('email','password')).load(data)
        except ValidationError as err:
            err.messages['status'] = 'error'
            return err.messages,HTTP_400_BAD_REQUEST

        #check if email already exists
        user = Customers.find_by_username(data['email'])
        if user:
            access_token = create_access_token(identity=user.customer_id)
            return {
                    'access_token': access_token,
                    'firstname': data['firstname'],
                    'lastname': data['lastname'],
                    'customer_id':user.customer_id
                }
        else:
            return {'status':'error',
            'data':'User {} does not exists'. format(data['email'])
            }, HTTP_400_BAD_REQUEST

class AllCustomers(Resource):
    pass

class CustomerOrders(Resource):
    pass

class CustomerOrder(Resource):
    pass

class Customer(Resource):
    pass



# api to handle vendor relative activities
class VendorRegistration(Resource):
    pass

class VendorLogin(Resource):
    pass


# api to handle product related activities
class AllProducts(Resource):
    pass

class Product(Resource):
    pass


# api to handle orders related activities
class AllOrders(Resource):
    pass

class Order(Resource):
    pass

# api to handle category related activities
class Categories(Resource):
    pass

class Category(Resource):
    pass


