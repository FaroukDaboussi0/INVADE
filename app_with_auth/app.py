
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_principal import Principal
from flask_mail import Mail
import mongoengine as me
from flask_session import Session

from config import Config
from auth import auth_bp  # Import the auth blueprint

# Initialize extensions
ma = Marshmallow()
jwt = JWTManager()
principal = Principal()
mail = Mail()
session = Session()
login_manager = LoginManager()
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize MongoEngine with app config
    me.connect(
        db=app.config['MONGODB_SETTINGS']['db'],
        host=app.config['MONGODB_SETTINGS']['host'],
        port=app.config['MONGODB_SETTINGS']['port']
    )

    # Initialize Flask-Mail
    mail.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    principal.init_app(app)
    session.init_app(app)
   
    login_manager.init_app(app)

    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Register other blueprints here
    # app.register_blueprint(other_bp, url_prefix='/other')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
