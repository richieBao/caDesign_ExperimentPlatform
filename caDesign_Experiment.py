import os
#from dotenv import load_dotenv

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

import sys
import click
from app import create_app, db
from app.models import User, Role  #Follow,Permission, Post, Comment
from flask_migrate import Migrate, upgrade

#print("_"*50)
#print(os.getenv('FLASK_CONFIG') )

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
#print("+"*50)
migrate = Migrate(app, db)

@app.shell_context_processor #在flask shell 中导入其他对象,导入后shell可以使用
def make_shell_context():
    return dict(db=db, User=User, Role=Role)  #Follow=Follow,Permission=Permission, Post=Post, Comment=Comment)


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
              help='Run tests under code coverage.')
@click.argument('test_names', nargs=-1)
def test(coverage, test_names):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        sys.exit(subprocess.call(sys.argv))

    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@app.cli.command()
@click.option('--length', default=25,
              help='Number of functions to include in the profiler report.')
@click.option('--profile-dir', default=None,
              help='Directory where profiler data files are saved.')
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    from werkzeug.middleware.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()

@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()

    # create or update user roles
    Role.insert_roles()

    # ensure all users are following themselves
    User.add_self_follows()

'''
@app.cli.command() #被装饰的函数名就是命令名
def test():
    """Run the unit tests."""
    import subprocess
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
'''


@app.route('/userA/<name>')
def userA(name):
    return '<h1>Hello, %s!</h1>' % name






# 异步发送邮件
from flask_mail import Mail, Message
from threading import Thread
def send_async_email(app, msg):
    app.config['MAIL_DEBUG'] = True  # 开启debug，便于调试看信息
    app.config['MAIL_SUPPRESS_SEND'] = False  # 发送邮件，为True则不发送
    app.config['MAIL_SERVER'] = 'smtp.qq.com'  # 邮箱服务器
    app.config['MAIL_PORT'] = 465  # 端口
    app.config['MAIL_USE_SSL'] = True  # 重要，qq邮箱需要使用SSL
    app.config['MAIL_USE_TLS'] = False  # 不需要使用TLS
    app.config['MAIL_USERNAME'] = '1310555375@qq.com'  # 填邮箱
    app.config['MAIL_PASSWORD'] = 'mcjhykfeslacfeec'  # 填授权码
    app.config['MAIL_DEFAULT_SENDER'] = '1310555375@qq.com'  # 填邮箱，默认发送者
    mail = Mail(app)
    with app.app_context():
        mail.send(msg)

@app.route('/mail')
def mail_test():
    msg = Message(subject='Hello World',
                  sender="1310555375@qq.com",  # 需要使用默认发送者则不用填
                  recipients=['richiebao@outlook.com', ])
    # 邮件内容会以文本和html两种格式呈现，而你能看到哪种格式取决于你的邮件客户端。
    msg.body = 'sended by flask-email'
    msg.html = '<b>caDesign Experiment Platform——测试Flask发送邮件<b>'
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return '<h1>邮件发送成功</h1>'





