from datetime import datetime
import uuid

from wxcloudrun import db


def generate_uuid():
    """生成UUID作为主键"""
    return str(uuid.uuid4())


# 用户表
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # 定义关系
    tasks = db.relationship('Task', backref='user', lazy=True, cascade="all, delete-orphan")
    goals = db.relationship('Goal', backref='user', lazy=True, cascade="all, delete-orphan")


# 任务表
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_id = db.Column(db.String(36), db.ForeignKey('goals.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Enum('high', 'medium', 'low', name='priority_enum'), default='medium')
    estimated_time = db.Column(db.Integer, default=0)  # 预计时间（分钟）
    actual_time = db.Column(db.Integer, default=0)  # 实际时间（分钟）
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    notes = db.Column(db.Text, nullable=True)
    expected_outcome = db.Column(db.Text, nullable=True)
    enthusiasm = db.Column(db.Integer, nullable=True)  # 热情度(1-5)
    difficulty = db.Column(db.Integer, nullable=True)  # 困难度(1-5)
    importance = db.Column(db.Integer, nullable=True)  # 重要性(1-5)
    is_repeating = db.Column(db.Boolean, default=False)
    repeat_frequency = db.Column(db.Enum('daily', 'weekly', 'monthly', 'yearly', 'custom', name='repeat_freq_enum'), nullable=True)
    repeat_interval = db.Column(db.Integer, nullable=True)
    repeat_end_date = db.Column(db.DateTime, nullable=True)
    repeat_count = db.Column(db.Integer, nullable=True)
    parent_task_id = db.Column(db.String(36), nullable=True)
    custom_week_days = db.Column(db.String(20), nullable=True)  # JSON格式
    
    # 定义关系
    tags = db.relationship('TaskTag', backref='task', lazy=True, cascade="all, delete-orphan")


# 目标表
class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(20), nullable=False, default='#000000')
    icon = db.Column(db.String(50), nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    progress = db.Column(db.Integer, default=0)  # 进度(0-100)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    goal_type = db.Column(db.Enum('long_term', 'active', name='goal_type_enum'), default='active')
    
    # 定义关系
    tasks = db.relationship('Task', backref='goal', lazy=True)


# 任务标签表
class TaskTag(db.Model):
    __tablename__ = 'task_tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'), nullable=False)
    tag_name = db.Column(db.String(50), nullable=False)


# 黑名单令牌表（用于注销和令牌管理）
class BlacklistedToken(db.Model):
    __tablename__ = 'blacklisted_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False, default=datetime.now)
