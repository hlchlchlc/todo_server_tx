import logging
from datetime import datetime, timedelta
import json
from sqlalchemy.exc import OperationalError
import uuid

from wxcloudrun import db
from wxcloudrun.model import User, Task, Goal, TaskTag, BlacklistedToken

# 初始化日志
logger = logging.getLogger('log')

# ========== 用户相关 ==========
def get_user_by_id(user_id):
    """
    根据ID获取用户
    """
    try:
        return User.query.filter_by(id=user_id).first()
    except OperationalError as e:
        logger.error(f"get_user_by_id error: {e}")
        return None

def get_user_by_username(username):
    """
    根据用户名获取用户
    """
    try:
        return User.query.filter_by(username=username).first()
    except OperationalError as e:
        logger.error(f"get_user_by_username error: {e}")
        return None

def get_user_by_email(email):
    """
    根据邮箱获取用户
    """
    try:
        return User.query.filter_by(email=email).first()
    except OperationalError as e:
        logger.error(f"get_user_by_email error: {e}")
        return None

def create_user(username, email, password_hash):
    """
    创建新用户
    """
    try:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(user)
        db.session.commit()
        return user
    except OperationalError as e:
        logger.error(f"create_user error: {e}")
        db.session.rollback()
        return None

def update_user_last_login(user_id):
    """
    更新用户最后登录时间
    """
    try:
        user = get_user_by_id(user_id)
        if user:
            user.last_login = datetime.now()
            db.session.commit()
            return True
        return False
    except OperationalError as e:
        logger.error(f"update_user_last_login error: {e}")
        db.session.rollback()
        return False

# ========== 任务相关 ==========
def get_tasks_by_user_id(user_id, filter_type=None, goal_id=None, sort_by=None):
    """
    获取用户的所有任务
    filter_type: all, today, week, completed, upcoming, unscheduled
    sort_by: dueDate, createdAt, priority, alphabetical
    """
    try:
        query = Task.query.filter_by(user_id=user_id)
        
        # 应用过滤条件
        if filter_type:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = today + timedelta(days=7)
            
            if filter_type == 'today':
                query = query.filter(Task.due_date >= today, Task.due_date < today + timedelta(days=1))
            elif filter_type == 'week':
                query = query.filter(Task.due_date >= today, Task.due_date < week_end)
            elif filter_type == 'completed':
                query = query.filter_by(completed=True)
            elif filter_type == 'upcoming':
                query = query.filter(Task.due_date >= today)
            elif filter_type == 'unscheduled':
                query = query.filter(Task.due_date == None)
        
        # 按目标ID筛选
        if goal_id:
            query = query.filter_by(goal_id=goal_id)
        
        # 应用排序
        if sort_by:
            if sort_by == 'dueDate':
                query = query.order_by(Task.due_date)
            elif sort_by == 'createdAt':
                query = query.order_by(Task.created_at.desc())
            elif sort_by == 'priority':
                # 自定义排序: high > medium > low
                query = query.order_by(
                    db.case(
                        [(Task.priority == 'high', 1)],
                        [(Task.priority == 'medium', 2)],
                        else_=3
                    )
                )
            elif sort_by == 'alphabetical':
                query = query.order_by(Task.title)
        else:
            # 默认按创建时间排序
            query = query.order_by(Task.created_at.desc())
        
        return query.all()
    except OperationalError as e:
        logger.error(f"get_tasks_by_user_id error: {e}")
        return []

def get_task_by_id(task_id, user_id=None):
    """
    获取指定ID的任务
    如果提供user_id，则检查任务是否属于该用户
    """
    try:
        query = Task.query.filter_by(id=task_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()
    except OperationalError as e:
        logger.error(f"get_task_by_id error: {e}")
        return None

def create_task(task_data, user_id):
    """
    创建新任务
    """
    try:
        task = Task(
            user_id=user_id,
            goal_id=task_data.get('goal_id'),
            title=task_data.get('title'),
            completed=task_data.get('completed', False),
            due_date=task_data.get('due_date'),
            priority=task_data.get('priority', 'medium'),
            estimated_time=task_data.get('estimated_time', 0),
            actual_time=task_data.get('actual_time', 0),
            notes=task_data.get('notes'),
            expected_outcome=task_data.get('expected_outcome'),
            enthusiasm=task_data.get('enthusiasm'),
            difficulty=task_data.get('difficulty'),
            importance=task_data.get('importance'),
            is_repeating=task_data.get('is_repeating', False),
            repeat_frequency=task_data.get('repeat_frequency'),
            repeat_interval=task_data.get('repeat_interval'),
            repeat_end_date=task_data.get('repeat_end_date'),
            repeat_count=task_data.get('repeat_count'),
            parent_task_id=task_data.get('parent_task_id'),
            custom_week_days=json.dumps(task_data.get('custom_week_days')) if task_data.get('custom_week_days') else None
        )
        
        db.session.add(task)
        db.session.flush()  # 获取生成的ID
        
        # 添加标签
        if task_data.get('tags'):
            for tag_name in task_data.get('tags'):
                tag = TaskTag(task_id=task.id, tag_name=tag_name)
                db.session.add(tag)
        
        db.session.commit()
        return task
    except OperationalError as e:
        logger.error(f"create_task error: {e}")
        db.session.rollback()
        return None

def update_task(task_id, task_data, user_id):
    """
    更新任务
    """
    try:
        task = get_task_by_id(task_id, user_id)
        if not task:
            return None
        
        # 更新任务属性
        for key, value in task_data.items():
            if key == 'tags':
                continue  # 标签单独处理
            if key == 'custom_week_days' and value:
                value = json.dumps(value)
            if hasattr(task, key):
                setattr(task, key, value)
        
        # 更新标签
        if 'tags' in task_data:
            # 删除现有标签
            TaskTag.query.filter_by(task_id=task_id).delete()
            
            # 添加新标签
            for tag_name in task_data['tags']:
                tag = TaskTag(task_id=task_id, tag_name=tag_name)
                db.session.add(tag)
        
        db.session.commit()
        return task
    except OperationalError as e:
        logger.error(f"update_task error: {e}")
        db.session.rollback()
        return None

def delete_task(task_id, user_id):
    """
    删除任务
    """
    try:
        task = get_task_by_id(task_id, user_id)
        if not task:
            return False
        
        db.session.delete(task)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.error(f"delete_task error: {e}")
        db.session.rollback()
        return False

def toggle_task_complete(task_id, user_id):
    """
    切换任务完成状态
    """
    try:
        task = get_task_by_id(task_id, user_id)
        if not task:
            return None
        
        task.completed = not task.completed
        db.session.commit()
        return task
    except OperationalError as e:
        logger.error(f"toggle_task_complete error: {e}")
        db.session.rollback()
        return None

# ========== 目标相关 ==========
def get_goals_by_user_id(user_id, goal_type=None):
    """
    获取用户的所有目标
    """
    try:
        query = Goal.query.filter_by(user_id=user_id)
        
        if goal_type and goal_type != 'all':
            query = query.filter_by(goal_type=goal_type)
        
        return query.order_by(Goal.created_at.desc()).all()
    except OperationalError as e:
        logger.error(f"get_goals_by_user_id error: {e}")
        return []

def get_goal_by_id(goal_id, user_id=None):
    """
    获取指定ID的目标
    """
    try:
        query = Goal.query.filter_by(id=goal_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()
    except OperationalError as e:
        logger.error(f"get_goal_by_id error: {e}")
        return None

def create_goal(goal_data, user_id):
    """
    创建新目标
    """
    try:
        goal = Goal(
            user_id=user_id,
            title=goal_data.get('title'),
            description=goal_data.get('description'),
            category=goal_data.get('category'),
            color=goal_data.get('color', '#000000'),
            icon=goal_data.get('icon'),
            start_date=goal_data.get('start_date'),
            end_date=goal_data.get('end_date'),
            completed=goal_data.get('completed', False),
            progress=goal_data.get('progress', 0),
            goal_type=goal_data.get('goal_type', 'active')
        )
        
        db.session.add(goal)
        db.session.commit()
        return goal
    except OperationalError as e:
        logger.error(f"create_goal error: {e}")
        db.session.rollback()
        return None

def update_goal(goal_id, goal_data, user_id):
    """
    更新目标
    """
    try:
        goal = get_goal_by_id(goal_id, user_id)
        if not goal:
            return None
        
        for key, value in goal_data.items():
            if hasattr(goal, key):
                setattr(goal, key, value)
        
        db.session.commit()
        return goal
    except OperationalError as e:
        logger.error(f"update_goal error: {e}")
        db.session.rollback()
        return None

def delete_goal(goal_id, user_id):
    """
    删除目标
    """
    try:
        goal = get_goal_by_id(goal_id, user_id)
        if not goal:
            return False
        
        db.session.delete(goal)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.error(f"delete_goal error: {e}")
        db.session.rollback()
        return False

def calculate_goal_progress(goal_id):
    """
    计算目标完成进度
    """
    try:
        goal = Goal.query.filter_by(id=goal_id).first()
        if not goal:
            return False
        
        # 获取目标下的所有任务
        tasks = Task.query.filter_by(goal_id=goal_id).all()
        
        if not tasks:
            return True  # 没有任务时直接返回，保持当前进度
        
        # 计算已完成任务的比例
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.completed)
        
        if total_tasks > 0:
            progress = int((completed_tasks / total_tasks) * 100)
            goal.progress = progress
            
            # 如果所有任务都完成，标记目标为已完成
            if progress == 100:
                goal.completed = True
        
        db.session.commit()
        return True
    except OperationalError as e:
        logger.error(f"calculate_goal_progress error: {e}")
        db.session.rollback()
        return False

# ========== 令牌黑名单 ==========
def add_token_to_blacklist(token):
    """
    将令牌添加到黑名单
    """
    try:
        blacklisted_token = BlacklistedToken(token=token)
        db.session.add(blacklisted_token)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.error(f"add_token_to_blacklist error: {e}")
        db.session.rollback()
        return False

def is_token_blacklisted(token):
    """
    检查令牌是否在黑名单中
    """
    try:
        return BlacklistedToken.query.filter_by(token=token).first() is not None
    except OperationalError as e:
        logger.error(f"is_token_blacklisted error: {e}")
        return True  # 出错时当作黑名单处理，增加安全性
