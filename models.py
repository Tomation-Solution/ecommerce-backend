from config import db, app
from datetime import datetime
from passlib.hash import pbkdf2_sha256 as sha256
import jwt
import time


class Customers(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(13), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    address = db.relationship('Address', backref=db.backref(
        'customer', lazy=True), cascade="all, delete-orphan")
    order = db.relationship(
        'Orders', backref=db.backref('customer'), lazy=True)

    def __str__(self):
        return '<Customer {} {}>'.format(self.firstname, self.lastname)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def generate_auth_token(self):
        return jwt.encode({'customer_id': self.customer_id}, app.config['SECRET_KEY'])

    @staticmethod
    def verify_auth_token(token):
        print('calling the static method')
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            print('there was an error')
            return
        return Customers.query.get(data['customer_id'])

    @classmethod
    def find_by_username(cls, email):
        return cls.query.filter_by(email=email).first()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class Address(db.Model):
    address_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customers.customer_id'), nullable=False)
    full_address = db.Column(db.Text, nullable=False)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    order = db.relationship('Orders', backref=db.backref(
        'address', lazy=True), cascade="all, delete-orphan")

    def __str__(self):
        return '<Address: {}>'.format(self.full_address)


class Products(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_image = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        'categories.category_id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    orderdetails = db.relationship(
        'OrderDetails', backref=db.backref('product', lazy=True))
    salesviewhistory = db.relationship('SalesViewHistory', backref=db.backref('product', lazy=True), cascade="all, delete-orphan")
    stock_quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric())
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def __str__(self):
        return "{} {}".format(self.product_name)


class Categories(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    product = db.relationship('Products', backref=db.backref(
        'category', lazy=True), cascade="all, delete-orphan")

    def __str__(self):
        return 'category - {}'.format(self.category_name)

# stores an aggregation of the total quantity ordered, total price, the customer id and the status of the order


class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    date_ordered = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    total_quantity = db.Column(db.Integer, nullable=False, default=0)
    total_price = db.Column(db.Numeric())
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customers.customer_id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey(
        'address.address_id'), nullable=False)
    orderdetails = db.relationship('OrderDetails', backref=db.backref(
        'order', lazy=True), cascade="all, delete-orphan")
    status = db.Column(db.String(25), nullable=False, default='progress')

    def __str__(self):
        return "{} {}".format(self.total_quantity, self.total_price)

# stores the breakdown detail of every order into individual product,quantity ordered and the cost of each


class OrderDetails(db.Model):
    order_detail_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    quantity = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Numeric())


class Vendor(db.Model):
    vendor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    vendor_logo = db.Column(db.String(150), nullable=False)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    account_number = db.Column(db.String(10), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    bank = db.Column(db.String(50))
    phone_number = db.Column(db.String(13), nullable=False)
    full_address = db.Column(db.Text, nullable=False)

    def __str__(self):
        return '{}'.format(self.name)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def generate_auth_token(self):
        return jwt.encode({'vendor_id': self.vendor_id}, app.config['SECRET_KEY'])

    @staticmethod
    def verify_auth_token(token):
        print('calling the static method')
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            print('there was an error')
            return
        return Vendor.query.get(data['vendor_id'])

    @classmethod
    def find_by_username(cls, email):
        return cls.query.filter_by(email=email).first()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)



class SalesViewHistory(db.Model):
     vsales_id = db.Column(db.Integer, primary_key=True)
     product_id = db.Column(db.Integer,db.ForeignKey('products.product_id'))
     total_views = db.Column(db.Integer)
     total_sales = db.Column(db.Integer)