import uuid
import mongoengine as me
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from Models.Roles import RoleEnum



class User(UserMixin, me.Document):
    user_id = me.UUIDField(primary_key=True, default=uuid.uuid4)
    username = me.StringField(required=True, unique=True)
    email = me.StringField(required=True, unique=True)
    password_hash = me.StringField(required=True)
    roles = me.ListField(me.StringField(choices=[role.value for role in RoleEnum]), default=[RoleEnum.USER.value])
    is_verified = me.BooleanField(default=False) 
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def add_role(self, role):
        if role not in self.roles:
            self.roles.append(role.value)
            self.save()

    def remove_role(self, role):
        if role.value in self.roles:
            self.roles.remove(role.value)
            self.save()
            
    def has_role(self, role):
        return role.value in self.roles