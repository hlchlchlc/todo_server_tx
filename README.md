# FlowTodo 后端服务

FlowTodo 是一个任务管理应用，帮助用户高效地管理任务和目标。本项目是 FlowTodo 的后端服务，基于微信云托管的 Flask 框架开发。

## 功能特点

- 用户管理：注册、登录、身份验证
- 任务管理：创建、查询、更新、删除任务
- 目标管理：创建和管理长期/活跃目标
- 任务与目标的关联
- 任务优先级、完成度、时间评估等功能
- 支持重复任务
- 支持任务标签

## 技术栈

- Web框架：Flask
- 数据库：MySQL
- ORM：SQLAlchemy
- 认证：JWT (JSON Web Token)
- 部署：微信云托管

## API 概览

### 认证 API

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新访问令牌
- `POST /api/auth/logout` - 退出登录
- `GET /api/auth/me` - 获取当前用户信息

### 任务 API

- `GET /api/tasks` - 获取所有任务
- `POST /api/tasks` - 创建新任务
- `GET /api/tasks/{task_id}` - 获取单个任务
- `PUT /api/tasks/{task_id}` - 更新任务
- `DELETE /api/tasks/{task_id}` - 删除任务
- `PATCH /api/tasks/{task_id}/toggle-complete` - 切换任务完成状态

### 目标 API

- `GET /api/goals` - 获取所有目标
- `POST /api/goals` - 创建新目标
- `GET /api/goals/{goal_id}` - 获取单个目标
- `PUT /api/goals/{goal_id}` - 更新目标
- `DELETE /api/goals/{goal_id}` - 删除目标
- `GET /api/goals/{goal_id}/tasks` - 获取目标下的所有任务

## 本地运行

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 设置环境变量：
   ```
   export MYSQL_USERNAME=your_db_username
   export MYSQL_PASSWORD=your_db_password
   export MYSQL_ADDRESS=127.0.0.1:3306
   export JWT_SECRET_KEY=your_secret_key
   ```

3. 运行应用：
   ```
   python run.py
   ```

## 微信云托管部署

1. 前往[微信云托管](https://cloud.weixin.qq.com/)
2. 选择"新建环境"
3. 上传本项目代码
4. 配置环境变量：
   - MYSQL_USERNAME
   - MYSQL_PASSWORD
   - MYSQL_ADDRESS
   - JWT_SECRET_KEY
5. 部署服务

## 数据库设计

应用使用了多个数据表来存储用户、任务和目标信息，详细结构请参考代码中的模型定义。

## 开发说明

- 使用 JWT 进行用户认证
- 所有 API 响应遵循统一的格式
- 错误处理遵循 RESTful API 最佳实践

## 安全注意事项

- 所有密码使用 bcrypt 算法哈希处理
- API 使用 JWT 认证保护
- 实现了令牌黑名单机制

## 许可证

MIT
