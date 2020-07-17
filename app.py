from config import app, api
from flask import Flask,jsonify,request
import json
import resource

# customer registration route method:post,patch to update
api.add_resource(resource.CustomerRegistration, '/customer/registration')
# customer login route method:post
api.add_resource(resource.CustomerLogin, '/customer/login')
# get a customer details by vendor
api.add_resource(resource.Customer, '/customer/<int:customer_id>')
# get all orders made by a customer method:get,post
api.add_resource(resource.CustomerOrders, '/customer/orders')
# get a single order made by customer method: get/patch/delete
api.add_resource(resource.CustomerOrder, '/customer/orders/<int:order_id>')
# get all customers details by vendor  method:get
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
api.add_resource(resource.Category, '/vendor/category/<int:category_id>')

#search for a product by name




if __name__ == '__main__':
    app.run()