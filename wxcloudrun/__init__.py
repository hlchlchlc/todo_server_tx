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

# 尝试创建数据库
def create_database_if_not_exists():
    try:
        # 不指定数据库名称，连接到MySQL服务器
        conn = pymysql.connect(
            host=config.db_address.split(':')[0],
            port=int(config.db_address.split(':')[1]),
            user=config.username,
            password=config.password
        )
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute("CREATE DATABASE IF NOT EXISTS todo_app")
        
        # 关闭连接
        cursor.close()
        conn.close()
        print("数据库检查/创建成功")
    except Exception as e:
        print(f"创建数据库时出错: {e}")

# 创建数据库
create_database_if_not_exists()

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
