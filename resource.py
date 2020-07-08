from flask_restful import Resource, reqparse
from flask import request, g
from marshmallow import ValidationError
from status import *
from flask_httpauth import HTTPBasicAuth,HTTPTokenAuth
from models import Customers
from dbschema import CustomersSchema,OrdersSchema

# api to handle customer related activities
auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    #first try to authenticate by token
    print(type(token))
    user = Customers.verify_auth_token(token)
    if not user:
        return False
    g.user = user
    return True

class AuthRequiredResources(Resource):
    method_decorators = [auth.login_required]
class CustomerRegistration(Resource):
    def post(self):
        # get incoming data
        data = request.json

        # check if data is valid
        try:
            result = CustomersSchema(exclude=("customer_id","date_created")).load(data)
        except ValidationError as err:
            err.messages['status'] = 'error'
            return err.messages, HTTP_400_BAD_REQUEST

        # check if email already exists
        if Customers.find_by_username(data['email']):
            return {'status': 'error',
                    'data': 'User {} already exists'. format(data['email'])
                    }, HTTP_400_BAD_REQUEST
        else:

            c = Customers(
                firstname=data['firstname'],
                lastname=data['lastname'],
                email=data['email'],
                phone_number=data['phone_number'],
                password=Customers.generate_hash(data['password'])
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
                    'customer_id': user.customer_id
                }, HTTP_201_CREATED
            except:
                db.session.rollback()
                return {'message': 'Something went wrong'}, 500


class CustomerLogin(Resource):
    def post(self):
        # get incoming data
        data = request.json

        # check if data is valid
        try:
            result = CustomersSchema(only=('email', 'password')).load(data)
        except ValidationError as err:
            err.messages['status'] = 'error'
            return err.messages, HTTP_400_BAD_REQUEST

        # check if email already exists
        user = Customers.find_by_username(data['email'])
        print('one user found', user)
        if user and Customers.verify_hash(data['password'], user.password):
            access_token = user.generate_auth_token()
            return {
                'access_token': access_token.decode(),
                'firstname': user.firstname,
                'lastname': user.lastname,
                'customer_id': user.customer_id
            }
        else:
            return {'status': 'error',
                    'data': "username or password is incorrect"
                    }, HTTP_400_BAD_REQUEST


class AllCustomers(Resource):
    def get(self):
        return {
            "status":"success",
            "data":[CustomersSchema().dump(c) for c in Customers.query.all()]
        }


class CustomerOrders(AuthRequiredResources):
    def post(self, customer_id):
       #get the list of orders->product_id, quantity,cost
       
       #aggregate the total cost and total quantity
       #store the aggregates in the order table
       #store the individual order in orderdetails table
       #return full details of the stored order
       pass

    def get(self):
        orders = g.user.order
        return {
            "status":"success",
            "data":[OrdersSchema().dump(o) for o in orders]
        }, HTTP_200_OK
    
    def delete(self):
        pass

    def patch(self):
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
