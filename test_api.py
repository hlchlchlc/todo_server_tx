#!/usr/bin/env python3
import requests
import json
import time
import random
import string

# API基础URL
BASE_URL = "https://flowserver-163620-5-1360594735.sh.run.tcloudbase.com"

# 用于存储访问令牌
access_token = None
refresh_token = None

# 随机生成测试用户名和密码
def generate_random_string(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

test_username = f"testuser_{generate_random_string()}"
test_email = f"{test_username}@example.com"
test_password = generate_random_string(12)

# 打印分隔线
def print_separator(title):
    print("\n" + "=" * 50)
    print(f" {title} ")
    print("=" * 50)

# 打印请求和响应信息
def print_request_response(method, url, data=None, response=None):
    print(f"\n> {method} {url}")
    if data:
        print(f"> 请求数据: {json.dumps(data, ensure_ascii=False)}")
    if response:
        print(f"> 状态码: {response.status_code}")
        try:
            print(f"> 响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"> 响应内容: {response.text}")

# 1. 测试用户注册
def test_register():
    print_separator("测试用户注册")
    
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "username": test_username,
        "email": test_email,
        "password": test_password
    }
    
    response = requests.post(url, json=data)
    print_request_response("POST", url, data, response)
    
    assert response.status_code == 201, "用户注册失败"
    return response.json()

# 2. 测试用户登录
def test_login():
    global access_token, refresh_token
    
    print_separator("测试用户登录")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": test_username,
        "password": test_password
    }
    
    response = requests.post(url, json=data)
    print_request_response("POST", url, data, response)
    
    assert response.status_code == 200, "用户登录失败"
    
    result = response.json()
    access_token = result.get("access_token")
    refresh_token = result.get("refresh_token")
    
    assert access_token, "未获取到访问令牌"
    assert refresh_token, "未获取到刷新令牌"
    
    return result

# 3. 测试获取当前用户信息
def test_get_me():
    print_separator("测试获取用户信息")
    
    url = f"{BASE_URL}/api/auth/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print_request_response("GET", url, None, response)
    
    assert response.status_code == 200, "获取用户信息失败"
    return response.json()

# 4. 测试创建目标
def test_create_goal():
    print_separator("测试创建目标")
    
    url = f"{BASE_URL}/api/goals"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "title": "测试目标",
        "description": "这是一个测试目标",
        "category": "工作",
        "color": "#FF5733",
        "goal_type": "active"
    }
    
    response = requests.post(url, json=data, headers=headers)
    print_request_response("POST", url, data, response)
    
    assert response.status_code == 201, "创建目标失败"
    return response.json()

# 5. 测试获取所有目标
def test_get_goals():
    print_separator("测试获取所有目标")
    
    url = f"{BASE_URL}/api/goals"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print_request_response("GET", url, None, response)
    
    assert response.status_code == 200, "获取目标列表失败"
    return response.json()

# 6. 测试创建任务
def test_create_task(goal_id=None):
    print_separator("测试创建任务")
    
    url = f"{BASE_URL}/api/tasks"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "title": "测试任务",
        "priority": "high",
        "estimated_time": 60,
        "tags": ["测试", "重要"],
        "notes": "这是一个测试任务",
        "enthusiasm": 4,
        "difficulty": 3,
        "importance": 5
    }
    
    if goal_id:
        data["goal_id"] = goal_id
    
    response = requests.post(url, json=data, headers=headers)
    print_request_response("POST", url, data, response)
    
    assert response.status_code == 201, "创建任务失败"
    return response.json()

# 7. 测试获取所有任务
def test_get_tasks():
    print_separator("测试获取所有任务")
    
    url = f"{BASE_URL}/api/tasks"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print_request_response("GET", url, None, response)
    
    assert response.status_code == 200, "获取任务列表失败"
    return response.json()

# 8. 测试更新任务
def test_update_task(task_id):
    print_separator("测试更新任务")
    
    url = f"{BASE_URL}/api/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "title": "已更新的测试任务",
        "priority": "medium",
        "notes": "这是一个已更新的测试任务"
    }
    
    response = requests.put(url, json=data, headers=headers)
    print_request_response("PUT", url, data, response)
    
    assert response.status_code == 200, "更新任务失败"
    return response.json()

# 9. 测试切换任务完成状态
def test_toggle_task_complete(task_id):
    print_separator("测试切换任务完成状态")
    
    url = f"{BASE_URL}/api/tasks/{task_id}/toggle-complete"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.patch(url, headers=headers)
    print_request_response("PATCH", url, None, response)
    
    assert response.status_code == 200, "切换任务完成状态失败"
    return response.json()

# 10. 测试刷新令牌
def test_refresh_token():
    global access_token
    
    print_separator("测试刷新令牌")
    
    url = f"{BASE_URL}/api/auth/refresh"
    headers = {"Authorization": f"Bearer {refresh_token}"}
    
    response = requests.post(url, headers=headers)
    print_request_response("POST", url, None, response)
    
    assert response.status_code == 200, "刷新令牌失败"
    
    result = response.json()
    access_token = result.get("access_token")
    
    assert access_token, "未获取到新的访问令牌"
    return result

# 11. 测试退出登录
def test_logout():
    print_separator("测试退出登录")
    
    url = f"{BASE_URL}/api/auth/logout"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.post(url, headers=headers)
    print_request_response("POST", url, None, response)
    
    assert response.status_code == 204, "退出登录失败"
    return True

# 主测试流程
def run_tests():
    print("\n开始测试FlowTodo API...\n")
    print(f"测试用户: {test_username}")
    print(f"测试邮箱: {test_email}")
    print(f"测试密码: {test_password}")
    
    try:
        # 用户认证测试
        test_register()
        test_login()
        test_get_me()
        
        # 目标管理测试
        goal = test_create_goal()
        goals = test_get_goals()
        goal_id = goal.get("id")
        
        # 任务管理测试
        task = test_create_task(goal_id)
        tasks = test_get_tasks()
        task_id = task.get("id")
        
        test_update_task(task_id)
        test_toggle_task_complete(task_id)
        
        # 令牌管理测试
        test_refresh_token()
        test_logout()
        
        print("\n\n所有测试通过! FlowTodo API 工作正常。")
    except AssertionError as e:
        print(f"\n\n测试失败: {e}")
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")

if __name__ == "__main__":
    run_tests() 