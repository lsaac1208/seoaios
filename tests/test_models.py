import pytest
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Site, Article, Page, Keyword, Task, SeoConfig, AiConfig, Category


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建测试CLI运行器"""
    return app.test_cli_runner()


@pytest.fixture
def authenticated_client(client, app):
    """创建已认证的测试客户端"""
    with app.app_context():
        # 创建测试用户
        user = User(username='testuser', email='test@example.com', nickname='Test User')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()

    # 登录
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)

    return client


class TestUserModel:
    """用户模型测试"""

    def test_create_user(self, app):
        """测试创建用户"""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == 'test'
            assert user.check_password('password123')
            assert not user.check_password('wrongpassword')

    def test_password_hashing(self, app):
        """测试密码哈希"""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            user.set_password('mypassword')

            assert user.password_hash is not None
            assert user.password_hash != 'mypassword'
            assert user.check_password('mypassword')
            assert not user.check_password('wrongpassword')

    def test_user_repr(self, app):
        """测试用户字符串表示"""
        with app.app_context():
            user = User(username='testuser', email='test@test.com')
            assert 'testuser' in repr(user)


class TestSiteModel:
    """站点模型测试"""

    def test_create_site(self, app):
        """测试创建站点"""
        with app.app_context():
            # 先创建用户
            user = User(username='owner', email='owner@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            site = Site(
                user_id=user.id,
                name='Test Site',
                domain='https://test.com',
                description='Test description',
                keywords='seo,test,python'
            )
            db.session.add(site)
            db.session.commit()

            assert site.id is not None
            assert site.name == 'Test Site'
            assert 'seo' in site.get_keywords_list()

    def test_get_keywords_list(self, app):
        """测试获取关键词列表"""
        with app.app_context():
            user = User(username='owner2', email='owner2@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            site = Site(
                user_id=user.id,
                name='Test',
                domain='https://test2.com',
                keywords='keyword1, keyword2, keyword3'
            )
            db.session.add(site)
            db.session.commit()

            keywords = site.get_keywords_list()
            assert len(keywords) == 3
            assert 'keyword1' in keywords


class TestArticleModel:
    """文章模型测试"""

    def test_create_article(self, app):
        """测试创建文章"""
        with app.app_context():
            # 创建用户和站点
            user = User(username='author', email='author@test.com')
            user.set_password('password')
            db.session.add(user)

            site = Site(user_id=1, name='Site', domain='https://site.com')
            db.session.add(site)
            db.session.commit()

            article = Article(
                site_id=site.id,
                user_id=user.id,
                title='Test Article',
                slug='test-article',
                content='This is test content with some words',
                meta_title='Test Title',
                meta_description='Test Description',
                status='draft'
            )
            db.session.add(article)
            db.session.commit()

            assert article.id is not None
            assert article.title == 'Test Article'
            assert article.status == 'draft'

    def test_get_tags_list(self, app):
        """测试获取标签列表"""
        with app.app_context():
            user = User(username='author2', email='author2@test.com')
            user.set_password('password')
            db.session.add(user)

            site = Site(user_id=1, name='Site2', domain='https://site2.com')
            db.session.add(site)
            db.session.commit()

            article = Article(
                site_id=site.id,
                user_id=user.id,
                title='Test',
                slug='test',
                content='content',
                tags='tag1, tag2, tag3'
            )
            db.session.add(article)
            db.session.commit()

            tags = article.get_tags_list()
            assert len(tags) == 3
            assert 'tag1' in tags


class TestKeywordModel:
    """关键词模型测试"""

    def test_create_keyword(self, app):
        """测试创建关键词"""
        with app.app_context():
            user = User(username='user3', email='user3@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            keyword = Keyword(
                user_id=user.id,
                keyword='python programming',
                search_volume=1000,
                difficulty=45.5,
                status='active'
            )
            db.session.add(keyword)
            db.session.commit()

            assert keyword.id is not None
            assert keyword.keyword == 'python programming'
            assert keyword.search_volume == 1000


class TestTaskModel:
    """任务模型测试"""

    def test_create_task(self, app):
        """测试创建任务"""
        with app.app_context():
            user = User(username='user4', email='user4@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            task = Task(
                user_id=user.id,
                name='Test Task',
                task_type='crawl',
                status='pending',
                config={'url': 'https://example.com'}
            )
            db.session.add(task)
            db.session.commit()

            assert task.id is not None
            assert task.name == 'Test Task'
            assert task.task_type == 'crawl'
            assert task.get_config()['url'] == 'https://example.com'

    def test_set_config(self, app):
        """测试设置任务配置"""
        with app.app_context():
            user = User(username='user5', email='user5@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            task = Task(user_id=user.id, name='Task', task_type='generate')
            task.set_config({'keywords': ['seo', 'ai'], 'count': 5})
            db.session.add(task)
            db.session.commit()

            config = task.get_config()
            assert config['keywords'] == ['seo', 'ai']
            assert config['count'] == 5


class TestAuthRoutes:
    """认证路由测试"""

    def test_login_page(self, client):
        """测试登录页面"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_register_page(self, client):
        """测试注册页面"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'register' in response.data.lower()

    def test_register_new_user(self, client, app):
        """测试新用户注册"""
        with app.app_context():
            response = client.post('/auth/register', data={
                'username': 'newuser',
                'email': 'newuser@test.com',
                'nickname': 'New User',
                'password': 'password123',
                'password2': 'password123'
            }, follow_redirects=True)

            assert response.status_code == 200

            # 验证用户已创建
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@test.com'

    def test_register_password_mismatch(self, client):
        """测试密码不匹配"""
        response = client.post('/auth/register', data={
            'username': 'testuser2',
            'email': 'test2@test.com',
            'password': 'password123',
            'password2': 'different'
        })

        assert response.status_code != 200 or b'password' in response.data.lower()

    def test_login_success(self, client, app):
        """测试成功登录"""
        with app.app_context():
            # 先创建用户
            user = User(username='logintest', email='login@test.com')
            user.set_password('password123')
            db.session.add(user)
            db.commit()

            response = client.post('/auth/login', data={
                'username': 'logintest',
                'password': 'password123'
            }, follow_redirects=True)

            assert response.status_code == 200

    def test_login_wrong_password(self, client, app):
        """测试错误密码"""
        with app.app_context():
            user = User(username='login2', email='login2@test.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

            response = client.post('/auth/login', data={
                'username': 'login2',
                'password': 'wrongpassword'
            })

            assert b'error' in response.data.lower() or b'wrong' in response.data.lower()


class TestMainRoutes:
    """主路由测试"""

    def test_index_page(self, client):
        """测试首页"""
        response = client.get('/')
        assert response.status_code == 200

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get('/health')
        assert response.status_code == 200
        assert b'ok' in response.data.lower()


class TestSiteRoutes:
    """站点路由测试"""

    def test_sites_list_requires_auth(self, client):
        """测试站点列表需要登录"""
        response = client.get('/sites/')
        # 会重定向到登录页
        assert response.status_code in [301, 302, 303]

    def test_create_site(self, authenticated_client, app):
        """测试创建站点"""
        with app.app_context():
            response = authenticated_client.post('/sites/new', data={
                'name': 'New Test Site',
                'domain': 'https://newtest.com',
                'description': 'A test site',
                'keywords': 'test, seo',
                'template': 'default',
                'output_type': 'static',
                'language': 'zh-CN'
            }, follow_redirects=True)

            assert response.status_code == 200

            # 验证站点已创建
            site = Site.query.filter_by(domain='https://newtest.com').first()
            assert site is not None
            assert site.name == 'New Test Site'

    def test_site_detail(self, authenticated_client, app):
        """测试站点详情"""
        with app.app_context():
            # 创建站点
            user = User.query.first()
            site = Site(
                user_id=user.id,
                name='Detail Test Site',
                domain='https://detailtest.com'
            )
            db.session.add(site)
            db.session.commit()

            response = authenticated_client.get(f'/sites/{site.id}')
            assert response.status_code == 200
            assert b'Detail Test Site' in response.data


class TestArticleRoutes:
    """文章路由测试"""

    def test_articles_list(self, authenticated_client):
        """测试文章列表"""
        response = authenticated_client.get('/articles/')
        assert response.status_code == 200

    def test_create_article(self, authenticated_client, app):
        """测试创建文章"""
        with app.app_context():
            # 创建站点
            user = User.query.first()
            site = Site(user_id=user.id, name='Test', domain='https://test.com')
            db.session.add(site)
            db.session.commit()

            response = authenticated_client.post('/articles/new', data={
                'site_id': site.id,
                'title': 'Test Article Title',
                'content': 'This is test content for the article.',
                'status': 'draft'
            }, follow_redirects=True)

            assert response.status_code == 200

            # 验证文章已创建
            article = Article.query.filter_by(title='Test Article Title').first()
            assert article is not None


class TestApiRoutes:
    """API路由测试"""

    def test_health_api(self, client):
        """测试健康检查API"""
        response = client.get('/api/health')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'ok'

    def test_stats_api_requires_auth(self, client):
        """测试统计API需要认证"""
        response = client.get('/api/stats')
        assert response.status_code in [401, 403]

    def test_stats_api(self, authenticated_client, app):
        """测试统计API"""
        with app.app_context():
            response = authenticated_client.get('/api/stats')
            assert response.status_code == 200
            json_data = response.get_json()
            assert 'sites_count' in json_data
            assert 'articles_count' in json_data


class TestHelperFunctions:
    """辅助函数测试"""

    def test_slugify(self):
        """测试slugify函数"""
        from app.utils.helpers import slugify

        assert slugify('Hello World') == 'hello-world'
        assert slugify('Test Page!') == 'test-page'
        assert slugify('关键词测试') == '关键词测试'
        assert slugify('') == ''

    def test_validate_url(self):
        """测试URL验证"""
        from app.utils.helpers import validate_url

        assert validate_url('https://example.com') == True
        assert validate_url('http://test.com') == True
        assert validate_url('invalid') == False
        assert validate_url('') == False

    def test_get_domain(self):
        """测试获取域名"""
        from app.utils.helpers import get_domain

        assert get_domain('https://example.com/page') == 'example.com'
        assert get_domain('http://test.com/path?query=1') == 'test.com'
        assert get_domain('') == ''

    def test_extract_keywords(self):
        """测试关键词提取"""
        from app.utils.helpers import extract_keywords

        text = "Python is a great programming language. Python is popular."
        keywords = extract_keywords(text, min_length=3, max_keywords=5)

        assert 'python' in keywords

    def test_calculate_readability(self):
        """测试可读性计算"""
        from app.utils.helpers import calculate_readability

        # 简单短文本
        score1 = calculate_readability("This is a short sentence.")
        assert 0 <= score1 <= 100

        # 长文本
        long_text = "This is a test. " * 50
        score2 = calculate_readability(long_text)
        assert 0 <= score2 <= 100

    def test_calculate_keyword_density(self):
        """测试关键词密度计算"""
        from app.utils.helpers import calculate_keyword_density

        text = "Python is a great programming language. Python is popular."
        density = calculate_keyword_density(text, "Python")
        assert density > 0

        density2 = calculate_keyword_density(text, "notexist")
        assert density2 == 0.0

    def test_generate_meta_description(self):
        """测试生成Meta描述"""
        from app.utils.helpers import generate_meta_description

        content = "This is a long content " * 20
        meta = generate_meta_description(content, max_length=160)
        assert len(meta) <= 163  # 160 + '...'

        # 测试空内容
        assert generate_meta_description("") == ""

    def test_format_file_size(self):
        """测试文件大小格式化"""
        from app.utils.helpers import format_file_size

        assert format_file_size(0) == '0 B'
        assert 'B' in format_file_size(100)
        assert 'KB' in format_file_size(2048)
        assert 'MB' in format_file_size(2 * 1024 * 1024)


class TestFilters:
    """模板过滤器测试"""

    def test_time_ago(self):
        """测试相对时间过滤器"""
        from app.utils.filters import time_ago
        from datetime import datetime, timedelta

        # 测试刚刚
        now = datetime.utcnow()
        assert '刚刚' in time_ago(now)

        # 测试分钟前
        minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        assert '分钟' in time_ago(minutes_ago)

        # 测试小时前
        hours_ago = datetime.utcnow() - timedelta(hours=3)
        assert '小时' in time_ago(hours_ago)

        # 测试天前
        days_ago = datetime.utcnow() - timedelta(days=10)
        assert '天' in time_ago(days_ago)

    def test_domain_from_url(self):
        """测试从URL提取域名"""
        from app.utils.filters import domain_from_url

        assert domain_from_url('https://example.com/page') == 'example.com'
        assert domain_from_url('http://test.com') == 'test.com'
        assert domain_from_url('') == ''
