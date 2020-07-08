from config import app, api
from flask import Flask,jsonify,request
import json
import resource

# customers and vendor registration,login and logout
api.add_resource(resource.CustomerRegistration, '/registration/customer')
api.add_resource(resource.VendorRegistration, '/registration/vendor')
api.add_resource(resource.CustomerLogin, '/login/customer')
api.add_resource(resource.VendorLogin, '/login/vendor')

#api to handle all of customers,products,categories, orders
api.add_resource(resource.AllCustomers, '/customers')
api.add_resource(resource.AllProducts, '/products')
api.add_resource(resource.AllOrders, '/orders')
api.add_resource(resource.Categories, '/categories')

api.add_resource(resource.CustomerOrders, '/customer/orders')

#api to handle specific customer, product, categories, order
api.add_resource(resource.Customer, '/customer/<int:customer_id>')
api.add_resource(resource.Product, '/product/<int:product_id>')
api.add_resource(resource.Order, '/order/<int:order_id>')
api.add_resource(resource.Category, '/category/<int:category_id>')

api.add_resource(resource.CustomerOrder, '/customer/orders/<int:order_id>')

if __name__ == '__main__':
    app.run(debug=True)