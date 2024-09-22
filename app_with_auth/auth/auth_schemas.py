import re
from marshmallow import Schema, fields, post_load, validates, ValidationError

class RegistrationSchema(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    confirm_password = fields.String(required=True)
    
    @post_load
    def validate_passwords(self, data, **kwargs):
        if data['password'] != data['confirm_password']:
            raise ValidationError("Passwords do not match.")
        return data

    @validates('password')
    def validate_password(self, value):
        # Password must contain at least one letter, one number, and one special character
        if not re.search(r'[A-Za-z]', value):
            raise ValidationError("Password must contain at least one letter.")
        if not re.search(r'\d', value):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),-.?":{}|<>]', value):
            raise ValidationError("Password must contain at least one special character.")

class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
