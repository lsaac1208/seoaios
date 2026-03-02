#!/usr/bin/env python
"""
SEO AIOS 测试运行器
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['FLASK_ENV'] = 'testing'

def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("SEO AIOS 测试套件")
    print("=" * 60)
    print()

    tests_passed = 0
    tests_failed = 0

    # 测试1: 辅助函数
    print("[1/6] 测试辅助函数...")
    try:
        from app.utils.helpers import slugify, validate_url, get_domain
        from app.utils.filters import time_ago, domain_from_url

        # slugify测试
        assert slugify('Hello World') == 'hello-world'
        assert slugify('Test Page!') == 'test-page'

        # validate_url测试
        assert validate_url('https://example.com') == True
        assert validate_url('invalid') == False

        # get_domain测试
        assert get_domain('https://example.com/page') == 'example.com'

        print("  ✓ 辅助函数测试通过")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ 辅助函数测试失败: {e}")
        tests_failed += 1

    # 测试2: 过滤器
    print("[2/6] 测试过滤器...")
    try:
        from datetime import datetime, timedelta

        # time_ago测试
        now = datetime.utcnow()
        assert '刚刚' in time_ago(now)

        # domain_from_url测试
        assert domain_from_url('https://example.com/page') == 'example.com'

        print("  ✓ 过滤器测试通过")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ 过滤器测试失败: {e}")
        tests_failed += 1

    # 测试3: 模型
    print("[3/6] 测试数据库模型...")
    try:
        from app import create_app, db
        from app.models import User, Site, Article

        app = create_app('testing')
        with app.app_context():
            # 创建测试用户
            user = User(username='testuser', email='test@test.com')
            user.set_password('password123')
            db.session.add(user)

            # 创建测试站点
            site = Site(
                user_id=1,
                name='Test Site',
                domain='https://test.com'
            )
            db.session.add(site)

            # 创建测试文章
            article = Article(
                site_id=1,
                user_id=1,
                title='Test Article',
                slug='test-article',
                content='Test content',
                status='draft'
            )
            db.session.add(article)
            db.session.commit()

            # 验证
            assert User.query.count() == 1
            assert Site.query.count() == 1
            assert Article.query.count() == 1

            print("  ✓ 数据库模型测试通过")
            tests_passed += 1
    except Exception as e:
        print(f"  ✗ 数据库模型测试失败: {e}")
        tests_failed += 1

    # 测试4: 路由 - 首页
    print("[4/6] 测试路由 - 首页...")
    try:
        app = create_app('testing')
        client = app.test_client()

        response = client.get('/')
        assert response.status_code == 200

        response = client.get('/health')
        assert response.status_code == 200

        print("  ✓ 路由测试通过")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ 路由测试失败: {e}")
        tests_failed += 1

    # 测试5: 认证路由
    print("[5/6] 测试认证路由...")
    try:
        app = create_app('testing')
        client = app.test_client()

        # 测试登录页面
        response = client.get('/auth/login')
        assert response.status_code == 200

        # 测试注册页面
        response = client.get('/auth/register')
        assert response.status_code == 200

        # 测试新用户注册
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@test.com',
            'nickname': 'New',
            'password': 'pass123',
            'password2': 'pass123'
        }, follow_redirects=True)

        # 验证用户创建
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'new@test.com'

        print("  ✓ 认证路由测试通过")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ 认证路由测试失败: {e}")
        tests_failed += 1

    # 测试6: API路由
    print("[6/6] 测试API路由...")
    try:
        app = create_app('testing')
        client = app.test_client()

        response = client.get('/api/health')
        assert response.status_code == 200

        json_data = response.get_json()
        assert json_data['status'] == 'ok'

        print("  ✓ API路由测试通过")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ API路由测试失败: {e}")
        tests_failed += 1

    # 总结
    print()
    print("=" * 60)
    print(f"测试结果: {tests_passed} 通过, {tests_failed} 失败")
    print("=" * 60)

    return tests_failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
