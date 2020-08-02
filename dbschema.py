from marshmallow import Schema, fields,validates, ValidationError

class AddressSchema(Schema):
    address_id = fields.Integer(strict=True)
    customer_id = fields.Integer(strict=True)
    full_address = fields.String(required=True,error_messages={"required":"Adress is required"})
    date_created = fields.DateTime()

class CustomersSchema(Schema):
    customer_id = fields.Integer(strict=True)
    firstname = fields.String(required=True, error_messages={"required":"first name is required"})
    lastname = fields.String(required=True,error_messages={"required":"last name is required"})
    date_created = fields.DateTime()
    email = fields.Email(required=True, error_messages={"required":"Email is required"})
    phone_number = fields.Str(validate=fields.Length(11,13))
    password  = fields.Str(validate=fields.Length(8,15))

class OrderSchema(Schema):
    order_detail_id =fields.Integer(strict=True)
    order_id = fields.Integer(strict=True)
    product_id =fields.Integer(strict=True)
    quantity = fields.Integer(strict=True)
    cost = fields.Integer(required=True, error_messages={"required":"Cost is required"})

class OrdersSchema(Schema):
    order_id = fields.Integer(strict=True)
    date_ordered = fields.DateTime()
    total_quantity = fields.Integer(required=True, strict=True)
    total_price = fields.Integer(required=True)
    customer_id = fields.Integer(required=True, strict=True)
    paymenttype_id = fields.Integer(required=True, strict=True)
    status = fields.Str(required=True)
    address_id = fields.Integer(strict=True)
    paid = fields.Integer(required=True, strick=True)
    transaction_id = fields.Integer(required=True, strick=True)
    transaction_reference = fields.String(required=True)
    orders = fields.List(fields.Nested(OrderSchema()))

class VendorSchema(Schema):
    vendor_id = fields.Integer(strict=True)
    name = fields.Str(required=True, error_messages={"required":"name is required"})
    vendor_logo = fields.String(required=True, error_messages={"required":"company logo is required"})
    date_created = fields.DateTime()
    email = fields.Email(required=True, error_messages={"required":"email cannot be empty"})
    password  = fields.Str(validate=fields.Length(8,15))
    full_address = fields.String(required=True, error_messages={"required":"Address is required"})
    account_number = fields.String(required=True,error_messages={"required":"account number is required"})
    phone_number = fields.Str(validate=fields.Length(11,13))
    account_name =  fields.String(required=True)
    bank =  fields.String(required=True)

class ProductsSchema(Schema):
    product_id = fields.Integer(strict=True)
    product_name =fields.String(required=True)
    product_image = fields.String(required=True)
    category_id = fields.Integer(strict=True, required=True)
    description = fields.String(required=True)
    manufacturer = fields.String(required=True)
    stock_quantity = fields.Integer(required=True)
    price =fields.Integer(required=True)
    date_created =  fields.String(required=True)

class CategoriesSchema(Schema):
    category_id = fields.Integer(strict=True)
    category_name =  fields.String(required=True)
    date_created =  fields.String(required=True)

class PaymentTypeSchema(Schema):
    paymenttype_id = fields.Integer(strict=True)
    payment_type = fields.String(required=True)