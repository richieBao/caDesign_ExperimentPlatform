from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config

from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import os
#from flask_images import Images

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

photos=UploadSet('photos', IMAGES)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    basedir=os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOADED_PHOTOS_DEST']=os.path.join(basedir,'uploads')  # you'll need to create a folder named uploads
    configure_uploads(app, photos)
    patch_request_class(app)
    #images=Images(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    '''
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    '''
    
    from .visual_perception import visual_perception as vp_blueprint
    app.register_blueprint(vp_blueprint, url_prefix='/vp')

    return app


