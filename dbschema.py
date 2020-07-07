from marshmallow import Schema, fields,validates, ValidationError

class CustomersSchema(Schema):
    firstname = fields.String(required=True, error_messages={"required":"first name is required"})
    lastname = fields.String(required=True,error_messages={"required":"last name is required"})
    email = fields.Email(required=True, error_messages={"required":"Email is required"})
    phone_number = fields.Str(validate=fields.Length(11,13))
    password  = fields.Str(validate=fields.Length(8,15))

