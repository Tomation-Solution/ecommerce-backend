from marshmallow import Schema, fields,validates, ValidationError

class CustomersSchema(Schema):
    customer_id = fields.Integer(strict=True)
    firstname = fields.String(required=True, error_messages={"required":"first name is required"})
    lastname = fields.String(required=True,error_messages={"required":"last name is required"})
    date_created = fields.DateTime()
    email = fields.Email(required=True, error_messages={"required":"Email is required"})
    phone_number = fields.Str(validate=fields.Length(11,13))
    password  = fields.Str(validate=fields.Length(8,15))

class OrdersSchema(Schema):
    order_id = fields.Integer(strict=True)
    date_ordered = fields.DateTime()
    total_quantity = fields.Integer(required=True, strict=True)
    total_price = fields.Integer(required=True, strict=True)
    customer_id = fields.Integer(required=True, strict=True)
    status = fields.Str(required=True)