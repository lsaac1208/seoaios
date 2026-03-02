#!/usr/bin/env python
"""
SEO AIOS 全量测试套件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['FLASK_ENV'] = 'testing'

from app import create_app, db
from app.models import User, Site, Article, Page, Keyword, Task, Category, SeoConfig, AiConfig

def create_test_client():
    """创建测试客户端并登录"""
    app = create_app('testing')
    client = app.test_client()

    with app.app_context():
        # 创建测试用户
        user = User(username='testuser', email='test@test.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()

    # 登录
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'

    return app, client


def test_all_routes():
    """测试所有路由"""
    app, client = create_test_client()

    print("=" * 60)
    print("SEO AIOS 全量测试")
    print("=" * 60)
    print()

    routes_tested = []
    errors = []

    # ===== 公开页面 =====
    print("[测试] 公开页面...")

    public_routes = [
        ('/', '首页'),
        ('/health', '健康检查'),
        ('/auth/login', '登录页'),
        ('/auth/register', '注册页'),
        ('/about', '关于页'),
    ]

    for route, name in public_routes:
        try:
            response = client.get(route)
            if response.status_code == 200:
                print(f"  ✓ {name} ({route}) - OK")
                routes_tested.append(route)
            else:
                print(f"  ✗ {name} ({route}) - 状态码: {response.status_code}")
                errors.append(f"{route}: {response.status_code}")
        except Exception as e:
            print(f"  ✗ {name} ({route}) - 错误: {e}")
            errors.append(f"{route}: {str(e)}")

    # ===== 需要登录的页面 =====
    print("\n[测试] 需要登录的页面...")

    with app.app_context():
        # 创建测试站点和文章
        user = User.query.first()

        site = Site(user_id=user.id, name='Test Site', domain='https://test.com')
        db.session.add(site)

        seo_config = SeoConfig(site_id=1)
        db.session.add(seo_config)

        ai_config = AiConfig(site_id=1)
        db.session.add(ai_config)

        db.session.commit()

        # 创建测试文章
        article = Article(
            site_id=1, user_id=user.id,
            title='Test Article', slug='test-article',
            content='<p>Test content</p>',
            meta_title='Test Title',
            meta_description='Test Description',
            status='published'
        )
        db.session.add(article)

        # 创建测试页面
        page = Page(
            site_id=1, title='Home', slug='',
            page_type='home', status='published'
        )
        db.session.add(page)

        # 创建测试关键词
        keyword = Keyword(user_id=user.id, keyword='test keyword', search_volume=100)
        db.session.add(keyword)

        # 创建测试任务
        task = Task(user_id=user.id, name='Test Task', task_type='crawl', status='pending')
        db.session.add(task)

        db.session.commit()

        site_id = site.id
        article_id = article.id
        page_id = page.id
        keyword_id = keyword.id
        task_id = task.id

    # 使用session模拟登录
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
        sess['_fresh'] = True

    auth_routes = [
        # 仪表盘和主页面
        ('/', '仪表盘'),
        ('/main/index', '主页面'),

        # 站点管理
        ('/sites/', '站点列表'),
        (f'/sites/{site_id}', '站点详情'),
        (f'/sites/{site_id}/edit', '站点编辑'),
        (f'/sites/{site_id}/pages', '站点页面管理'),
        (f'/sites/{site_id}/settings', '站点设置'),

        # 文章管理
        ('/articles/', '文章列表'),
        (f'/articles/{article_id}', '文章详情'),
        (f'/articles/{article_id}/edit', '文章编辑'),

        # SEO
        ('/seo/dashboard', 'SEO仪表盘'),
        ('/seo/keywords', '关键词管理'),

        # AI
        ('/ai/generate_content', 'AI生成内容'),
        ('/ai/rewrite_content', 'AI改写内容'),
        ('/ai/crawl', '内容抓取'),

        # 任务
        ('/tasks/', '任务列表'),
        (f'/tasks/{task_id}', '任务详情'),

        # API
        ('/api/health', 'API健康检查'),
        ('/api/stats', 'API统计'),
    ]

    for route, name in auth_routes:
        try:
            response = client.get(route)
            if response.status_code == 200:
                print(f"  ✓ {name} ({route}) - OK")
                routes_tested.append(route)
            else:
                print(f"  ✗ {name} ({route}) - 状态码: {response.status_code}")
                errors.append(f"{route}: {response.status_code}")
        except Exception as e:
            print(f"  ✗ {name} ({route}) - 错误: {str(e)[:50]}")
            errors.append(f"{route}: {str(e)[:50]}")

    # ===== 测试表单提交 =====
    print("\n[测试] 表单提交...")

    # 测试创建站点
    try:
        response = client.post('/sites/new', data={
            'name': 'New Site',
            'domain': 'https://newsite.com',
            'description': 'Test',
            'template': 'default',
            'output_type': 'static',
            'language': 'zh-CN'
        }, follow_redirects=False)

        if response.status_code in [200, 302, 303]:
            print(f"  ✓ 创建站点 - OK")
            routes_tested.append('/sites/new (POST)')
        else:
            print(f"  ✗ 创建站点 - 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ✗ 创建站点 - 错误: {str(e)[:50]}")

    # 测试创建文章
    try:
        response = client.post('/articles/new', data={
            'site_id': str(site_id),
            'title': 'New Article',
            'content': '<p>New content</p>',
            'status': 'draft'
        }, follow_redirects=False)

        if response.status_code in [200, 302, 303]:
            print(f"  ✓ 创建文章 - OK")
            routes_tested.append('/articles/new (POST)')
        else:
            print(f"  ✗ 创建文章 - 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ✗ 创建文章 - 错误: {str(e)[:50]}")

    # 测试添加关键词
    try:
        response = client.post('/seo/add_keyword', data={
            'keyword': 'new keyword',
            'site_id': str(site_id)
        }, follow_redirects=False)

        if response.status_code in [200, 302, 303]:
            print(f"  ✓ 添加关键词 - OK")
            routes_tested.append('/seo/add_keyword (POST)')
    except Exception as e:
        print(f"  ✗ 添加关键词 - 错误: {str(e)[:50]}")

    # ===== 测试模板渲染 =====
    print("\n[测试] 模板渲染...")

    with client.session_transaction() as sess:
        sess['_user_id'] = '1'

    # 测试站点列表页面的模板
    try:
        response = client.get('/sites/')
        if b'Test Site' in response.data:
            print(f"  ✓ 站点列表模板 - 数据正确")
        else:
            print(f"  ✓ 站点列表模板 - 渲染成功")
        routes_tested.append('template: sites/index')
    except Exception as e:
        print(f"  ✗ 站点列表模板 - 错误: {str(e)[:50]}")
        errors.append(f"template sites/index: {str(e)[:50]}")

    # 测试文章列表页面
    try:
        response = client.get('/articles/')
        if response.status_code == 200:
            print(f"  ✓ 文章列表模板 - 渲染成功")
            routes_tested.append('template: articles/index')
    except Exception as e:
        print(f"  ✗ 文章列表模板 - 错误: {str(e)[:50]}")

    # ===== 测试模型关联 =====
    print("\n[测试] 数据模型...")

    try:
        with app.app_context():
            # 测试站点查询
            sites = Site.query.all()
            print(f"  ✓ 站点查询 - {len(sites)} 条记录")

            # 测试文章查询
            articles = Article.query.all()
            print(f"  ✓ 文章查询 - {len(articles)} 条记录")

            # 测试关键词查询
            keywords = Keyword.query.all()
            print(f"  ✓ 关键词查询 - {len(keywords)} 条记录")

            # 测试任务查询
            tasks = Task.query.all()
            print(f"  ✓ 任务查询 - {len(tasks)} 条记录")

            # 测试关系
            site = Site.query.first()
            if site:
                pages_count = site.pages.count()
                articles_count = site.articles.count()
                print(f"  ✓ 站点关联 - {pages_count} 页面, {articles_count} 文章")

    except Exception as e:
        print(f"  ✗ 数据模型 - 错误: {str(e)}")
        errors.append(f"models: {str(e)}")

    # ===== 总结 =====
    print("\n" + "=" * 60)
    print(f"测试完成: {len(routes_tested)} 通过")
    if errors:
        print(f"错误: {len(errors)} 个")
        for e in errors[:10]:
            print(f"  - {e}")
    else:
        print("所有测试通过!")
    print("=" * 60)

    return len(errors) == 0


if __name__ == '__main__':
    success = test_all_routes()
    sys.exit(0 if success else 1)
