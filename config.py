import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config: #用类的方式存储配置变量有助于后续扩展
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string' #flask及扩展将SECRET_KEY配置变量作为加密密钥，用于生成签名或令牌。程序会先从环境变量中查找 SECRET_KEY， 如果没有，就会使用后面的硬编码字符串。

    MAIL_DEBUG=os.environ.get('MAIL_DEBUG', True)
    MAIL_SUPPRESS_SEND=os.environ.get('MAIL_SUPPRESS_SEND', False)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', True)  # 重要，qq邮箱需要使用SSL
    MAIL_DEFAULT_SENDER=('MAIL_DEFAULT_SENDER','1310555375@qq.com' )

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', False)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME','1310555375@qq.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD','mcjhykfeslacfeec')
    FLASKY_MAIL_SUBJECT_PREFIX = '[caDesign Experiment Platform]'
    FLASKY_MAIL_SENDER = 'caDesign Experiment Platform <1310555375@qq.com>'

    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SSL_REDIRECT = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_SLOW_DB_QUERY_TIME = 0.5

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or  'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod #指定一个类的方法为类方法，没有此参数（装饰符）指定的类的方法为实例方法。在于重构类的时候，不必修改构造函数（即__init__函数），只是额外添加需要处理的函数。
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.INFO)
        app.logger.addHandler(syslog_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}