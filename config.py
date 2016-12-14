# coding=utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[大乐]'
    # 在本地环境设置支持smtp的邮箱服务
    #Mac OS X 中使用 bash，那么可以按照下面的方式设定这两个变量：
    # (venv) $ export MAIL_USERNAME=<Gmail username>
    # (venv) $ export MAIL_PASSWORD=<Gmail password>
    # 微软 Windows 用户可按照下面的方式设定环境变量：
    # (venv) $ set MAIL_USERNAME=<Gmail username>
    # (venv) $ set MAIL_PASSWORD=<Gmail password>
    # set MAIL_USERNAME=zhoule627886474@163.com
    FLASKY_MAIL_SENDER = 'zhoule627886474@163.com'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30

    @staticmethod
    def init_app(app):
        pass

# 开发环境
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/Flask-dev'



# 正式环境
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/Flask-pro'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
