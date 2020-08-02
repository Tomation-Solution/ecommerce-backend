import random
import os
from flask_restful import Resource, reqparse
from flask import request, g, abort
from marshmallow import ValidationError
from sqlalchemy import text
from status import *
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from models import *
from config import mail
from flask_mail import Message
from helper import send_mail, ALLOWED_EXTENSIONS
from dbschema import *

# api to handle customer related activities
auth = HTTPTokenAuth(scheme='Bearer')


@auth.verify_token
def verify_token(token):
    # first try to authenticate by token
    try:
        # checks if the user is a verified customer
        user = Customers.verify_auth_token(token)
    except KeyError:
        # if not customer, checks if the user is a vendor
        user = Vendor.verify_auth_token(token)
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
                send_mail("Welcome to Our pharmaceutic e-commerce platform",
                          data['email'], email=data['email'], password=data['password'])
                c.save_to_db()
                user = Customers.query.filter_by(email=data['email']).first()
                access_token = user.generate_auth_token()
                return {
                    'message': 'User {} was created'.format(data['email']),
                    'access_token': access_token.decode(),
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
            "data": [CustomersSchema(exclude=('password',)).dump(c) for c in Customers.query.all()]
        }

    def patch(self):
        data = request.json
        data = CustomersSchema(
            exclude=('customer_id', 'date_created')).dump(data)
        Customers.query.filter_by(email=data['email']).update({
            Customers.firstname: data['firstname'],
            Customers.lastname: data['lastname'],
            Customers.email: data['email'],
            Customers.phone_number: data['phone_number'],
            Customers.password: Customers.generate_hash(data['password'])
        })
        db.session.commit()
        return {"status": "success", "data": "profile updated successfully"}, HTTP_200_OK


class CustomerOrders(AuthRequiredResources):
    # customer post a new order
    def post(self):
        # get the list of orders->product_id, quantity,cost
        data = request.json

        # check if data is valid
        try:
            filter = OrdersSchema(
                only=('orders', 'address_id', 'paymenttype_id'))
            result = filter.load(data)
        except ValidationError as err:
            err.messages['status'] = 'error'
            return err.messages, HTTP_400_BAD_REQUEST

        # check if quantity of product demanded each does not exceed available stock in database
        orderlist = result['orders']
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
                return {"status": "error", "data": "quantity ordered for product {} less than available".format(pid)}, HTTP_400_BAD_REQUEST
                break
        # decrement stock quantity by quantity demanded
        # update the stock quantity in the product
        for o in orderlist:
            pid = o['product_id']
            demanded_qty = o['quantity']
            pd = Products.query.get_or_404(pid)
            Products.query.filter_by(product_id=pid).update(
                {Products.stock_quantity: pd.stock_quantity - demanded_qty})
        db.session.commit()
        # aggregate the total cost and total quantity
        total_cost = total_quantity = 0
        for o in orderlist:
            total_cost += o['cost']
            total_quantity += o['quantity']
        # store the aggregates in the order table
        the_order = Orders(total_quantity=total_quantity,
                           total_price=total_cost, customer_id=g.user.customer_id, address_id=result['address_id'], paymenttype_id=result['paymenttype_id'])
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
        response['address'] = the_order.address.full_address
        response['paymenttype'] = the_order.paymentType.payment_type
        body = "Your order with order id {} has been recieved, ensure to login to monitor your order status".format(
            the_order.order_id)
        send_mail("MAIL ORDER RECIEVED", recipient=g.user.email, body=body)
        return response, HTTP_201_CREATED

    # customer gets all his orders
    def get(self):
        orders = Orders.query.filter_by(
            customer_id=g.user.customer_id).order_by(Orders.date_ordered).all()
        filter = OrdersSchema(exclude=("orders",))
        return {
            "status": "success",
            "data": [filter.dump(o) for o in orders]
        }, HTTP_200_OK


class CustomerOrder(AuthRequiredResources):
    # customer cancels a specific order
    def patch(self, order_id):
        try:
            order = Orders.query.get_or_404(order_id)
        except:
            return {"status": "error", "data": "No Order with such id"}, HTTP_404_NOT_FOUND
        result = OrdersSchema().dump(request.json)
        Orders.query.filter_by(order_id=order_id).update({
            Orders.total_price: result.get('total_price') or order.total_price,
            Orders.total_quantity: result.get('total_quantity') or order.total_price,
            Orders.paymenttype_id: result.get('paymenttype_id') or order.paymenttype_id,
            Orders.address_id: result.get('address_id') or order.address_id,
            Orders.status: result.get('status') or order.status,
            Orders.paid: result.get('paid') or order.paid,
            Orders.transaction_id: result.get('transaction_id') or order.transaction_id,
            Orders.transaction_reference: result.get('transaction_reference') or order.transaction_reference
            })
        db.session.commit()
        response = OrdersSchema().dump(order)
        return {"status": "success",
        "data":response
        }, HTTP_200_OK

    # customer fetch a specific order
    def get(self, order_id):
        try:
            order = Orders.query.get_or_404(order_id)
        except:
            return {"status": "error", "data": "No Order with such id"}, HTTP_404_NOT_FOUND
        # get all individual products of the order
        orderdetails = OrderDetails.query.filter_by(order_id=order_id).all()
        # convert them to python format->dict
        orderdetails = OrderSchema(many=True).dump(orderdetails)
        # convert the order to dict
        d_order = OrdersSchema().dump(order)
        # add the order details to order
        d_order['address'] = order.address.full_address
        d_order['payment_type'] = order.paymentType.payment_type 
        d_order["orders"] = orderdetails
        return {
            "status": "success",
            "data": d_order
        }

    def delete(self, order_id):
        try:
            order = Orders.query.get_or_404(order_id)
        except:
            return {"status": "error", "data": "No Order with such id"}, HTTP_404_NOT_FOUND
        result = Orders.query.filter_by(order_id=order_id).first()
        db.session.delete(result)
        db.session.commit()
        return {"status": "success", "data": "order with id {} deleted".format(order_id)}, HTTP_204_NO_CONTENT


# api to work with individual customers
class Customer(AuthRequiredResources):
    def get(self, customer_id):
        try:
            customer = Customers.query.get_or_404(customer_id)
        except:
            return {"status": "error", "data": "No customer with such id found"}, HTTP_404_NOT_FOUND
        result = CustomersSchema(exclude=('password',)).dump(customer)
        return {"status": "success", "data": result}, HTTP_200_OK


# api to handle vendor relative activities
class VendorRegistration(Resource):

    def post(self):
        # get incoming data
        data = dict(request.form)
        vendor_lg = request.files.get('vendor_logo')
        # check if vendor uploaded a logo and if its an accepted image
        if vendor_lg.filename == '':
            return {"status": "error", "data": "vendor image is required"}, HTTP_400_BAD_REQUEST
        vendor_lg = request.files['vendor_logo']
        if vendor_lg.filename.rsplit('.')[1] not in ALLOWED_EXTENSIONS:
            return {"status": "error", "data": "this file type is not allowed"}, HTTP_400_BAD_REQUEST
        data['vendor_logo'] = vendor_lg.filename
        # check if data is valid
        try:
            result = VendorSchema(
                exclude=("vendor_id", "date_created")).load(data)
        except ValidationError as err:
            err.messages['status'] = 'error'
            return err.messages, HTTP_400_BAD_REQUEST

        # check if email already exists
        if Vendor.find_by_username(result['email']):
            return {'status': 'error',
                    'data': 'User {} already exists'. format(data['email'])
                    }, HTTP_400_BAD_REQUEST
        else:
            v = Vendor(
                name=result['name'],
                vendor_logo=result['vendor_logo'],
                email=result['email'],
                account_number=result["account_number"],
                account_name=result["account_name"],
                phone_number=result['phone_number'],
                password=Vendor.generate_hash(result['password']),
                bank=result['bank'],
                full_address=result['full_address']
            )
            try:
                v.save_to_db()
                vendor_lg.save(app.config['UPLOAD_FOLDER']+vendor_lg.filename)
                send_mail("Welcome to Our pharmaceutic e-commerce platform",
                          data['email'], email=data['email'], password=data['password'])
                v = Vendor.query.filter_by(email=data['email']).first()
                access_token = v.generate_auth_token()
                return {
                    'message': 'User {} was created'.format(data['email']),
                    'access_token': access_token.decode(),
                    'name': result['name'],
                    'vendor_id': v.vendor_id
                }, HTTP_201_CREATED
            except:
                db.session.rollback()
                return {'message': 'Something went wrong'}, 500


class VendorLogin(Resource):
    def post(self):
        # get incoming data
        data = request.json

        # check if data is valid
        try:
            result = VendorSchema(only=("email", "password")).load(data)
        except ValidationError as err:
            err.messages['status'] = 'error'
            return err.messages, HTTP_400_BAD_REQUEST

        # check if email already exists
        vendor = Vendor.find_by_username(data['email'])
        if vendor and Vendor.verify_hash(data['password'], vendor.password):
            access_token = vendor.generate_auth_token()
            return {
                'access_token': access_token.decode(),
                'firstname': vendor.name,
                'vendor_id': vendor.vendor_id,
                "vendor_logo": vendor.vendor_logo
            }
        else:
            return {'status': 'error',
                    'data': "username or password is incorrect"
                    }, HTTP_400_BAD_REQUEST


# api to handle product related activities
class AllProducts(Resource):
    def get(self):
        # check if request parameter is empty, returns all products
        if request.args == {}:
            # return all products
            result = ProductsSchema(many=True).dump(Products.query.all())
            return {"status": "success", "data": result}, HTTP_200_OK
        # return products based on categories
        elif 'category' in request.args:
            # return based on category
            name = request.args.get('category')
            # gets the category from the db
            cat = Categories.query.filter_by(category_name=name).first()
            # returns all products for a category
            result = cat.product
            response = ProductsSchema(many=True).dump(result)
            return {"status": "success", "data": response}, HTTP_200_OK
        # return products based on type
        elif 'type' in request.args:
            # gets the type specified in the request parameters
            requested_type = request.args.get('type')
            if requested_type == 'mostviewed':
                result = SalesViewHistory.query.order_by(
                    SalesViewHistory.total_views.desc()).limit(6)
                response = [ProductsSchema().dump(r.product) for r in result]
                return {"status": "success", "data": response}, HTTP_200_OK
            elif requested_type == 'bestsellers':
                result = SalesViewHistory.query.order_by(
                    SalesViewHistory.total_sales.desc()).limit(6)
                response = [ProductsSchema().dump(r.product) for r in result]
                return {"status": "success", "data": response}, HTTP_200_OK
        # return products based on search
        elif 'search' in request.args:
            search = request.args.get('search')
            sql = text("select * from Products where product_name like :name").params(
                {'name': '%{}%'.format(search)})

            result = db.session.query(Products).from_statement(sql).all()
            response = ProductsSchema(many=True).dump(result)
            return {"status": "success", "data": response}, HTTP_200_OK
        else:
            return {"status": "error", "data": "Invalid request"}, HTTP_400_BAD_REQUEST

    @auth.login_required
    def post(self):
        # check if user is a vendor
        try:
            id = g.user.vendor_id
        except AttributeError as e:
            return {"status": "error", "data": "unauthorized"}, HTTP_401_UNAUTHORIZED
        # gets an immutable dict of all fields in the form
        data = request.form
        # gets the file uploaded as product image
        datafile = request.files.get('product_image')
        # check if file exists and process the request
        if datafile.filename != '':
            data = dict(data)
            data['product_image'] = datafile.filename
            # validate the incoming data to ensure its correct
            data = ProductsSchema(
                exclude=('product_id', 'date_created')).dump(data)
            try:
                p = Products(product_name=data['product_name'], product_image=data['product_image'], description=data['description'],
                             category_id=data['category_id'], manufacturer=data['manufacturer'], stock_quantity=data['stock_quantity'], price=data['price'])
            except KeyError as error:
                return {"status": "error", "data": "one or more field missing"}, HTTP_400_BAD_REQUEST
                abort(400)
            db.session.add(p)
            db.session.commit()
            datafile.save(app.config['UPLOAD_FOLDER']+datafile.filename)
            return {"status": "success", "data": ProductsSchema().dump(p)}, HTTP_200_OK
        return {"status": "error", "data": "no image selected"}, HTTP_400_BAD_REQUEST


class Product(Resource):
    def get(self, product_id):
        try:
            result = Products.query.get_or_404(product_id)
        except:
            return {"status": "error", "data": "No product with such id"}
        # update the view history
        new_total_views = result.salesviewhistory[0].total_views + 1
        SalesViewHistory.query.filter_by(product_id=product_id).update({
            salesviewhistory.total_views: new_total_views
        })
        db.session.commit()
        # get the required product and return a response
        response = ProductsSchema().dump(result)
        response['total_views'] = result.salesviewhistory[0].total_views
        response['total_sales'] = result.salesviewhistory[0].total_sales
        return {"status": "error", "data": response}

    @auth.login_required
    def patch(self, product_id):
        try:
            id = g.user.vendor_id
        except:
            return {"status": "error", "data": "unauthorized"}, HTTP_401_UNAUTHORIZED
        data = dict(request.form)
        # fetch the product from the table, return error if not
        try:
            initial_product = Products.query.get_or_404(product_id)
        except:
            return {"status": "error", "data": "No product with id {}".format(product_id)}, HTTP_404_NOT_FOUND

        # check if file exists
        datafile = request.files.get('product_image')
        if datafile.filename == '':
            return {"status": "error", "data": "no image selected"}, HTTP_400_BAD_REQUEST
        # update the product in the table
        product_name = data['product_name']
        category_id = data['category_id']
        description = data['description']
        manufacturer = data['manufacturer']
        product_image = datafile.filename
        stock_quantity = data['stock_quantity']
        price = data['price']
        Products.query.filter_by(product_id=product_id).update({
            Products.product_name: product_name,
            Products.category_id: category_id,
            Products.description: description,
            Products.stock_quantity: stock_quantity,
            Products.manufacturer: manufacturer,
            Products.price: price,
            Products.product_image: product_image
        })
        db.session.commit()
        datafile.save(app.config['UPLOAD_FOLDER']+datafile.filename)
        os.remove(app.config['UPLOAD_FOLDER']+initial_product.product_image)
        response = Products.query.get(product_id)
        response = ProductsSchema().dump(response)
        return {"status": "success", "data": response}, HTTP_200_OK

# api to handle orders related activities by vendor


class AllOrders(AuthRequiredResources):
    def get(self):
        try:
            id = g.user.vendor_id
        except:
            return {"status": "error", "data": "unauthorized user"}, HTTP_401_UNAUTHORIZED
        result = Orders.query.all()
        result = OrdersSchema().dump(result)
        return {"status": "success", "data": result}

# api to handle category related activities


class AllCategories(Resource):
    def get(self):
        result = Categories.query.all()
        response = CategoriesSchema(many=True).dump(result)
        return {"status": "success", "data": response}, HTTP_200_OK

    def post(self):
        data = request.json
        data = CategoriesSchema(only=('category_name',)).dump(data)
        c = Categories(category_name=data['category_name'])
        db.session.add(c)
        db.session.commit()
        response = CategoriesSchema().dump(c)
        return {"status": "success", "data": response}, HTTP_201_CREATED


class Category(Resource):
    def get(self, category_id):
        try:
            theCategory = Categories.query.get_or_404(category_id)
        except:
            return {"status": "error", "data": "resource not found"}, HTTP_404_NOT_FOUND
        response = CategoriesSchema().dump(theCategory)
        return {"status": "success", "data": response}, HTTP_200_OK

    def patch(self, category_id):
        try:
            theCategory = Categories.query.get_or_404(category_id)
        except:
            return {"status": "error", "data": "resource not found"}, HTTP_404_NOT_FOUND
        data = CategoriesSchema(
            exclude=('date_created', 'category_id')).dump(request.json)
        Categories.query.filter_by(category_id=category_id).update({
            Categories.category_name: data['category_name']
        })
        db.session.commit()
        response = CategoriesSchema().dump(theCategory)
        return {"status": "success", "data": response}, HTTP_200_OK


class PaymentTypes(Resource):
    def get(self, paymenttype_id):
        try:
            thetype = PaymentType.query.get_or_404(paymenttype_id)
        except:
            return {"status": "error", "data": "resource not found"}, HTTP_404_NOT_FOUND
        response = PaymentTypeSchema().dump(thetype)
        return {"status": "success", "data": response}, HTTP_200_OK

    def patch(self, paymenttype_id):
        try:
            thetype = PaymentType.query.get_or_404(paymenttype_id)
        except:
            return {"status": "error", "data": "resource not found"}, HTTP_404_NOT_FOUND
        data = PaymentTypeSchema().dump(request.json)
        PaymentType.query.filter_by(paymenttype_id=paymenttype_id).update({
            PaymentType.payment_type: data['payment_type']
        })
        db.session.commit()
        response = PaymentTypeSchema().dump(thetype)
        return {"status": "success", "data": response}, HTTP_200_OK


class AllPaymentTypes(Resource):
    def post(self):
        data = PaymentTypeSchema(
            exclude=('paymenttype_id',)).dump(request.json)
        p = PaymentType(payment_type=data['payment_type'])
        db.session.add(p)
        db.session.commit()
        response = PaymentTypeSchema().dump(p)
        return {"status": "success", "data": response}, HTTP_201_CREATED

    def get(self):
        alltype = PaymentType.query.all()
        response = PaymentTypeSchema(many=True).dump(alltype)
        return {"status": "success", "data": response}, HTTP_200_OK


class addresses(AuthRequiredResources):
    # add a new address
    def post(self):
        data = AddressSchema(exclude=('address_id','date_created')).dump(request.json)
        result = Address(customer_id=g.user.customer_id,full_address=data['full_address'])
        db.session.add(result)
        db.session.commit()
        return {"status":"success","data":AddressSchema().dump(result)}, HTTP_201_CREATED

    # get all addresses for a user
    def get(self):
        result = Address.query.all()
        response = AddressSchema(many=True).dump(result)
        return {"status":"success","data":response},HTTP_200_OK


class address(AuthRequiredResources):
    # get a single address
    def get(self,address_id):
        try:
            result = Address.query.get_or_404(address_id)
        except:
            return {"status":"error","data":"address with id {} does not exists".format(address_id)},HTTP_404_NOT_FOUND
        response = AddressSchema().dump(result)
        return {"status":"error", "data":response}, HTTP_200_OK

    def patch(self,address_id):
        try:
            result = Address.query.get_or_404(address_id)
        except:
            return {"status":"error","data":"address with id {} does not exists".format(address_id)},HTTP_404_NOT_FOUND
        data = AddressSchema().dump(request.json)
        Address.query.filter_by(address_id=address_id).update({
            Address.customer_id: g.user.customer_id,
            Address.full_address:data['full_address']
        })
        db.session.commit()
        response = Address.query.get(address_id)
        response = AddressSchema().dump(response)
        return {"status":"success","data":response}

    def delete(self):
        pass


class RequestPasswordChange(Resource):
    # checks db if the user requesting password change exists and send a mail containing the url to change pwd
    def post(self):
        data = request.json
        result = Customers.query.filter_by(email=data['email']).first()
        if not result:
            return {"status": "error", "data": "use does not exist"}
        token = result.generate_auth_token()
        change_password_url = "{}/changepassword/{}".format(
            os.environ['HOST'], token.decode())
        send_mail('PASSWORD CHANGE REQUEST', result.email,
                  "click on the this link to change password {}".format(change_password_url))
        return {"status": "success", 'data': change_password_url}, HTTP_200_OK


# get the detail of the user trying to change password using the token supplied
class Password(Resource):
    def get(self, token):
        user = Customers.verify_auth_token(token)
        result = CustomersSchema(exclude=('password',)).dump(user)
        return {"status": "success", "data": result}, HTTP_200_OK
