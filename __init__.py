import os
from flask import Flask

def create_app(test=None):
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path,'messenger.sqlite'),
    )

    if test is None:
        app.config.from_pyfile('config.py',silent=True)
    else:
        app.config.from_mapping(test)

    try:
        os.makedirs(app.instance_path)
    except:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello user'
    
    @app.route('/poop')
    def poopy():
        return 'u found the secret path'

    from . import db
    db.initApp(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import message
    app.register_blueprint(message.bp)
    app.add_url_rule('/',endpoint='index')

    return app