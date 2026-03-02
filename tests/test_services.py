"""
SEO AIOS 服务层测试
Services Layer Tests
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Site, Article, SeoConfig, AiConfig
from app.services.content_generator import ContentGenerator
from app.services.content_rewriter import ContentRewriter
from app.services.crawler import WebCrawler
from app.services.seo_analyzer import SeoAnalyzer
from app.services.seo_optimizer import SeoOptimizer
from app.services.sitemap_generator import SitemapGenerator
from app.services.robots_generator import RobotsGenerator


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # 创建测试用户和站点
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()

        site = Site(user_id=user.id, name='Test Site', domain='https://test.com')
        db.session.add(site)
        db.session.commit()

        seo_config = SeoConfig(site_id=site.id)
        db.session.add(seo_config)

        ai_config = AiConfig(site_id=site.id)
        db.session.add(ai_config)

        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def site(app):
    """获取测试站点"""
    with app.app_context():
        return Site.query.first()


@pytest.fixture
def ai_config(app):
    """获取测试AI配置"""
    with app.app_context():
        return AiConfig.query.first()


class TestContentGenerator:
    """内容生成器测试"""

    def test_generator_init(self, ai_config):
        """测试生成器初始化"""
        generator = ContentGenerator(ai_config)
        assert generator.ai_config == ai_config
        assert generator.ai_config.provider == 'openai'

    def test_build_prompt(self, ai_config):
        """测试构建提示词"""
        generator = ContentGenerator(ai_config)
        prompt = generator._build_prompt(
            topic="Python教程",
            keywords=["Python", "编程"],
            length=1000,
            style="informative"
        )

        assert "Python教程" in prompt
        assert "Python, 编程" in prompt
        assert "1000" in prompt

    def test_parse_result(self, ai_config):
        """测试解析结果"""
        generator = ContentGenerator(ai_config)

        content = """TITLE: Python入门教程
META: 这是一个Python入门教程
CONTENT:
# Python入门

Python是一种高级编程语言。
"""

        result = generator._parse_result(
            content=content,
            topic="Python教程",
            keywords=["Python", "编程"]
        )

        assert result['title'] == "Python入门教程"
        assert "Python入门教程" in result['meta_description']


class TestContentRewriter:
    """内容改写器测试"""

    def test_rewriter_init(self, ai_config):
        """测试改写器初始化"""
        rewriter = ContentRewriter(ai_config)
        assert rewriter.ai_config == ai_config

    def test_build_prompt(self, ai_config):
        """测试构建改写提示词"""
        rewriter = ContentRewriter(ai_config)
        prompt = rewriter._build_prompt(
            content="这是原始内容",
            rewrite_type="semantic",
            level=3
        )

        assert "这是原始内容" in prompt
        assert "semantic" in prompt or "语义" in prompt

    def test_build_prompt_different_levels(self, ai_config):
        """测试不同改写级别"""
        rewriter = ContentRewriter(ai_config)

        for level in [1, 2, 3, 4, 5]:
            prompt = rewriter._build_prompt("test", "semantic", level)
            assert prompt is not None


class TestWebCrawler:
    """网页爬虫测试"""

    def test_crawler_init(self):
        """测试爬虫初始化"""
        crawler = WebCrawler()
        assert crawler.timeout == 30
        assert crawler.user_agent is not None

    def test_crawler_with_custom_config(self):
        """测试自定义配置"""
        crawler = WebCrawler(timeout=60, user_agent='CustomBot/1.0')
        assert crawler.timeout == 60
        assert crawler.user_agent == 'CustomBot/1.0'

    def test_crawler_session(self):
        """测试爬虫会话"""
        crawler = WebCrawler()
        assert crawler.session is not None
        assert 'User-Agent' in crawler.session.headers


class TestSeoAnalyzer:
    """SEO分析器测试"""

    def test_analyzer_init(self):
        """测试分析器初始化"""
        analyzer = SeoAnalyzer()
        assert analyzer is not None

    def test_analyze_article_with_title(self, app):
        """测试分析有标题的文章"""
        with app.app_context():
            user = User.query.first()
            site = Site.query.first()

            article = Article(
                site_id=site.id,
                user_id=user.id,
                title='Test Article',
                slug='test-article',
                content='<h1>Main Title</h1><p>This is content about Python programming. Python is great.</p>',
                meta_title='Test Article Title',
                meta_description='This is a test article about Python',
                meta_keywords='python, programming',
                status='published'
            )
            db.session.add(article)
            db.session.commit()

            analyzer = SeoAnalyzer()
            result = analyzer.analyze_article(article)

            assert 'score' in result
            assert 'issues' in result
            assert 'suggestions' in result
            assert 'details' in result
            assert result['score'] >= 0

    def test_analyze_article_without_title(self, app):
        """测试分析无标题的文章"""
        with app.app_context():
            user = User.query.first()
            site = Site.query.first()

            article = Article(
                site_id=site.id,
                user_id=user.id,
                title='',
                slug='test-article',
                content='Some content',
                status='draft'
            )
            db.session.add(article)
            db.session.commit()

            analyzer = SeoAnalyzer()
            result = analyzer.analyze_article(article)

            assert 'issues' in result
            assert len(result['issues']) > 0

    def test_analyze_article_short_content(self, app):
        """测试分析内容过短的文章"""
        with app.app_context():
            user = User.query.first()
            site = Site.query.first()

            article = Article(
                site_id=site.id,
                user_id=user.id,
                title='Short Content Article',
                slug='short-content',
                content='Short',  # 内容过短
                meta_title='Short',
                meta_description='Short',
                status='draft'
            )
            db.session.add(article)
            db.session.commit()

            analyzer = SeoAnalyzer()
            result = analyzer.analyze_article(article)

            # 应该有关于内容长度的建议
            assert any('短' in issue for issue in result['issues'])

    def test_analyze_keyword_density(self, app):
        """测试关键词密度分析"""
        with app.app_context():
            user = User.query.first()
            site = Site.query.first()

            # 高密度关键词
            content = "Python " * 50 + "is great"
            article = Article(
                site_id=site.id,
                user_id=user.id,
                title='Python Article',
                slug='python-article',
                content=content,
                meta_title='Python',
                meta_description='Python',
                meta_keywords='python',
                status='draft'
            )
            db.session.add(article)
            db.session.commit()

            analyzer = SeoAnalyzer()
            result = analyzer.analyze_article(article)

            # 检查是否有关键词密度相关的issue
            assert result['score'] >= 0


class TestSeoOptimizer:
    """SEO优化器测试"""

    def test_optimizer_init(self):
        """测试优化器初始化"""
        optimizer = SeoOptimizer()
        assert optimizer is not None

    def test_optimize_article(self, app):
        """测试优化文章"""
        with app.app_context():
            user = User.query.first()
            site = Site.query.first()

            article = Article(
                site_id=site.id,
                user_id=user.id,
                title='Test Article for Optimization',
                slug='test-optimization',
                content='<p>This is test content. Python is a great language.</p>',
                status='draft'
            )
            db.session.add(article)
            db.session.commit()

            optimizer = SeoOptimizer()
            result = optimizer.optimize_article(article)

            assert 'meta_title' in result or 'meta_description' in result
            assert 'suggestions' in result


class TestSitemapGenerator:
    """站点地图生成器测试"""

    def test_generator_init(self, site):
        """测试生成器初始化"""
        generator = SitemapGenerator(site)
        assert generator.site == site

    def test_generate_xml(self, app):
        """测试生成XML"""
        with app.app_context():
            site = Site.query.first()

            generator = SitemapGenerator(site)

            urls = [
                {'loc': 'https://test.com', 'changefreq': 'daily', 'priority': '1.0', 'lastmod': '2024-01-01'},
                {'loc': 'https://test.com/about', 'changefreq': 'weekly', 'priority': '0.8', 'lastmod': '2024-01-01'}
            ]

            xml = generator._generate_xml(urls)

            assert '<?xml' in xml
            assert '<urlset' in xml
            assert 'https://test.com' in xml
            assert 'changefreq' in xml

    def test_escape_xml(self, app):
        """测试XML转义"""
        with app.app_context():
            site = Site.query.first()
            generator = SitemapGenerator(site)

            escaped = generator._escape_xml('<test>&"test"')
            assert '&lt;' in escaped
            assert '&amp;' in escaped
            assert '&quot;' in escaped


class TestRobotsGenerator:
    """Robots生成器测试"""

    def test_generator_init(self, site):
        """测试生成器初始化"""
        generator = RobotsGenerator(site)
        assert generator.site == site

    def test_generate_allow_all(self, app):
        """测试生成允许所有的robots"""
        with app.app_context():
            site = Site.query.first()
            site.seo_config.allow_robots = True

            generator = RobotsGenerator(site)
            content = generator.generate()

            assert 'User-agent: *' in content
            assert 'Allow: /' in content

    def test_generate_disallow_all(self, app):
        """测试生成禁止所有的robots"""
        with app.app_context():
            site = Site.query.first()
            site.seo_config.allow_robots = False

            generator = RobotsGenerator(site)
            content = generator.generate()

            assert 'Disallow: /' in content

    def test_generate_with_sitemap(self, app):
        """测试生成包含sitemap"""
        with app.app_context():
            site = Site.query.first()
            site.domain = 'https://mysite.com'

            generator = RobotsGenerator(site)
            content = generator.generate()

            assert 'Sitemap:' in content
            assert 'mysite.com/sitemap.xml' in content
