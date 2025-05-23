from flask import Blueprint, request, jsonify
from datetime import datetime
import json

from wxcloudrun.dao import (
    get_tasks_by_user_id, get_task_by_id, create_task, 
    update_task, delete_task, toggle_task_complete
)
from wxcloudrun.utils import token_required, format_task

# 创建蓝图
tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@tasks_bp.route('', methods=['GET'])
@token_required
def get_tasks(current_user):
    """
    获取所有任务
    支持过滤、排序和按目标筛选
    """
    # 获取查询参数
    filter_type = request.args.get('filter', 'all')
    sort_by = request.args.get('sort')
    goal_id = request.args.get('goal_id')
    
    # 获取任务列表
    tasks = get_tasks_by_user_id(current_user.id, filter_type, goal_id, sort_by)
    
    # 格式化响应
    return jsonify([format_task(task) for task in tasks]), 200

@tasks_bp.route('', methods=['POST'])
@token_required
def add_task(current_user):
    """
    创建新任务
    """
    data = request.get_json()
    
    # 验证请求数据
    if not data or not data.get('title'):
        return jsonify({'error': {'message': 'Title is required', 'code': 'missing_title'}}), 400
    
    # 处理日期字段
    if 'due_date' in data and data['due_date']:
        try:
            data['due_date'] = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': {'message': 'Invalid due_date format', 'code': 'invalid_date'}}), 400
    
    if 'repeat_end_date' in data and data['repeat_end_date']:
        try:
            data['repeat_end_date'] = datetime.fromisoformat(data['repeat_end_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': {'message': 'Invalid repeat_end_date format', 'code': 'invalid_date'}}), 400
    
    # 创建任务
    task = create_task(data, current_user.id)
    
    if not task:
        return jsonify({'error': {'message': 'Failed to create task', 'code': 'create_failed'}}), 500
    
    # 返回创建的任务
    return jsonify(format_task(task)), 201

@tasks_bp.route('/<task_id>', methods=['GET'])
@token_required
def get_task(current_user, task_id):
    """
    获取单个任务
    """
    task = get_task_by_id(task_id, current_user.id)
    
    if not task:
        return jsonify({'error': {'message': 'Task not found', 'code': 'task_not_found'}}), 404
    
    return jsonify(format_task(task)), 200

@tasks_bp.route('/<task_id>', methods=['PUT'])
@token_required
def update_task_route(current_user, task_id):
    """
    更新任务
    """
    data = request.get_json()
    
    # 验证请求数据
    if not data:
        return jsonify({'error': {'message': 'No data provided', 'code': 'missing_data'}}), 400
    
    # 处理日期字段
    if 'due_date' in data and data['due_date']:
        try:
            data['due_date'] = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': {'message': 'Invalid due_date format', 'code': 'invalid_date'}}), 400
    
    if 'repeat_end_date' in data and data['repeat_end_date']:
        try:
            data['repeat_end_date'] = datetime.fromisoformat(data['repeat_end_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': {'message': 'Invalid repeat_end_date format', 'code': 'invalid_date'}}), 400
    
    # 更新任务
    task = update_task(task_id, data, current_user.id)
    
    if not task:
        return jsonify({'error': {'message': 'Task not found', 'code': 'task_not_found'}}), 404
    
    return jsonify(format_task(task)), 200

@tasks_bp.route('/<task_id>', methods=['DELETE'])
@token_required
def delete_task_route(current_user, task_id):
    """
    删除任务
    """
    result = delete_task(task_id, current_user.id)
    
    if not result:
        return jsonify({'error': {'message': 'Task not found', 'code': 'task_not_found'}}), 404
    
    return '', 204

@tasks_bp.route('/<task_id>/toggle-complete', methods=['PATCH'])
@token_required
def toggle_complete(current_user, task_id):
    """
    切换任务完成状态
    """
    task = toggle_task_complete(task_id, current_user.id)
    
    if not task:
        return jsonify({'error': {'message': 'Task not found', 'code': 'task_not_found'}}), 404
    
    return jsonify(format_task(task)), 200 