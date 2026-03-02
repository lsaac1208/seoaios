"""
SEO AIOS 集成测试
Integration Tests
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Site, Article, Page, Keyword, Task


class TestUserFlow:
    """用户流程测试"""

    def test_full_user_flow(self, app):
        """测试完整用户流程"""
        with app.app_context():
            # 1. 创建用户
            user = User(username='flowtest', email='flow@test.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

            assert user.id is not None

            # 2. 验证密码
            assert user.check_password('password123')

            # 3. 创建站点
            site = Site(
                user_id=user.id,
                name='Flow Test Site',
                domain='https://flowtest.com',
                description='Test site for flow'
            )
            db.session.add(site)
            db.session.commit()

            assert site.id is not None

            # 4. 创建页面
            page = Page(
                site_id=site.id,
                title='Home',
                slug='',
                page_type='home',
                status='published'
            )
            db.session.add(page)
            db.session.commit()

            assert page.id is not None

            # 5. 创建文章
            article = Article(
                site_id=site.id,
                user_id=user.id,
                title='Test Article',
                slug='test-article',
                content='This is test content for the article.',
                status='published'
            )
            db.session.add(article)
            db.session.commit()

            assert article.id is not None

            # 6. 创建关键词
            keyword = Keyword(
                user_id=user.id,
                site_id=site.id,
                keyword='testing',
                search_volume=1000
            )
            db.session.add(keyword)
            db.session.commit()

            assert keyword.id is not None

            # 7. 创建任务
            task = Task(
                user_id=user.id,
                site_id=site.id,
                name='Test Task',
                task_type='crawl',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()

            assert task.id is not None


class TestSiteWorkflow:
    """站点工作流测试"""

    def test_site_with_pages(self, app):
        """测试站点与页面关联"""
        with app.app_context():
            user = User(username='siteflow', email='siteflow@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            # 创建站点
            site = Site(
                user_id=user.id,
                name='Site Flow Test',
                domain='https://siteflow.com'
            )
            db.session.add(site)
            db.session.commit()

            # 创建多个页面
            pages_data = [
                {'title': 'Home', 'slug': '', 'page_type': 'home'},
                {'title': 'About', 'slug': 'about', 'page_type': 'about'},
                {'title': 'Contact', 'slug': 'contact', 'page_type': 'contact'}
            ]

            for i, page_data in enumerate(pages_data):
                page = Page(
                    site_id=site.id,
                    title=page_data['title'],
                    slug=page_data['slug'],
                    page_type=page_data['page_type'],
                    status='published',
                    order=i
                )
                db.session.add(page)

            db.session.commit()

            # 验证
            pages = Page.query.filter_by(site_id=site.id).all()
            assert len(pages) == 3


class TestArticleWorkflow:
    """文章工作流测试"""

    def test_article_publishing_flow(self, app):
        """测试文章发布流程"""
        with app.app_context():
            # 创建用户和站点
            user = User(username='articleflow', email='articleflow@test.com')
            user.set_password('password')
            db.session.add(user)

            site = Site(
                user_id=user.id,
                name='Article Flow Site',
                domain='https://articleflow.com'
            )
            db.session.add(site)
            db.session.commit()

            # 创建草稿文章
            article = Article(
                site_id=site.id,
                user_id=user.id,
                title='Draft Article',
                slug='draft-article',
                content='Draft content here',
                status='draft'
            )
            db.session.add(article)
            db.session.commit()

            # 验证草稿状态
            assert article.status == 'draft'
            assert article.published_at is None

            # 发布文章
            article.status = 'published'
            from datetime import datetime
            article.published_at = datetime.utcnow()
            db.session.commit()

            # 验证发布状态
            assert article.status == 'published'
            assert article.published_at is not None

    def test_article_seo_flow(self, app):
        """测试文章SEO流程"""
        with app.app_context():
            user = User(username='seoflow', email='seoflow@test.com')
            user.set_password('password')
            db.session.add(user)

            site = Site(user_id=user.id, name='SEO Flow', domain='https://seoflow.com')
            db.session.add(site)
            db.session.commit()

            # 创建带SEO信息的文章
            article = Article(
                site_id=site.id,
                user_id=user.id,
                title='SEO Test Article',
                slug='seo-test',
                content='<h1>Main Title</h1><p>Content about SEO.</p>',
                meta_title='SEO Test Title',
                meta_description='This is SEO test article description',
                meta_keywords='seo, test, optimization',
                status='published'
            )
            db.session.add(article)
            db.session.commit()

            # 验证SEO字段
            assert article.meta_title is not None
            assert article.meta_description is not None
            assert 'seo' in article.meta_keywords


class TestTaskWorkflow:
    """任务工作流测试"""

    def test_task_lifecycle(self, app):
        """测试任务生命周期"""
        with app.app_context():
            user = User(username='taskflow', email='taskflow@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            # 创建任务
            task = Task(
                user_id=user.id,
                name='Test Crawl Task',
                task_type='crawl',
                status='pending',
                config={'url': 'https://example.com', 'max_depth': 2}
            )
            db.session.add(task)
            db.session.commit()

            task_id = task.id

            # 验证初始状态
            assert task.status == 'pending'
            assert task.started_at is None
            assert task.completed_at is None

            # 开始执行
            task.status = 'running'
            from datetime import datetime
            task.started_at = datetime.utcnow()
            db.session.commit()

            # 模拟执行
            task.progress = 50
            task.message = 'Crawling...'
            db.session.commit()

            assert task.status == 'running'
            assert task.progress == 50

            # 完成
            task.status = 'completed'
            task.progress = 100
            task.completed_at = datetime.utcnow()
            task.result = '{"pages": 10, "status": "success"}'
            db.session.commit()

            assert task.status == 'completed'
            assert task.completed_at is not None


class TestKeywordTracking:
    """关键词追踪测试"""

    def test_keyword_ranking_change(self, app):
        """测试关键词排名变化"""
        with app.app_context():
            user = User(username='ranktest', email='ranktest@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            # 创建关键词
            keyword = Keyword(
                user_id=user.id,
                keyword='python tutorial',
                current_rank=10,
                previous_rank=15
            )
            keyword.rank_changed = keyword.current_rank - keyword.previous_rank  # 5
            db.session.add(keyword)
            db.session.commit()

            # 验证排名变化
            assert keyword.rank_changed == 5
            assert keyword.rank_changed > 0  # 排名提升


class TestDataIntegrity:
    """数据完整性测试"""

    def test_cascade_delete(self, app):
        """测试级联删除"""
        with app.app_context():
            # 创建用户
            user = User(username='deletetest', email='deletetest@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            user_id = user.id

            # 创建站点
            site = Site(
                user_id=user_id,
                name='Delete Test Site',
                domain='https://deletetest.com'
            )
            db.session.add(site)
            db.session.commit()

            site_id = site.id

            # 创建文章
            article = Article(
                site_id=site_id,
                user_id=user_id,
                title='Test Article',
                slug='test-delete',
                content='Test content'
            )
            db.session.add(article)
            db.session.commit()

            article_id = article.id

            # 删除站点
            db.session.delete(site)
            db.session.commit()

            # 验证文章也被删除
            assert Article.query.get(article_id) is None

            # 删除用户
            db.session.delete(user)
            db.session.commit()

            # 验证用户已被删除
            assert User.query.get(user_id) is None
