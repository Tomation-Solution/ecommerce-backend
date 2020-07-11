from flask_restful import Resource, reqparse
from flask import request, g, abort
from marshmallow import ValidationError
from status import *
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from models import *
from config import mail
from flask_mail import Message
from helper import send_mail
from dbschema import CustomersSchema, OrdersSchema, OrderSchema, OrderList

# api to handle customer related activities
auth = HTTPTokenAuth(scheme='Bearer')


@auth.verify_token
def verify_token(token):
    # first try to authenticate by token
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
            result = CustomersSchema(
                exclude=("customer_id", "date_created")).load(data)
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
                send_mail("Welcome to Our pharmaceutic e-commerce platform",recipient=data['email'],email=data['email'],password=data['password'])
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


class AllCustomers(AuthRequiredResources):
    def get(self):
        return {
            "status": "success",
            "data": [CustomersSchema().dump(c) for c in Customers.query.all()]
        }


class CustomerOrders(AuthRequiredResources):
    # customer post a new order
    def post(self):
        # get the list of orders->product_id, quantity,cost
        data = request.json

        # check if data is valid
        try:
            filter = OrdersSchema(only=('orders',))
            result = filter.load(data)
        except ValidationError as err:
            err.messages['status'] = 'error'
            return err.messages, HTTP_400_BAD_REQUEST

        # check if quantity of product demanded each does not exceed available stock in database
        orderlist = result['orders']
        print(orderlist)
        for o in orderlist:
            # fetch the individual product
            try:
                pid = o['product_id']
                pd = Products.query.get_or_404(pid)
            except:
                return {
                    "status": "error", 
                    "data": "Product with id {} not available".format(pid)}, HTTP_404_NOT_FOUND
                break
                abort(404)
            # check the quantity left against demanded
            if o['quantity'] > pd.stock_quantity:
                # return a message if anyone is more than the available
                return {"status":"error", "data":"quantity ordered for product {} less than available".format(pid)},HTTP_400_BAD_REQUEST
                break 

        #decrement stock quantity by quantity demanded
        # update the stock quantity in the product
        for o in orderlist:
            pid = o['product_id']
            demanded_qty = o['quantity']
            pd = Products.query.get_or_404(pid)
            Products.query.filter_by(product_id=pid).update({Products.stock_quantity:pd.stock_quantity - demanded_qty})
        db.session.commit()

        # aggregate the total cost and total quantity
        total_cost = total_quantity = 0
        for o in orderlist:
            total_cost += o['cost']
            total_quantity += o['quantity']
        # store the aggregates in the order table
        the_order = Orders(total_quantity=total_quantity,
                           total_price=total_cost, customer_id=g.user.customer_id)
        db.session.add(the_order)
        db.session.flush()

        # store the individual order in orderdetails table
        for order in orderlist:
            each_order = OrderDetails(
                order_id=the_order.order_id, product_id=order['product_id'], quantity=order['quantity'], cost=order['cost'])
            db.session.add(each_order)
        db.session.commit()

        # return full details of the stored order
        the_order = Orders.query.get(the_order.order_id)
        response = OrdersSchema().dump(the_order)
        body = "Your order with order id {} has been recieved, ensure to login to monitor your order status".format(the_order.order_id)
        send_mail("MAIL ORDER RECIEVED",recipient=g.user.email, body=body)
        return response, HTTP_201_CREATED

    # customer gets all his orders
    def get(self):
        orders = g.user.order
        filter = OrdersSchema(exclude=("orders",))
        return {
            "status": "success",
            "data": [filter.dump(o) for o in orders]
        }, HTTP_200_OK


class CustomerOrder(AuthRequiredResources):
    # customer cancels a specific order
    def delete(self, order_id):
        try:
            order = Orders.query.get_or_404(order_id)
        except:
            return {"status": "error", "data": "No Order with such id"}, HTTP_404_NOT_FOUND
        Orders.query.filter_by(order_id=order_id).update({Orders.status:'cancelled'})
        db.session.commit()
        return {"status": "success", "data": "order with id {} cancelled".format(order.order_id)}, HTTP_200_OK

    # customer fetch a specific order
    def get(self, order_id):
        try:
            order = Orders.query.get_or_404(order_id)
        except:
            return {"status": "error", "data": "No Order with such id"}, HTTP_404_NOT_FOUND
        orderdetails = OrderDetails.query.filter_by(order_id=order_id).all()
        orderdetails=OrderSchema(many=True).dump(orderdetails)
        order = OrdersSchema().dump(order)
        order["orders"] = orderdetails
        return {
            "status":"success",
            "data":order
        }


class Customer(Resource):
    pass


# api to handle vendor relative activities
class VendorRegistration(Resource):
   
    def post(self):
        # get incoming data
        data = request.json
        # check if data is valid
        try:
            result = CustomersSchema(
                exclude=("customer_id", "date_created")).load(data)
        except ValidationError as err:
            err.messages['status'] = 'error'
            return err.messages, HTTP_400_BAD_REQUEST

        # # check if email already exists
        # if Customers.find_by_username(data['email']):
        #     return {'status': 'error',
        #             'data': 'User {} already exists'. format(data['email'])
        #             }, HTTP_400_BAD_REQUEST
        # else:

            # c = Customers(
            #     firstname=data['firstname'],
            #     lastname=data['lastname'],
            #     email=data['email'],
            #     phone_number=data['phone_number'],
            #     password=Customers.generate_hash(data['password'])
            # )
            # try:
            #     c.save_to_db()
            #     user = Customers.query.filter_by(email=data['email']).first()
            #     access_token = create_access_token(identity=user.customer_id)
            #     send_mail("Welcome to Our pharmaceutic e-commerce platform",recipient=data['email'],email=data['email'],password=data['password'])
            #     return {
            #         'message': 'User {} was created'.format(data['email']),
            #         'access_token': access_token,
            #         'firstname': data['firstname'],
            #         'lastname': data['lastname'],
            #         'customer_id': user.customer_id
            #     }, HTTP_201_CREATED
            # except:
            #     db.session.rollback()
            #     return {'message': 'Something went wrong'}, 500


class VendorLogin(Resource):
    pass


# api to handle product related activities
class AllProducts(Resource):
    def get(self):
        pass


class Product(Resource):
    pass


# api to handle orders related activities by vendor
class AllOrders(Resource):
    pass

# api to handle order related activities by vendor
class Order(Resource):
    pass

# api to handle category related activities


class Categories(Resource):
    pass


class Category(Resource):
    pass
