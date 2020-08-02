from dotenv import load_dotenv
from config import app, api
from flask import Flask,jsonify,request
import json
import resource

# customer registration route method:post
api.add_resource(resource.CustomerRegistration, '/customers/registration')
# customer login route method:post
api.add_resource(resource.CustomerLogin, '/customers/login')
# get a customer details by vendor
api.add_resource(resource.Customer, '/customers/<int:customer_id>')
# request password change
api.add_resource(resource.RequestPasswordChange, '/requests')
# recover a forgottern password
api.add_resource(resource.Password, '/changepassword/<string:token>')
# get all orders made by a customer method:get,post
api.add_resource(resource.CustomerOrders, '/customers/orders')
# get a single order made by customer method: get/patch/delete
api.add_resource(resource.CustomerOrder, '/customer/orders/<int:order_id>')
# get all customers details by vendor  method:get,patch to update
api.add_resource(resource.AllCustomers, '/customers')
# get all products by customer or vendor method:get,post
api.add_resource(resource.AllProducts, '/products')
# get a specific product  method: get/patch/delete
api.add_resource(resource.Product, '/product/<int:product_id>')
# vendor registration route method:post
api.add_resource(resource.VendorRegistration, '/vendor/registration')
# vendor login route method:post
api.add_resource(resource.VendorLogin, '/vendor/login')
# get all orders made to a vendor method:get,post
api.add_resource(resource.AllOrders, '/vendor/orders')
# vendor get all categories method:get,post
api.add_resource(resource.AllCategories, '/vendor/categories')
# vendor get a  specific category  method: get/patch/delete
api.add_resource(resource.Category, '/vendor/categories/<int:category_id>')
# vendor post a payment type
api.add_resource(resource.AllPaymentTypes, '/vendor/paymenttype')
# fetch a payment type, update or delete
api.add_resource(resource.PaymentTypes, '/vendor/paymenttype/<int:paymenttype_id>')
# post a new address
api.add_resource(resource.addresses, '/addresses')
# fetch address for a user or update an address or delete
api.add_resource(resource.address, '/addresses/<int:address_id>')



if __name__ == '__main__':
    app.run()