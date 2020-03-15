import os
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # 加载默认开发环境配置
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    # 测试环境配置如有，则加载，否则，从instance path中加载配置
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # 创建instance path
    try:
        os.mkdir(app.instance_path)
    except OSError:
        pass

    # 初始化app
    from . import db
    db.init_app(app)

    # 添加blueprint
    from . import auth
    app.register_blueprint(auth.bp)
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    # 创建默认视图
    @app.route('/')
    def hello_world():
        return 'Hello World!'

    return app
