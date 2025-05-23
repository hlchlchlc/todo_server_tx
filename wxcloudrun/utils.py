import os
import jwt
import datetime
import uuid
import json
from functools import wraps
from flask import request, jsonify
import logging
from werkzeug.security import generate_password_hash, check_password_hash

from wxcloudrun.dao import get_user_by_id, is_token_blacklisted

# 初始化日志
logger = logging.getLogger('log')

# JWT配置
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=30)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=7)

def hash_password(password):
    """
    对密码进行哈希处理
    """
    return generate_password_hash(password)

def check_password(password_hash, password):
    """
    验证密码是否匹配
    """
    return check_password_hash(password_hash, password)

def generate_access_token(user_id):
    """
    生成访问令牌
    """
    payload = {
        'exp': datetime.datetime.utcnow() + JWT_ACCESS_TOKEN_EXPIRES,
        'iat': datetime.datetime.utcnow(),
        'sub': user_id,
        'type': 'access'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def generate_refresh_token(user_id):
    """
    生成刷新令牌
    """
    payload = {
        'exp': datetime.datetime.utcnow() + JWT_REFRESH_TOKEN_EXPIRES,
        'iat': datetime.datetime.utcnow(),
        'sub': user_id,
        'type': 'refresh'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def decode_token(token):
    """
    解码JWT令牌
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        if is_token_blacklisted(token):
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """
    用于验证访问令牌的装饰器
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从Authorization头中获取令牌
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': {'message': 'Token is missing', 'code': 'token_missing'}}), 401
        
        if not token:
            return jsonify({'error': {'message': 'Token is missing', 'code': 'token_missing'}}), 401
        
        # 解码令牌
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': {'message': 'Token is invalid or expired', 'code': 'token_invalid'}}), 401
        
        # 验证令牌类型
        if payload.get('type') != 'access':
            return jsonify({'error': {'message': 'Invalid token type', 'code': 'token_type_invalid'}}), 401
        
        # 获取用户
        current_user = get_user_by_id(payload['sub'])
        if not current_user:
            return jsonify({'error': {'message': 'User not found', 'code': 'user_not_found'}}), 401
        
        # 将用户对象传递给被装饰的函数
        return f(current_user, *args, **kwargs)
    
    return decorated

def refresh_token_required(f):
    """
    用于验证刷新令牌的装饰器
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从Authorization头中获取令牌
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': {'message': 'Token is missing', 'code': 'token_missing'}}), 401
        
        if not token:
            return jsonify({'error': {'message': 'Token is missing', 'code': 'token_missing'}}), 401
        
        # 解码令牌
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': {'message': 'Token is invalid or expired', 'code': 'token_invalid'}}), 401
        
        # 验证令牌类型
        if payload.get('type') != 'refresh':
            return jsonify({'error': {'message': 'Invalid token type', 'code': 'token_type_invalid'}}), 401
        
        # 获取用户
        current_user = get_user_by_id(payload['sub'])
        if not current_user:
            return jsonify({'error': {'message': 'User not found', 'code': 'user_not_found'}}), 401
        
        # 将用户对象传递给被装饰的函数
        return f(current_user, *args, **kwargs)
    
    return decorated

def format_task(task):
    """
    格式化任务对象为JSON响应
    """
    tags = [tag.tag_name for tag in task.tags] if task.tags else []
    custom_week_days = None
    if task.custom_week_days:
        try:
            custom_week_days = json.loads(task.custom_week_days)
        except:
            custom_week_days = []
    
    return {
        'id': task.id,
        'title': task.title,
        'goal_id': task.goal_id,
        'completed': task.completed,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'priority': task.priority,
        'estimated_time': task.estimated_time,
        'actual_time': task.actual_time,
        'created_at': task.created_at.isoformat(),
        'tags': tags,
        'notes': task.notes,
        'expected_outcome': task.expected_outcome,
        'enthusiasm': task.enthusiasm,
        'difficulty': task.difficulty,
        'importance': task.importance,
        'is_repeating': task.is_repeating,
        'repeat_frequency': task.repeat_frequency,
        'repeat_interval': task.repeat_interval,
        'repeat_end_date': task.repeat_end_date.isoformat() if task.repeat_end_date else None,
        'repeat_count': task.repeat_count,
        'parent_task_id': task.parent_task_id,
        'custom_week_days': custom_week_days
    }

def format_goal(goal):
    """
    格式化目标对象为JSON响应
    """
    return {
        'id': goal.id,
        'title': goal.title,
        'description': goal.description,
        'category': goal.category,
        'color': goal.color,
        'icon': goal.icon,
        'start_date': goal.start_date.isoformat() if goal.start_date else None,
        'end_date': goal.end_date.isoformat() if goal.end_date else None,
        'completed': goal.completed,
        'progress': goal.progress,
        'created_at': goal.created_at.isoformat(),
        'goal_type': goal.goal_type
    }

def format_user(user):
    """
    格式化用户对象为JSON响应
    """
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    } 