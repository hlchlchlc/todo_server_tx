from flask import Blueprint, request, jsonify
from datetime import datetime

from wxcloudrun.dao import get_user_by_username, get_user_by_email, create_user, update_user_last_login, add_token_to_blacklist
from wxcloudrun.utils import hash_password, check_password, generate_access_token, generate_refresh_token, format_user, token_required, refresh_token_required

# 创建蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    """
    data = request.get_json()
    
    # 验证请求数据
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': {'message': 'Username, email and password are required', 'code': 'missing_fields'}}), 400
    
    # 检查用户名是否已存在
    if get_user_by_username(data.get('username')):
        return jsonify({'error': {'message': 'Username already exists', 'code': 'username_exists'}}), 400
    
    # 检查邮箱是否已存在
    if get_user_by_email(data.get('email')):
        return jsonify({'error': {'message': 'Email already exists', 'code': 'email_exists'}}), 400
    
    # 创建新用户
    hashed_password = hash_password(data.get('password'))
    user = create_user(data.get('username'), data.get('email'), hashed_password)
    
    if not user:
        return jsonify({'error': {'message': 'Failed to create user', 'code': 'create_failed'}}), 500
    
    # 返回用户信息
    return jsonify(format_user(user)), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    """
    data = request.get_json()
    
    # 验证请求数据
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': {'message': 'Username and password are required', 'code': 'missing_fields'}}), 400
    
    # 获取用户
    user = get_user_by_username(data.get('username'))
    if not user:
        return jsonify({'error': {'message': 'Invalid credentials', 'code': 'invalid_credentials'}}), 401
    
    # 验证密码
    if not check_password(user.password_hash, data.get('password')):
        return jsonify({'error': {'message': 'Invalid credentials', 'code': 'invalid_credentials'}}), 401
    
    # 更新最后登录时间
    update_user_last_login(user.id)
    
    # 生成令牌
    access_token = generate_access_token(user.id)
    refresh_token = generate_refresh_token(user.id)
    
    # 返回令牌和用户信息
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': format_user(user)
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@refresh_token_required
def refresh(current_user):
    """
    刷新访问令牌
    """
    # 生成新的访问令牌
    access_token = generate_access_token(current_user.id)
    
    return jsonify({
        'access_token': access_token
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    退出登录
    """
    # 获取令牌
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(" ")[1]
    
    # 将令牌添加到黑名单
    if not add_token_to_blacklist(token):
        return jsonify({'error': {'message': 'Failed to logout', 'code': 'logout_failed'}}), 500
    
    return '', 204

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(current_user):
    """
    获取当前用户信息
    """
    return jsonify(format_user(current_user)), 200 