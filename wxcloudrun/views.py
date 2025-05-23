from flask import render_template, jsonify
from run import app
from wxcloudrun.auth import auth_bp
from wxcloudrun.tasks import tasks_bp
from wxcloudrun.goals import goals_bp
from wxcloudrun.response import make_err_response, make_succ_empty_response, make_succ_response

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(goals_bp)

@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': {'code': 'not_found', 'message': 'Resource not found'}}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': {'code': 'server_error', 'message': 'Internal server error'}}), 500

# 健康检查接口（云托管需要）
@app.route('/api/health', methods=['GET'])
def health_check():
    return make_succ_response('ok')

# CORS处理
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,PATCH,OPTIONS'
    return response
