from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
import os
import config

# 因MySQLDB不支持Python3，使用pymysql扩展库代替MySQLDB库
pymysql.install_as_MySQLdb()

# 初始化web应用
app = Flask(__name__, instance_relative_config=True)
app.config['DEBUG'] = config.DEBUG

# 设定数据库链接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/todo_app'.format(
    config.username, config.password, config.db_address
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
app.config['JSON_AS_ASCII'] = False

# 初始化DB操作对象
db = SQLAlchemy(app)

# 加载配置
app.config.from_object('config')

# 确保数据库表存在
from wxcloudrun.model import User, Task, Goal, TaskTag, BlacklistedToken
@app.before_first_request
def create_tables():
    db.create_all()

# 加载控制器
from wxcloudrun import views
