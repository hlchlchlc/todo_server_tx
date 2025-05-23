# FlowTodo 后端开发文档

本文档详细说明了FlowTodo应用后端的设计和实现方案，包括API接口、数据库设计、认证机制等内容。

## 1. 技术栈

FlowTodo后端采用以下技术栈：

- **Web框架**：Flask 
- **数据库**：MySQL
- **ORM**：SQLAlchemy
- **认证**：JWT (JSON Web Token)
- **API文档**：Swagger/OpenAPI
- **数据库迁移**：Flask-Migrate

## 2. 项目结构

```
flowtodo-backend/
├── app/
│   ├── __init__.py       # 应用初始化
│   ├── config.py         # 配置文件
│   ├── models/           # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py       # 用户模型
│   │   ├── task.py       # 任务模型
│   │   └── goal.py       # 目标模型
│   ├── api/              # API路由
│   │   ├── __init__.py
│   │   ├── auth.py       # 认证相关路由
│   │   ├── tasks.py      # 任务相关路由
│   │   └── goals.py      # 目标相关路由
│   ├── schemas/          # 数据验证和序列化
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   └── goal.py
│   └── utils/            # 工具函数
│       ├── __init__.py
│       └── helpers.py
├── migrations/           # 数据库迁移文件
├── tests/                # 测试
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_tasks.py
│   └── test_goals.py
├── .env.example          # 环境变量示例
├── .gitignore
├── requirements.txt      # 依赖包
├── run.py                # 应用入口
└── README.md             # 项目说明
```

## 3. 数据库设计

### 3.1 用户表 (users)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 主键，自增 |
| username | VARCHAR(50) | 用户名，唯一 |
| email | VARCHAR(100) | 邮箱，唯一 |
| password_hash | VARCHAR(255) | 密码哈希 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| last_login | DATETIME | 最后登录时间 |
| is_active | BOOLEAN | 账户是否激活 |

### 3.2 任务表 (tasks)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | VARCHAR(36) | 主键，UUID |
| user_id | INT | 外键，关联users表 |
| goal_id | VARCHAR(36) | 外键，关联goals表，可为NULL |
| title | VARCHAR(255) | 任务标题 |
| completed | BOOLEAN | 是否已完成 |
| due_date | DATETIME | 截止日期，可为NULL |
| priority | ENUM | 优先级：high, medium, low |
| estimated_time | INT | 预计时间(分钟) |
| actual_time | INT | 实际时间(分钟) |
| created_at | DATETIME | 创建时间 |
| notes | TEXT | 备注，可为NULL |
| expected_outcome | TEXT | 预期收益，可为NULL |
| enthusiasm | TINYINT | 热情度(1-5) |
| difficulty | TINYINT | 困难度(1-5) |
| importance | TINYINT | 重要性(1-5) |
| is_repeating | BOOLEAN | 是否为重复任务 |
| repeat_frequency | ENUM | 重复频率：daily, weekly, monthly, yearly, custom |
| repeat_interval | INT | 重复间隔 |
| repeat_end_date | DATETIME | 重复结束日期 |
| repeat_count | INT | 重复次数 |
| parent_task_id | VARCHAR(36) | 父任务ID |
| custom_week_days | VARCHAR(20) | 自定义每周重复的星期几，JSON格式 |

### 3.3 目标表 (goals)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | VARCHAR(36) | 主键，UUID |
| user_id | INT | 外键，关联users表 |
| title | VARCHAR(255) | 目标标题 |
| description | TEXT | 目标描述，可为NULL |
| category | VARCHAR(50) | 目标分类，可为NULL |
| color | VARCHAR(20) | 颜色 |
| icon | VARCHAR(50) | 图标，可为NULL |
| start_date | DATETIME | 开始日期，可为NULL |
| end_date | DATETIME | 结束日期，可为NULL |
| completed | BOOLEAN | 是否已完成 |
| progress | TINYINT | 进度(0-100) |
| created_at | DATETIME | 创建时间 |
| goal_type | ENUM | 目标类型：long_term, active |

### 3.4 任务标签表 (task_tags)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 主键，自增 |
| task_id | VARCHAR(36) | 外键，关联tasks表 |
| tag_name | VARCHAR(50) | 标签名称 |

## 4. API设计

### 4.1 认证API

#### 4.1.1 用户注册

- **URL**: `/api/auth/register`
- **方法**: `POST`
- **描述**: 创建新用户
- **请求体**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **响应**:
  ```json
  {
    "id": "integer",
    "username": "string",
    "email": "string",
    "created_at": "string"
  }
  ```

#### 4.1.2 用户登录

- **URL**: `/api/auth/login`
- **方法**: `POST`
- **描述**: 用户登录并获取访问令牌
- **请求体**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **响应**:
  ```json
  {
    "access_token": "string",
    "refresh_token": "string",
    "user": {
      "id": "integer",
      "username": "string",
      "email": "string"
    }
  }
  ```

#### 4.1.3 刷新令牌

- **URL**: `/api/auth/refresh`
- **方法**: `POST`
- **描述**: 使用刷新令牌获取新的访问令牌
- **请求头**: `Authorization: Bearer <refresh_token>`
- **响应**:
  ```json
  {
    "access_token": "string"
  }
  ```

#### 4.1.4 退出登录

- **URL**: `/api/auth/logout`
- **方法**: `POST`
- **描述**: 使当前令牌失效
- **请求头**: `Authorization: Bearer <access_token>`
- **响应**: `204 No Content`

### 4.2 任务API

#### 4.2.1 获取所有任务

- **URL**: `/api/tasks`
- **方法**: `GET`
- **描述**: 获取当前用户的所有任务
- **请求头**: `Authorization: Bearer <access_token>`
- **查询参数**:
  - `filter`: 过滤类型 (all, today, week, completed, upcoming, unscheduled)
  - `sort`: 排序方式 (dueDate, createdAt, priority, alphabetical)
  - `goal_id`: 按目标ID筛选
- **响应**:
  ```json
  [
    {
      "id": "string",
      "title": "string",
      "goal_id": "string",
      "completed": "boolean",
      "due_date": "string",
      "priority": "string",
      "estimated_time": "integer",
      "actual_time": "integer",
      "created_at": "string",
      "tags": ["string"],
      "notes": "string",
      "expected_outcome": "string",
      "enthusiasm": "integer",
      "difficulty": "integer",
      "importance": "integer",
      "is_repeating": "boolean",
      "repeat_frequency": "string",
      "repeat_interval": "integer",
      "repeat_end_date": "string",
      "repeat_count": "integer",
      "parent_task_id": "string",
      "custom_week_days": ["integer"]
    }
  ]
  ```

#### 4.2.2 创建任务

- **URL**: `/api/tasks`
- **方法**: `POST`
- **描述**: 创建新任务
- **请求头**: `Authorization: Bearer <access_token>`
- **请求体**: 任务数据（同上面的响应格式，但不包含id和created_at）
- **响应**: 创建的任务数据

#### 4.2.3 获取单个任务

- **URL**: `/api/tasks/{task_id}`
- **方法**: `GET`
- **描述**: 获取指定ID的任务
- **请求头**: `Authorization: Bearer <access_token>`
- **响应**: 任务数据

#### 4.2.4 更新任务

- **URL**: `/api/tasks/{task_id}`
- **方法**: `PUT`
- **描述**: 更新指定ID的任务
- **请求头**: `Authorization: Bearer <access_token>`
- **请求体**: 任务数据
- **响应**: 更新后的任务数据

#### 4.2.5 删除任务

- **URL**: `/api/tasks/{task_id}`
- **方法**: `DELETE`
- **描述**: 删除指定ID的任务
- **请求头**: `Authorization: Bearer <access_token>`
- **响应**: `204 No Content`

#### 4.2.6 标记任务为已完成/未完成

- **URL**: `/api/tasks/{task_id}/toggle-complete`
- **方法**: `PATCH`
- **描述**: 切换任务的完成状态
- **请求头**: `Authorization: Bearer <access_token>`
- **响应**: 更新后的任务数据

### 4.3 目标API

#### 4.3.1 获取所有目标

- **URL**: `/api/goals`
- **方法**: `GET`
- **描述**: 获取当前用户的所有目标
- **请求头**: `Authorization: Bearer <access_token>`
- **查询参数**:
  - `type`: 目标类型 (long_term, active, all)
- **响应**:
  ```json
  [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "category": "string",
      "color": "string",
      "icon": "string",
      "start_date": "string",
      "end_date": "string",
      "completed": "boolean",
      "progress": "integer",
      "created_at": "string",
      "goal_type": "string"
    }
  ]
  ```

#### 4.3.2 创建目标

- **URL**: `/api/goals`
- **方法**: `POST`
- **描述**: 创建新目标
- **请求头**: `Authorization: Bearer <access_token>`
- **请求体**: 目标数据（同上面的响应格式，但不包含id和created_at）
- **响应**: 创建的目标数据

#### 4.3.3 获取单个目标

- **URL**: `/api/goals/{goal_id}`
- **方法**: `GET`
- **描述**: 获取指定ID的目标
- **请求头**: `Authorization: Bearer <access_token>`
- **响应**: 目标数据

#### 4.3.4 更新目标

- **URL**: `/api/goals/{goal_id}`
- **方法**: `PUT`
- **描述**: 更新指定ID的目标
- **请求头**: `Authorization: Bearer <access_token>`
- **请求体**: 目标数据
- **响应**: 更新后的目标数据

#### 4.3.5 删除目标

- **URL**: `/api/goals/{goal_id}`
- **方法**: `DELETE`
- **描述**: 删除指定ID的目标
- **请求头**: `Authorization: Bearer <access_token>`
- **响应**: `204 No Content`

#### 4.3.6 获取目标下的所有任务

- **URL**: `/api/goals/{goal_id}/tasks`
- **方法**: `GET`
- **描述**: 获取指定目标下的所有任务
- **请求头**: `Authorization: Bearer <access_token>`
- **响应**: 任务数组

## 5. 认证机制

FlowTodo后端使用JWT（JSON Web Token）进行认证，流程如下：

1. 用户通过`/api/auth/login`接口登录，获取`access_token`和`refresh_token`
2. 客户端在后续请求中，通过`Authorization`头部携带`access_token`
3. `access_token`有效期较短（例如30分钟），过期后需要使用`refresh_token`获取新的`access_token`
4. `refresh_token`有效期较长（例如7天），用于在`access_token`过期后获取新的令牌
5. 用户退出登录时，应调用`/api/auth/logout`接口使当前令牌失效

## 6. 数据同步策略

为了支持离线使用和数据同步，FlowTodo采用以下同步策略：

1. 客户端在本地存储任务和目标数据的副本
2. 客户端在有网络连接时，定期与服务器同步数据
3. 每个数据项都有`updated_at`字段，用于解决冲突
4. 同步过程中，较新的数据会覆盖较旧的数据
5. 客户端应记录离线期间的更改，并在恢复网络连接后进行同步

## 7. 错误处理

API返回的错误格式统一为：

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

常见HTTP状态码：

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `204 No Content`: 请求成功，无返回内容
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证或认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 请求格式正确但语义错误
- `500 Internal Server Error`: 服务器内部错误

```

## 9. 安全性考虑

1. 所有密码使用bcrypt算法哈希存储
2. API使用HTTPS加密传输
3. JWT令牌使用强密钥签名
4. 实现请求速率限制，防止暴力攻击
5. 验证所有用户输入，防止SQL注入和XSS攻击
6. 实现CORS策略，限制跨域请求
7. 定期轮换密钥和令牌

