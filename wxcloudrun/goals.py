from flask import Blueprint, request, jsonify
from datetime import datetime

from wxcloudrun.dao import (
    get_goals_by_user_id, get_goal_by_id, create_goal, 
    update_goal, delete_goal, calculate_goal_progress,
    get_tasks_by_user_id
)
from wxcloudrun.utils import token_required, format_goal, format_task

# 创建蓝图
goals_bp = Blueprint('goals', __name__, url_prefix='/api/goals')

@goals_bp.route('', methods=['GET'])
@token_required
def get_goals(current_user):
    """
    获取所有目标
    """
    # 获取查询参数
    goal_type = request.args.get('type', 'all')
    
    # 获取目标列表
    goals = get_goals_by_user_id(current_user.id, goal_type)
    
    # 格式化响应
    return jsonify([format_goal(goal) for goal in goals]), 200

@goals_bp.route('', methods=['POST'])
@token_required
def add_goal(current_user):
    """
    创建新目标
    """
    data = request.get_json()
    
    # 验证请求数据
    if not data or not data.get('title'):
        return jsonify({'error': {'message': 'Title is required', 'code': 'missing_title'}}), 400
    
    # 处理日期字段
    if 'start_date' in data and data['start_date']:
        try:
            data['start_date'] = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': {'message': 'Invalid start_date format', 'code': 'invalid_date'}}), 400
    
    if 'end_date' in data and data['end_date']:
        try:
            data['end_date'] = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': {'message': 'Invalid end_date format', 'code': 'invalid_date'}}), 400
    
    # 创建目标
    goal = create_goal(data, current_user.id)
    
    if not goal:
        return jsonify({'error': {'message': 'Failed to create goal', 'code': 'create_failed'}}), 500
    
    # 返回创建的目标
    return jsonify(format_goal(goal)), 201

@goals_bp.route('/<goal_id>', methods=['GET'])
@token_required
def get_goal(current_user, goal_id):
    """
    获取单个目标
    """
    goal = get_goal_by_id(goal_id, current_user.id)
    
    if not goal:
        return jsonify({'error': {'message': 'Goal not found', 'code': 'goal_not_found'}}), 404
    
    return jsonify(format_goal(goal)), 200

@goals_bp.route('/<goal_id>', methods=['PUT'])
@token_required
def update_goal_route(current_user, goal_id):
    """
    更新目标
    """
    data = request.get_json()
    
    # 验证请求数据
    if not data:
        return jsonify({'error': {'message': 'No data provided', 'code': 'missing_data'}}), 400
    
    # 处理日期字段
    if 'start_date' in data and data['start_date']:
        try:
            data['start_date'] = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': {'message': 'Invalid start_date format', 'code': 'invalid_date'}}), 400
    
    if 'end_date' in data and data['end_date']:
        try:
            data['end_date'] = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': {'message': 'Invalid end_date format', 'code': 'invalid_date'}}), 400
    
    # 更新目标
    goal = update_goal(goal_id, data, current_user.id)
    
    if not goal:
        return jsonify({'error': {'message': 'Goal not found', 'code': 'goal_not_found'}}), 404
    
    # 如果更新了完成状态或进度，重新计算进度
    if 'completed' in data or 'progress' in data:
        calculate_goal_progress(goal_id)
    
    # 重新获取更新后的目标
    goal = get_goal_by_id(goal_id, current_user.id)
    
    return jsonify(format_goal(goal)), 200

@goals_bp.route('/<goal_id>', methods=['DELETE'])
@token_required
def delete_goal_route(current_user, goal_id):
    """
    删除目标
    """
    result = delete_goal(goal_id, current_user.id)
    
    if not result:
        return jsonify({'error': {'message': 'Goal not found', 'code': 'goal_not_found'}}), 404
    
    return '', 204

@goals_bp.route('/<goal_id>/tasks', methods=['GET'])
@token_required
def get_goal_tasks(current_user, goal_id):
    """
    获取目标下的所有任务
    """
    # 首先检查目标是否存在
    goal = get_goal_by_id(goal_id, current_user.id)
    
    if not goal:
        return jsonify({'error': {'message': 'Goal not found', 'code': 'goal_not_found'}}), 404
    
    # 获取目标下的任务
    tasks = get_tasks_by_user_id(current_user.id, None, goal_id)
    
    return jsonify([format_task(task) for task in tasks]), 200 